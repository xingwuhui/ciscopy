# -*- coding: utf-8 -*-
"""
This purpose of this module is to provide network related methods and
attributes associated with retrieving, storing, and processing OB
Configuration Management Database (CMDB) Configuration Item (CI)
elements.
"""

import socket


class CiscoPyNetwork(object):
    def __init__(self, ipaddress, timeout=5, port_num=22):
        self.ipaddress = ipaddress
        self.timeout = timeout
        self.port_num = port_num

    @property
    def reachable(self):
        result = False
        try:
            skt = socket.socket()
            skt.settimeout(self.timeout)
            skt.connect((self.ipaddress, self.port_num))
            skt.shutdown(socket.SHUT_RD)
            result = True
        except (socket.error or socket.herror or socket.gaierror or
                socket.timeout):
            pass
        
        return result
    
    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.__dict__)
