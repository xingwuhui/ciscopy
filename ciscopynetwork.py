# -*- coding: utf-8 -*-
"""
This purpose of this module is to provide network related methods and
attributes associated with retrieving, storing, and processing network
device data.
"""

import socket
import paramiko


class CiscoPyNetwork:
    def __init__(self, host: str, port_number: int = 22, timeout: float = 5.0):
        self.host = host
        self.port_number = port_number
        self.timeout = timeout
        self.status: bool = False
        self.reachable: bool = self.return_reachable()
    
    def return_reachable(self) -> bool:
        """
        Test whether there is network reachability to the host on the ssh port
        22.
        
        Due to constraints in `ping` and `udp`, this method uses `tcp` port 22
        to determine network reachability.
        :return bool:       (Truse/False)
        """
        try:
            skt = socket.socket()

            skt.settimeout(self.timeout)
            skt.connect((self.host, self.port_number))
            skt.shutdown(socket.SHUT_RD)
            skt.close()
            
            self.status = True
            
            return True
        except socket.error:
            return False

    @staticmethod
    def return_sshclient(host_ip, ssh_username, ssh_password):
        sshclient = paramiko.SSHClient()
        
        sshclient.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())
        
        try:
            sshclient.connect(hostname=host_ip,
                              username=ssh_username,
                              password=ssh_password,
                              allow_agent=False,
                              look_for_keys=False,
                              auth_timeout=5.0)
            return sshclient
        except paramiko.BadHostKeyException:
            # TODO: add code here to propertly handle the excetion
            raise
        except paramiko.AuthenticationException:
            # TODO: add code here to propertly handle the excetion
            raise
        except paramiko.SSHException:
            # TODO: add code here to propertly handle the excetion
            raise
        except socket.error:
            # TODO: add code here to propertly handle the excetion
            raise
    
    def __repr__(self):
        return '{}'.format(self.__dict__)
