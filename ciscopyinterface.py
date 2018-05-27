# -*- coding: utf-8 -*-
"""This purpose of this module is to provide ipaddress related methods
and attributes associated with retrieving and processing OB
Configuration Management Database (CMDB) Configuration Item (CI)
elements.

The class CiscoIPv4Interface defined in this module inherits the
ipaddress.IPv4Interface class.
"""

import netaddr


class CiscoPyInterface(object):
    def __init__(self, if_name, **kwargs):
        """

        :param if_name:         Interface name (or designation)
        :param bandwidth:       Interface bandwidth as a string
        :param ipv4network:     Interface ip_address/subnet_mask as a string.
                                The value of subnet_mask may be dotted
                                notation or CIDR notation.
        :param description:     Interface description
        :param ip_redirects:    True/False
        :param ip_unreachables: True/False
        :param ip_proxyarp:     True/False
        """
        self.name = if_name
        self.description = kwargs.get('description', '')
        if kwargs.get('ipaddr_netmask') is not None:
            self.ipv4network = netaddr.IPNetwork(kwargs.get('ipaddr_netmask'))

    def mgtip_is_natted(self, l):
        """
        This method checks whether the OB TAC Management IP
        address is natted. This method depends on the method named
        ipadentaddr_to_ipaddress to set the attribute named dev_ips.

        The attribute dev_ips is a list of class IPv4Address ip
        addresses.
        """

        self.ipadentaddr_to_ipaddress(l)
          
        if len(self.dev_ips) != 0:
            if isinstance(self.dev_ips, list):
                if all(isinstance(v, IPv4Address) for v in self.dev_ips):
                    if self.ip in self.dev_ips:
                        self.mgtip_is_natted = False
                    else:
                        self.mgtip_is_natted = True
