# -*- coding: utf-8 -*-
"""This purpose of this module is to provide ipaddress related methods
and attributes associated with retrieving and processing interfaces on
Cisco devices.
"""

import ipaddress
import re


class CiscoPyInterfaces(list):
    pass


class CiscoPyIPv4Interface(ipaddress.IPv4Interface):
    def __init__(self, if_name, ipv4, **kwargs):
        """
        :param if_name:         interface name (or designation) as a string
        :param ipv4:            ipv4_address/ipv4_subnetmask as a string
        :param bandwidth:       interface bandwidth as a string
        :param description:     interface description as a string
        :param ip_redirects:    True/False
        :param ip_unreachables: True/False
        :param ip_proxyarp:     True/False
        """

        if '/' not in ipv4:
            raise ValueError('parameter ipv4 not in correct format')

        ip_regex = re.compile(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')
        if ip_regex.match(ipv4.split('/')[0]) is None:
            raise ValueError('the ip address of paramter ipv4 is not in dotted '
                             'notation.')

        if ip_regex.match(ipv4.split('/')[-1]) is None:
            raise ValueError('the subnet mask of paramter ipv4 is not in '
                             'dotted notation.')

        super(CiscoPyIPv4Interface, self).__init__(ipv4)

        self.interface_name = if_name

        if 'bandwidth' not in kwargs.keys():
            self.bandwidth = -1
        else:
            if not isinstance(kwargs.get('bandwidth'), int):
                raise TypeError('bandwidth parameter not type int')
            else:
                self.bandwidth = kwargs.get('bandwidth')

        if 'description' not in kwargs.keys():
            self.description = ''
        else:
            if not isinstance(kwargs.get('description'), str):
                raise TypeError('description parameter not type str')
            else:
                self.description = kwargs.get('description')

        if 'ip_redirects' not in kwargs.keys():
            self.ip_redirects = False
        else:
            if not isinstance(kwargs.get('ip_redirects'), bool):
                raise TypeError('ip_redirects parameter not type bool')
            else:
                self.ip_redirects = kwargs.get('ip_redirects')

        if 'ip_unreachables' not in kwargs.keys():
            self.ip_unreachables = False
        else:
            if not isinstance(kwargs.get('ip_unreacables'), bool):
                raise TypeError('ip_unreachables parameter not type bool')
            else:
                self.ip_redirects = kwargs.get('ip_unreachables')

        if 'ip_proxyarp' not in kwargs.keys():
            self.ip_proxyarp = False
        else:
            if not isinstance(kwargs.get('ip_proxyarp'), bool):
                raise TypeError('ip_proxyarp parameter not type bool')
            else:
                self.ip_redirects = kwargs.get('ip_proxyarp')

