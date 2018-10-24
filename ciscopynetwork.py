# -*- coding: utf-8 -*-
"""
This purpose of this module is to provide network related methods and
attributes associated with retrieving, storing, and processing OB
Configuration Management Database (CMDB) Configuration Item (CI)
elements.
"""

import socket


class CiscoPyNetwork(object):
    def __init__(self, host, timeout=5, port_num=22):
        self.host = host
        self.timeout = timeout
        self.port_num = port_num

    def reachable(self):
        """
        Test whether there is network reachability to the host.

        :return:    `bool` (Truse/False)
        """
        try:
            skt = socket.socket()

            skt.settimeout(self.timeout)
            skt.connect((self.host, self.port_num))
            skt.shutdown(socket.SHUT_RD)
            skt.close()

            return True
        except (socket.error or socket.herror or socket.gaierror or
                socket.timeout):
            return False

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.__dict__)
