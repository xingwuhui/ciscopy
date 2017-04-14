# -*- coding: utf-8 -*-
'''
This purpose of this module is to provide network related methods and
attributes associated with retrieving, storing, and processing OB
Configuration Management Database (CMDB) Configuration Item (CI)
elements.
'''
from pyping import ping as pping

class CiscoNetwork(object):
    def __init__(self, ipaddress, timeout=3000, count=2, packet_size=55):
        self.ipaddress = ipaddress
        self.timeout = timeout
        self.count = count
        self.packet_size = packet_size

    @property
    def reachable(self):
        result = False
        try:
            pping_result = pping(self.ipaddress,
                                 timeout=self.timeout,
                                 count=self.count,
                                 packet_size=self.packet_size)
            if pping_result.ret_code == 0:
                result = True
        except:
            pass
        
        return result
    
    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.__dict__)
