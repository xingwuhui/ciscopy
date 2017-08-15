# -*- coding: utf-8 -*-
'''
The purpose of this module is to provide the SNMPv2 methods and
attributes that enable the retrieval of SNMPv2 OIDs from Cisco IOS type
devices.

The class CiscoSNMP defined in this module inherits the
easysnmp.session.Session class.

The Cisco IOS type devices MUST support the following MIBs:
    *   SNMPv2-MIB
    *   RFC1213-MIB
    *   IF-MIB
    *   ENTITY-MIB
'''

import easysnmp

class CiscoPySNMP(easysnmp.session.Session):
    def __init__(self, hostname, snmp_community):
        super().__init__(hostname=hostname, community=snmp_community,
                         version=2, timeout=3, retries=2,
                         use_sprint_value=True)

    @property
    def walk_entlogicaltype(self):
        '''snmp walk .1.3.6.1.2.1.47.1.2.1.1.3
        .1.3.6.1.2.1.47.1.2.1.1.3 = ENTITY-MIB::entLogicalType'''
        try:
            return self.walk('.1.3.6.1.2.1.47.1.2.1.1.3')
        except:
            return None
    
    @property
    def get_sysname(self):
        '''snmp get .1.3.6.1.2.1.1.5
        .1.3.6.1.2.1.1.5 = SNMPv2-MIB::sysName.0'''
        
        try:
            return self.get(('.1.3.6.1.2.1.1.5', '0'))
        except:
            return None
    
    @property
    def walk_ipadentifindex(self):
        '''snmp walk .1.3.6.1.2.1.4.20.1.2
        .1.3.6.1.2.1.4.20.1.2 = RFC1213-MIB::ipAdEntIfIndex)'''
        try:
            return self.walk('.1.3.6.1.2.1.4.20.1.2')
        except:
            return None
    
    @property
    def walk_ipadentaddr(self):
        '''snmp walk .1.3.6.1.2.1.4.20.1.1
        .1.3.6.1.2.1.4.20.1.1 = RFC1213-MIB::ipAdEntAddr'''
        try:
            return self.walk('.1.3.6.1.2.1.4.20.1.1')
        except:
            return None
    
    @property
    def walk_ipadentnetmask(self):
        '''snmp walk .1.3.6.1.2.1.4.20.1.3
        .1.3.6.1.2.1.4.20.1.3 = RFC1213-MIB::ipAdEntNetMask
        '''
        try:
            return self.walk('.1.3.6.1.2.1.4.20.1.3')
        except:
            return None
    
    @property
    def walk_ifalias(self):
        '''snmp walk .1.3.6.1.2.1.31.1.1.1.18
        .1.3.6.1.2.1.31.1.1.1.18 = IF-MIB::ifAlias'''
        try:
            return self.walk('.1.3.6.1.2.1.31.1.1.1.18')
        except:
            return None
    
    @property
    def walk_ifname(self):
        '''snmp walk .1.3.6.1.2.1.31.1.1.1.1
        .1.3.6.1.2.1.31.1.1.1.1 = IF-MIB::ifName'''
        try:
            return self.walk('.1.3.6.1.2.1.31.1.1.1.1')
        except:
            return None
    
    @property
    def walk_ifdescr(self):
        '''snmp walk .1.3.6.1.2.1.2.2.1.2
        .1.3.6.1.2.1.2.2.1.2 = IF-MIB::ifDescr'''
        try:
            return self.walk('.1.3.6.1.2.1.2.2.1.2')
        except:
            return None
    
    @property
    def walk_entphysicalmfgname(self):
        '''snmp walk .1.3.6.1.2.1.47.1.1.1.1.12
        .1.3.6.1.2.1.47.1.1.1.1.12 = ENTITY-MIB::entPhysicalMfgName)'''
        try:
            return self.walk('.1.3.6.1.2.1.47.1.1.1.1.12')
        except:
            return None
    
    @property
    def walk_entphysicalserialnum(self):
        '''snmp walk .1.3.6.1.2.1.47.1.1.1.1.11
        .1.3.6.1.2.1.47.1.1.1.1.11 = ENTITY-MIB::entPhysicalSerialNum)'''
        try:
            return self.walk('.1.3.6.1.2.1.47.1.1.1.1.11')
        except:
            return None
    
    @property
    def walk_entphysicalmodelname(self):
        '''snmp walk .1.3.6.1.2.1.47.1.1.1.1.13
        .1.3.6.1.2.1.47.1.1.1.1.13 = ENTITY-MIB::entPhysicalModelName'''
        try:
            return self.walk('.1.3.6.1.2.1.47.1.1.1.1.13')
        except:
            return None
        
    @property
    def get_cmdb_data(self):
        '''Use the individual get and walk methods to define the
        attributes that will store the retrieved data.'''
        self.entLogicalType = self.walk_entlogicaltype
        self.sysName = self.get_sysname
        self.ipAdEntIfIndex = self.walk_ipadentifindex
        self.ipAdEntAddr = self.walk_ipadentaddr
        self.ipAdEntNetMask = self.walk_ipadentnetmask
        self.ifAlias = self.walk_ifalias
        self.ifName = self.walk_ifname
        self.ifDescr = self.walk_ifdescr
        self.entPhysicalMfgName = self.walk_entphysicalmfgname
        self.entPhysicalSerialNum = self.walk_entphysicalserialnum
        self.entPhysicalModelName = self.walk_entphysicalmodelname

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.__dict__)
