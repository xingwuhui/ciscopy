# -*- coding: utf-8 -*-
"""

This purpose of this module is to provide interface related classes, methods,
and attributes for Cisco device interfaces based on appropriate SNMP OIDs;
such as ifMIB; ipMIB; CISCO-STACK-MIB; CISCO-L2L3-INTERFACE-CONFIG-MIB, etc.
"""

import ipaddress
import re


class MissingParameterError(ValueError):
    pass


class CiscoPyInterfaces(list):
    def __repr__(self):
        repr_asstring = '<{}([{}])>'
        if self:
            return repr_asstring.format(self.__class__.__name__, ', '.join(map(str, self)))
        else:
            repr_asstring = '<{}([{}])>'
            return repr_asstring.format(self.__class__.__name__, '')


class CiscoPyInterface(object):
    def __init__(self, **kwargs):
        if 'name' not in kwargs.keys():
            raise MissingParameterError('Keyword parameter `name` missing.')
        
        if 'oid_index' not in kwargs.keys():
            raise MissingParameterError('Keyword parameter `oid_index` missing.')

        self.name: str = kwargs['name']
        self.oid_index: str = kwargs.get('oid_index', None)
        self.short_name: str = ''
        self.obtac_short_name = ''
        self.description: str = ''
        self.speed: str = ''
        self.admin_status: str = 'down'
        self.operational_status: str = 'down'
        self.physical_address: str = ''
        self.trunking: bool = False
        self.ip_address: ipaddress.IPv4Interface = ipaddress.IPv4Interface('0.0.0.0')
    
    def __repr__(self):
        repr_string = '<{}(name={}, ' \
                      'oid_index={}, ' \
                      'short_name={}, ' \
                      'description={}, ' \
                      'speed={}, ' \
                      'admin_status={}, ' \
                      'operational_status={}, ' \
                      'physical_address={}, ' \
                      'trunking={}, ' \
                      'ip_address={})>'
        return repr_string.format(self.__class__.__name__,
                                  self.name,
                                  self.oid_index,
                                  self.short_name,
                                  self.description,
                                  self.speed,
                                  self.admin_status,
                                  self.operational_status,
                                  self.physical_address,
                                  self.trunking,
                                  self.ip_address)
        

class CiscoPySwitchPhysicalInterface(CiscoPyInterface):
    def __init__(self, **kwargs):
        """

        :param interface_name:      The Switch Physical Interface name; type str
        :param mode:                The switchport mode; type str
        :param access_vlan:         The switchport access vlan; type int
        :param voice_vlan:          The switchport voice vlan; type int
        :param trunk_native_vlan:   The switchport trunk native vlan; type int
        :param trunk_allowed_vlan:  The switchport trunk allowed vlans;
                                    type list
        """
        super(CiscoPySwitchPhysicalInterface, self).__init__(**kwargs)
        self.mode = None
        self.access_vlan = 1
        self.voice_vlan = None
        self.trunk_native_vlan = 1
        self.trunk_allowed_vlan = []
        self.spanningtree_portfast = False
        self.spanningtree_bpduguard = False


class CiscoPySwitchVirtualInterface(CiscoPyInterface):
    def __init__(self, **kwargs):
        """

        :param interface_name:  The Switch Logical Interface name; type str
        :param ip_redirects:    True/False; type bool
        :param ip_unreachables: True/False; type bool
        :param ip_proxyarp:     True/False; type bool
        """
        super(CiscoPySwitchVirtualInterface, self).__init__(**kwargs)

        if ('ip_redirects' in kwargs.keys() and
                not isinstance(kwargs['ip_redirects'], bool)):
            raise TypeError('The ip_redirects parameter is not type bool')
        else:
            self.ip_redirects = kwargs.get('ip_redirects', False)

        if ('ip_unreachables' in kwargs.keys() and
                not isinstance(kwargs['ip_unreachables'], bool)):
            raise TypeError('The ip_unreachables parameter is not type bool')
        else:
            self.ip_redirects = kwargs.get('ip_unreachables', False)

        if ('ip_proxyarp' in kwargs.keys() and
                not isinstance(kwargs['ip_proxyarp'], bool)):
            raise TypeError('The ip_proxyarp parameter is not type bool')
        else:
            self.ip_redirects = kwargs.get('ip_proxyarp', False)


class CiscoPyIPv4Interface(ipaddress.IPv4Interface):
    def __init__(self, if_name, ipv4, **kwargs):
        """
        :param if_name:         type str: interface name (snmp ifDescr)
        :param ipv4:            type str: ipv4_address/ipv4_subnetmask (snmp ipAdEntAddr/ipAdEntNetMask)
        :param bandwidth:       type str: interface bandwidth (snmp ifHighSpeed)
        :param description:     type str: interface description (snmp ifAlias)
        :param ip_redirects:    type bool: True/False
        :param ip_unreachables: type bool: True/False
        :param ip_proxyarp:     type bool: True/False
        """

        if '/' not in ipv4:
            raise ValueError('parameter ipv4 not in correct format')

        ip_regex = re.compile(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')
        if ip_regex.match(ipv4.split('/')[0]) is None:
            raise ValueError('The paramter `ipv4` address value is not in dotted deciaml notation.')

        if ip_regex.match(ipv4.split('/')[-1]) is None:
            raise ValueError('The paramter `ipv4` subnet value is not in dotted decimal notation.')

        super(CiscoPyIPv4Interface, self).__init__(ipv4)

        self.interface_name: str = if_name
        self.bandwidth: str = kwargs.get('bandwidth', '-1')
        self.description: str = kwargs.get('description', '')
        self.ip_redirects: bool = kwargs.get('ip_redirects', True)
        self.ip_unreachables: bool = kwargs.get('ip_unreachables', True)
        self.ip_proxyarp: bool = kwargs.get('ip_proxyarp', True)


class OBTACIPv4Interface(CiscoPyIPv4Interface):
    pass
