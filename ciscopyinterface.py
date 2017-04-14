# -*- coding: utf-8 -*-
'''This purpose of this module is to provide ipaddress related methods
and attributes associated with retrieving and processing OB
Configuration Management Database (CMDB) Configuration Item (CI)
elements.

The class CiscoIPv4Interface defined in this module inherits the
ipaddress.IPv4Interface class.'''

from collections import OrderedDict
from ipaddress import IPv4Address, IPv4Interface
#from easysnmp.variables import SNMPVariable, SNMPVariableList
#from cisco.ciscosnmp import CiscoSNMP

class CiscoPyInterface(OrderedDict):
     def __init__(self):
          self['oid index'] = None
          self['name'] = None
          self['description'] = None
          self['ip address'] = None
          self['circuit id'] = None
          
     def is_mgtip_natted(self, l):
          '''
          This method checks whether the OB TAC Management IP
          address is natted.
          
          This method depends on the method
          named ipadentaddr_to_ipaddress to set the attribute
          named dev_ips.
          
          The attribute dev_ips is a list of class IPv4Address ip
          addresses.
          '''
          self.ipadentaddr_to_ipaddress(l)
          
          if len(self.dev_ips) != 0:
               if isinstance(self.dev_ips, list):
                    if all(isinstance(v, IPv4Address) for v in self.dev_ips):
                         if self.ip in self.dev_ips:
                              self.mgtip_is_natted = False
                         else:
                              self.mgtip_is_natted = True
