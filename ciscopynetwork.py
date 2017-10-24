# -*- coding: utf-8 -*-
'''
This purpose of this module is to provide network related methods and
attributes associated with retrieving, storing, and processing network devices.
'''
#from pyping import ping as pping
from subprocess import run as sp_run, PIPE as sp_PIPE

class CiscoPyNetwork(object):
    def __init__(self,
                 ipaddress,
                 wait_time='3000',
                 count='2',
                 packet_size='55'):
        self.ipaddress = ipaddress
        self.wait_time = wait_time
        self.count = count
        self.packet_size = packet_size

    @property
    def is_reachable(self):
        '''
        Is the network device reachable. Basically a ping test.
        
        The ping command assumes that this method will executed on a
        Linux/Unix type computer.
        '''
        result = False
        ping_cmd = ['ping', '-c', self.count, '-W', self.wait_time, '-s',
                    self.packet_size, self.ipaddress]
        spr_cp = sp_run(ping_cmd, stdout=sp_PIPE,
                        stderr=sp_PIPE)
        
        if spr_cp.returncode == 0:
            result = True

        return result
    
    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.__dict__)
