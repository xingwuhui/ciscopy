# -*- coding: utf-8 -*-
"""This purpose of this module is to provide ipaddress related methods
and attributes associated with retrieving and processing OB
Configuration Management Database (CMDB) Configuration Item (CI)
elements.

The class CiscoIPv4Interface defined in this module inherits the
ipaddress.IPv4Interface class.
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
        self.bandwidth = kwargs.get('bandwidth')
        self.description = kwargs.get('description')

        if not isinstance(kwargs.get('ip_redirects'), bool):
            raise ValueError('ip_redirects parameter is not type bool')
        self.ip_redirects = kwargs.get('ip_redirects', False)

        if not isinstance(kwargs.get('ip_unreachables'), bool):
            raise ValueError('ip_unreachables parameter is not type bool')
        self.ip_unreachables = kwargs.get('ip_unreachables', False)

        if not isinstance(kwargs.get('ip_proxyarp'), bool):
            raise ValueError('ip_proxyarp parameter is not type bool')
        self.ip_proxyarp = kwargs.get('ip_proxyarp', False)

