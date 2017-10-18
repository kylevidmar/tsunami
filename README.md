
Tsunami Module Readme
==============================================

module overview:
----------------------------------------------
Library used for transfering files seamlessly with tsunami-udp protocol from FUL to remote site provided:

*deploy:
      - This deploys the tsunami server container to a CaaS server with ports forwarded
        and mount points also forwarded for /nfs/netboot
      - Upon completion returns the Container ID
      - It offers the file argument passed on the Tsunami server so it can be pulled in the remote site.
      ( e.g tsunami.deploy() )

*clean:
      - This removes the tsunami server container when complete.
      - This also kills the running container
      ( e.g tsunami.clean() )

*ports:
      - Returns info on the port forwarded for tsunami server container id passed
      (e.g tsunami.ports(id))

*copy:
      - Leverages pxe servers in each site via the location prefix
      - pExpects into them and calls tsunami client process to pull file to scratch location
      - Port provided is the forwarded port from tsunami server container
      - Scratch is mounted via HTTP and a link is provided upon completion
      (e.g tsunami.copy(port,location))


==============================================
