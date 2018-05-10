# -*- coding: utf-8 -*-
"""
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
"""

import easysnmp
import ipaddress


class CiscoPySNMP(easysnmp.session.Session):
    def __init__(self, hostname, community):
        super().__init__(hostname=hostname, community=community,
                         version=2, timeout=3, retries=2,
                         use_sprint_value=True)

        self.ifDescr = None
        self.ipAdEntIfIndex = None
        self.entLogicalType = None
        self.sysName = None
        self.ipAdEntAddr = None
        self.ipAdEntNetMask = None
        self.ifAlias = None
        self.ifName = None
        self.entPhysicalMfgName = None
        self.entPhysicalSerialNum = None
        self.entPhysicalModelName = None

    def get_ifindex(self, interface):
        r = ''
        
        if self.ifDescr is None:
            self.ifDescr = self.walk_ifdescr
        
        for v in self.ifDescr:
            voi = v.oid_index
            vv = v.value
            
            if interface == vv.lower():
                r = voi
        
        return r
    
    def get_ifip(self, interface):
        ipv4network = None
        ip_address = None

        if self.ipAdEntIfIndex is None:
            self.ipAdEntIfIndex = self.walk_ipadentifindex
            self.ipAdEntAddr = self.walk_ipadentaddr
            self.ipAdEntNetMask = self.walk_ipadentnetmask
        
        for v in self.ipAdEntIfIndex:
            voi = v.oid_index
            vv = v.value
            
            if vv == self.get_ifindex(interface):
                ip_address = voi

        for ipadentaddr, ipadentnetmask in zip(self.ipAdEntAddr,
                                               self.ipAdEntNetMask):
            if ipadentaddr.oid_index == ip_address:
                ipv4network = '{}/{}'.format(ipadentaddr.oid_index,
                                             ipadentnetmask.value)

        return ipv4network

    @property
    def walk_entlogicaltype(self):
        """snmp walk .1.3.6.1.2.1.47.1.2.1.1.3
        .1.3.6.1.2.1.47.1.2.1.1.3 = ENTITY-MIB::entLogicalType
        """
        try:
            return self.walk('.1.3.6.1.2.1.47.1.2.1.1.3')
        except (easysnmp.exceptions.EasySNMPError,
                easysnmp.exceptions.EasySNMPNoSuchInstanceError,
                easysnmp.exceptions.EasySNMPConnectionError,
                easysnmp.exceptions.EasySNMPNoSuchNameError,
                easysnmp.exceptions.EasySNMPNoSuchObjectError,
                easysnmp.exceptions.EasySNMPTimeoutError,
                easysnmp.exceptions.EasySNMPUndeterminedTypeError,
                easysnmp.exceptions.EasySNMPUnknownObjectIDError):
            return None
    
    @property
    def get_sysname(self):
        """
        snmp get .1.3.6.1.2.1.1.5
        .1.3.6.1.2.1.1.5 = SNMPv2-MIB::sysName
        """
        
        try:
            return self.get(('.1.3.6.1.2.1.1.5', '0'))
        except (easysnmp.exceptions.EasySNMPError,
                easysnmp.exceptions.EasySNMPNoSuchInstanceError,
                easysnmp.exceptions.EasySNMPConnectionError,
                easysnmp.exceptions.EasySNMPNoSuchNameError,
                easysnmp.exceptions.EasySNMPNoSuchObjectError,
                easysnmp.exceptions.EasySNMPTimeoutError,
                easysnmp.exceptions.EasySNMPUndeterminedTypeError,
                easysnmp.exceptions.EasySNMPUnknownObjectIDError):
            return None
    
    @property
    def walk_ipadentifindex(self):
        """
        snmp walk .1.3.6.1.2.1.4.20.1.2
        .1.3.6.1.2.1.4.20.1.2 = RFC1213-MIB::ipAdEntIfIndex)
        """
        try:
            return self.walk('.1.3.6.1.2.1.4.20.1.2')
        except (easysnmp.exceptions.EasySNMPError,
                easysnmp.exceptions.EasySNMPNoSuchInstanceError,
                easysnmp.exceptions.EasySNMPConnectionError,
                easysnmp.exceptions.EasySNMPNoSuchNameError,
                easysnmp.exceptions.EasySNMPNoSuchObjectError,
                easysnmp.exceptions.EasySNMPTimeoutError,
                easysnmp.exceptions.EasySNMPUndeterminedTypeError,
                easysnmp.exceptions.EasySNMPUnknownObjectIDError):
            return None
    
    @property
    def walk_ipadentaddr(self):
        """
        snmp walk .1.3.6.1.2.1.4.20.1.1
        .1.3.6.1.2.1.4.20.1.1 = RFC1213-MIB::ipAdEntAddr
        """

        try:
            return self.walk('.1.3.6.1.2.1.4.20.1.1')
        except (easysnmp.exceptions.EasySNMPError,
                easysnmp.exceptions.EasySNMPNoSuchInstanceError,
                easysnmp.exceptions.EasySNMPConnectionError,
                easysnmp.exceptions.EasySNMPNoSuchNameError,
                easysnmp.exceptions.EasySNMPNoSuchObjectError,
                easysnmp.exceptions.EasySNMPTimeoutError,
                easysnmp.exceptions.EasySNMPUndeterminedTypeError,
                easysnmp.exceptions.EasySNMPUnknownObjectIDError):
            return None
    
    @property
    def walk_ipadentnetmask(self):
        """
        snmp walk .1.3.6.1.2.1.4.20.1.3
        .1.3.6.1.2.1.4.20.1.3 = RFC1213-MIB::ipAdEntNetMask
        """
        try:
            return self.walk('.1.3.6.1.2.1.4.20.1.3')
        except (easysnmp.exceptions.EasySNMPError,
                easysnmp.exceptions.EasySNMPNoSuchInstanceError,
                easysnmp.exceptions.EasySNMPConnectionError,
                easysnmp.exceptions.EasySNMPNoSuchNameError,
                easysnmp.exceptions.EasySNMPNoSuchObjectError,
                easysnmp.exceptions.EasySNMPTimeoutError,
                easysnmp.exceptions.EasySNMPUndeterminedTypeError,
                easysnmp.exceptions.EasySNMPUnknownObjectIDError):
            return None
    
    @property
    def walk_ifalias(self):
        """
        snmp walk .1.3.6.1.2.1.31.1.1.1.18
        .1.3.6.1.2.1.31.1.1.1.18 = IF-MIB::ifAlias
        """

        try:
            return self.walk('.1.3.6.1.2.1.31.1.1.1.18')
        except (easysnmp.exceptions.EasySNMPError,
                easysnmp.exceptions.EasySNMPNoSuchInstanceError,
                easysnmp.exceptions.EasySNMPConnectionError,
                easysnmp.exceptions.EasySNMPNoSuchNameError,
                easysnmp.exceptions.EasySNMPNoSuchObjectError,
                easysnmp.exceptions.EasySNMPTimeoutError,
                easysnmp.exceptions.EasySNMPUndeterminedTypeError,
                easysnmp.exceptions.EasySNMPUnknownObjectIDError):
            return None
    
    @property
    def walk_ifname(self):
        """
        snmp walk .1.3.6.1.2.1.31.1.1.1.1
        .1.3.6.1.2.1.31.1.1.1.1 = IF-MIB::ifName
        """
        try:
            return self.walk('.1.3.6.1.2.1.31.1.1.1.1')
        except (easysnmp.exceptions.EasySNMPError,
                easysnmp.exceptions.EasySNMPNoSuchInstanceError,
                easysnmp.exceptions.EasySNMPConnectionError,
                easysnmp.exceptions.EasySNMPNoSuchNameError,
                easysnmp.exceptions.EasySNMPNoSuchObjectError,
                easysnmp.exceptions.EasySNMPTimeoutError,
                easysnmp.exceptions.EasySNMPUndeterminedTypeError,
                easysnmp.exceptions.EasySNMPUnknownObjectIDError):
            return None
    
    @property
    def walk_ifdescr(self):
        """
        snmp walk .1.3.6.1.2.1.2.2.1.2
        .1.3.6.1.2.1.2.2.1.2 = IF-MIB::ifDescr
        """
        try:
            return self.walk('.1.3.6.1.2.1.2.2.1.2')
        except (easysnmp.exceptions.EasySNMPError,
                easysnmp.exceptions.EasySNMPNoSuchInstanceError,
                easysnmp.exceptions.EasySNMPConnectionError,
                easysnmp.exceptions.EasySNMPNoSuchNameError,
                easysnmp.exceptions.EasySNMPNoSuchObjectError,
                easysnmp.exceptions.EasySNMPTimeoutError,
                easysnmp.exceptions.EasySNMPUndeterminedTypeError,
                easysnmp.exceptions.EasySNMPUnknownObjectIDError):
            return None
    
    @property
    def walk_entphysicalmfgname(self):
        """
        snmp walk .1.3.6.1.2.1.47.1.1.1.1.12
        .1.3.6.1.2.1.47.1.1.1.1.12 = ENTITY-MIB::entPhysicalMfgName)
        """

        try:
            return self.walk('.1.3.6.1.2.1.47.1.1.1.1.12')
        except (easysnmp.exceptions.EasySNMPError,
                easysnmp.exceptions.EasySNMPNoSuchInstanceError,
                easysnmp.exceptions.EasySNMPConnectionError,
                easysnmp.exceptions.EasySNMPNoSuchNameError,
                easysnmp.exceptions.EasySNMPNoSuchObjectError,
                easysnmp.exceptions.EasySNMPTimeoutError,
                easysnmp.exceptions.EasySNMPUndeterminedTypeError,
                easysnmp.exceptions.EasySNMPUnknownObjectIDError):
            return None
    
    @property
    def walk_entphysicalserialnum(self):
        """snmp walk .1.3.6.1.2.1.47.1.1.1.1.11
        .1.3.6.1.2.1.47.1.1.1.1.11 = ENTITY-MIB::entPhysicalSerialNum
        """

        try:
            return self.walk('.1.3.6.1.2.1.47.1.1.1.1.11')
        except (easysnmp.exceptions.EasySNMPError,
                easysnmp.exceptions.EasySNMPNoSuchInstanceError,
                easysnmp.exceptions.EasySNMPConnectionError,
                easysnmp.exceptions.EasySNMPNoSuchNameError,
                easysnmp.exceptions.EasySNMPNoSuchObjectError,
                easysnmp.exceptions.EasySNMPTimeoutError,
                easysnmp.exceptions.EasySNMPUndeterminedTypeError,
                easysnmp.exceptions.EasySNMPUnknownObjectIDError):
            return None
    
    @property
    def walk_entphysicalmodelname(self):
        """snmp walk .1.3.6.1.2.1.47.1.1.1.1.13
        .1.3.6.1.2.1.47.1.1.1.1.13 = ENTITY-MIB::entPhysicalModelName
        """

        try:
            return self.walk('.1.3.6.1.2.1.47.1.1.1.1.13')
        except (easysnmp.exceptions.EasySNMPError,
                easysnmp.exceptions.EasySNMPNoSuchInstanceError,
                easysnmp.exceptions.EasySNMPConnectionError,
                easysnmp.exceptions.EasySNMPNoSuchNameError,
                easysnmp.exceptions.EasySNMPNoSuchObjectError,
                easysnmp.exceptions.EasySNMPTimeoutError,
                easysnmp.exceptions.EasySNMPUndeterminedTypeError,
                easysnmp.exceptions.EasySNMPUnknownObjectIDError):
            return None
        
    @property
    def get_cmdbdata(self):
        """
        Use the individual get and walk methods to define the
        attributes that will store the retrieved data.
        """
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
