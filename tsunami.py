##########################################################
#  
#   Name:   Tsunami
#
#   Purpose:  To create a class that contains functions
#             to support tsunami file transfer leveraging
#             docker and remote storage.
#
#
###########################################################

from docker import Client, errors
from docker import *
from kick.kick_constants import DOCKER_API_MIN_VER
import pexpect
from pexpect import pxssh
import time
import os


class tsunami:
    '''
    This is the base class for Tsunami-udp. Allows you to create a containerized
    version of Tsunami Server with /netboot mounted, 
    You then pull the remote file to the desired destination.

    Initial Arguments:
            * self: is the docker-py connection
    '''  
    def __init__(self):
        '''Tsunami base class __init__ will find available CaaS and connect'''
        #Clear terminal for cleaner logging
        os.system('clear')
        #Find CaaS server with most available resources
        caas_server = find_ful_caas()
        print('LOG: Using Fulton CaaS Server: ' + caas_server)
        docker = caas_server
        self.docker = docker
        #Use CaaS Server in question
        dd_url = "tcp://" + docker + ":2375"
        #Create Docker-py client object and connect
        dockerClient = Client(base_url=dd_url, version=DOCKER_API_MIN_VER)
        self.dockerClient = dockerClient
    
    '''
    ************************************
    Tsunami Server Functions
    ************************************
    '''

    def deploy(self, build_path):
        '''
        Purpose:
                Deploys peihsinsu/tsunami-udp container on Docker client object,
                It then sets up port forwarding and mount forwarding on the container,
                Finally it runs the Tsunami Server offering the build_path argument.
                
        Arguments:
                * self - docker-py connection
                * build_path - path to the file to offer up assuming /nfs/netboot/ root
        
        Returns:
                * Id - container id of tsunami server
        '''
        print('LOG: Tsunami Server started')
        self.build_path = build_path
        self.file = build_path
        #Command to run tsunami server on container
        mycommand = 'tsunamid --port 46224 /tmp/ims/' + build_path
        print('LOG: Offering up ' + build_path)
        #Deploy container and forward ports and volumes
        container_1 = self.dockerClient.create_container(detach='True', ports=[(46224, 'tcp')], volumes=['/tmp'], image='peihsinsu/tsunami-udp', command=mycommand)
        #Start container
        self.dockerClient.start(container_1, port_bindings={'46224/tcp': ('0.0.0.0',)}, binds={'/nfs/netboot':{'bind': '/tmp', 'ro': False}})
        self.container_1 = container_1
        #Return container Id
        return self.container_1['Id']
        
    def clean(self, id):
        '''
        Purpose:
                Deletes container after completion.
                
        Arguments:
                * self - docker-py connection
                * id - container id of tsunami container
        '''
        #Kill running container
        self.dockerClient.kill(id)
        #Delete running container
        self.dockerClient.remove_container(id)
        print('LOG: Deleting Tsunami Server.')
        
    def ports(self, id):
        '''
        Purpose:
                Returns ports forwarded for given container id.
                
        Arguments:
                * self - docker-py connection
                * id - container id of tsunami container
        
        Returns:
                * ports - port of running tsunami container
        '''
        #Find ports via inspect_container call
        info = self.dockerClient.inspect_container(id)
        ports = (info['NetworkSettings']['Ports']['46224/tcp'][0]['HostPort'])
        print('LOG: Finding port Tsunami is running on... ' + ports)
        return ports
      
    '''
    ************************************
    Tsunami Client Functions
    ************************************
    '''
    
    def copy(self, port, location):
        '''
        Purpose:
                Connects via pexpect to remote site provided and initiates the client side
                pull of file via the tsunami server.
                
        Arguments:
                * self - docker-py connection
                * port - port tsunami server is running on
                * location - 3 character location identifier, see below
        '''
        #Start time so transfer time can be provided
        start = time.time()
        print('LOG: Average transfer speed will be about 30-100MB/sec')
        print('LOG: Initating the copy process.  Please wait, this could take a few minutes...')
        #Based on location variable find ip to use for client
        if location == 'SJC':
            ip = 'pxe-sja.cisco.com'
            user = 'pxe'
            password = 'pxe'
        elif location == 'SJA':
            ip = 'pxe-sja.cisco.com'
            user = 'pxe'
            password = 'pxe'
        elif location == 'BGL':
            ip = 'pxe-bgl.cisco.com'
            user = 'pxe'
            password = 'pxe'
        elif location == 'AST':
            ip = 'pxe-ast.cisco.com'
            user = 'pxe'
            password = 'pxe'
        #Start pxssh pexpect session and run tsunami client
        s = pxssh.pxssh(timeout=3000)
        s.login(ip, user, password)
        s.sendline('cd /tftpboot/asa/scratch/kick')
        s.sendline('tsunami')
        s.sendline('connect ' + self.docker + ' ' + port)
        s.sendline('set rate 128M')
        s.sendline('set verbose no')
        s.prompt()
        s.sendline('get *')
        #Wait for transfer complete and end session
        s.expect('Transfer complete*.')
        #Get end time for transfer time
        end = time.time()
        #Do the math
        howlong = (end - start)
        my_file_name = file_name(self.file)
        print('LOG: Copy complete.  Total elapsed time is ' + str(howlong) + ' seconds')
        print('LOG: Copy complete please naviate to http://' + ip + '/scratch/kick/' + my_file_name + ' to pull your file')
        path = 'http://' + ip + 'scratch/kick/' + my_file_name
        #Return http link to file in remote location
        return path

def find_ful_caas():
    '''
        Purpose:
                Finds caas server with most resources.
    '''
    #First check CaaS1
    dd_url = "tcp://kick-ful-caas1:2375"
    dockerClient = Client(base_url=dd_url, version=DOCKER_API_MIN_VER)
    cont_1 = dockerClient.info()
    caas1 = cont_1['ContainersRunning']
    caas1 = int(caas1)
    #Check CaaS2
    dd_url = "tcp://kick-ful-caas2:2375"
    dockerClient = Client(base_url=dd_url, version=DOCKER_API_MIN_VER)
    cont_2 = dockerClient.info()
    caas2 = cont_2['ContainersRunning']
    caas2 = int(caas2)
    #CaaS3
    dd_url = "tcp://kick-ful-caas3:2375"
    dockerClient = Client(base_url=dd_url, version=DOCKER_API_MIN_VER)
    cont_3 = dockerClient.info()
    caas3 = cont_3['ContainersRunning']
    caas3 = int(caas3)
    #CaaS4
    dd_url = "tcp://kick-ful-caas4:2375"
    dockerClient = Client(base_url=dd_url, version=DOCKER_API_MIN_VER)
    cont_4 = dockerClient.info()
    caas4 = cont_4['ContainersRunning']
    caas4 = int(caas4)
    #Compare data and find CaaS with most resources and return it
    dict_caas = {'kick-ful-caas1.cisco.com': caas1, 'kick-ful-caas2.cisco.com': caas2, 'kick-ful-caas3.cisco.com': caas3, 'kick-ful-caas4.cisco.com': caas4}
    dict_caas = sorted(dict_caas, key=dict_caas.get)
    return dict_caas[0]

def file_name(file):
    '''
        Purpose: Returns base file name from file path.
    '''
    new_file = os.path.basename(file)
    return new_file
    
