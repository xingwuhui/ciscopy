# -*- coding: utf-8 -*-
"""
This purpose of this module is to provide network related methods and
attributes associated with retrieving, storing, and processing network
device data.
"""

import socket
import netmiko


class CiscoPyNetwork:
    def __init__(self):
        self.device = {}
        self.sshdetect = None
        self.devicetype = None
        self.sshclient = None
        self.ssh_status = False
        self.ssh_status_cause = None
        self.ssh_cli_prompt = ''
        self.ssh_logout_prompt = ''
    
    @staticmethod
    def reachable(host, port_number=22, timeout=5.0):
        """
        Test whether there is network reachability to the host.

        :return:    `bool` (Truse/False)
        """
        try:
            skt = socket.socket()

            skt.settimeout(timeout)
            skt.connect((host, port_number))
            skt.shutdown(socket.SHUT_RD)
            skt.close()

            return True
        except socket.error:
            return False

    def set_devicetype(self, **kwargs):
        device_type = 'autodetect'
        host = kwargs.get('host')
        username = kwargs.get('username')
        password = kwargs.get('password')
        enable_password = kwargs.get('secret')
        
        try:
            self.sshdetect = netmiko.SSHDetect(device_type=device_type,
                                               host=host,
                                               username=username,
                                               password=password,
                                               secret=enable_password)
            self.devicetype = self.sshdetect.autodetect()

        except netmiko.NetMikoAuthenticationException as exception:
            self.ssh_status_cause = exception
        except netmiko.NetMikoTimeoutException as exception:
            self.ssh_status_cause = exception
    
    def set_sshclient(self, host, username, password, secret=''):
        self.device['host'] = host
        self.device['username'] = username
        self.device['password'] = password
        self.device['secret'] = secret
        
        if not self.devicetype:
            self.set_devicetype(**self.device)
        
        self.device['device_type'] = self.devicetype
        
        try:
            self.sshclient = netmiko.Netmiko(**self.device)
            self.sshclient.prompt = self.sshclient.find_prompt()
            self.ssh_status = True
        except netmiko.NetMikoAuthenticationException as exception:
            self.ssh_status_cause = exception
        except netmiko.NetMikoTimeoutException as exception:
            self.ssh_status_cause = exception
