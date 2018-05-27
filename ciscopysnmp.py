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


class CiscoPySNMP(easysnmp.session.Session):
    def __init__(self,
                 host,
                 community,
                 version=2,
                 timeout=3,
                 retries=2,
                 use_sprint_value=True,
                 **kwargs):
        super().__init__(hostname=host,
                         community=community,
                         version=version,
                         timeout=timeout,
                         retries=retries,
                         use_sprint_value=use_sprint_value,
                         **kwargs)
        self.host = host
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
            self.set_ifdescr()

        if self.ifDescr is None:
            raise ValueError('Unable to snmp walk ifDescr of {}'.format(
                self.host))
        for v in self.ifDescr:
            voi = v.oid_index
            vv = v.value
            
            if interface == vv:
                r = voi
        
        return r
    
    def get_ifip(self, interface):
        ipv4network = None
        ip_address = None

        if self.ipAdEntIfIndex is None:
            self.set_ipadentifindex()
            self.set_ipadentaddr()
            self.set_ipadentnetmask()

        if self.ipAdEntIfIndex is None:
            value_err_msg = 'Unable to snmp walk ipAdEntIfIndex of {}'
            raise ValueError(value_err_msg.format(self.host))
        
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

    def setattr_entlogicaltype(self):
        """snmp walk .1.3.6.1.2.1.47.1.2.1.1.3
        .1.3.6.1.2.1.47.1.2.1.1.3 = ENTITY-MIB::entLogicalType
        """
        try:
            self.entLogicalType = self.walk('.1.3.6.1.2.1.47.1.2.1.1.3')
        except (easysnmp.exceptions.EasySNMPError,
                easysnmp.exceptions.EasySNMPNoSuchInstanceError,
                easysnmp.exceptions.EasySNMPConnectionError,
                easysnmp.exceptions.EasySNMPNoSuchNameError,
                easysnmp.exceptions.EasySNMPNoSuchObjectError,
                easysnmp.exceptions.EasySNMPTimeoutError,
                easysnmp.exceptions.EasySNMPUndeterminedTypeError,
                easysnmp.exceptions.EasySNMPUnknownObjectIDError):
            pass
    
    def setattr_sysname(self):
        """
        snmp get .1.3.6.1.2.1.1.5
        .1.3.6.1.2.1.1.5 = SNMPv2-MIB::sysName
        """
        
        try:
            self.sysName = self.get(('.1.3.6.1.2.1.1.5', '0'))
        except (easysnmp.exceptions.EasySNMPError,
                easysnmp.exceptions.EasySNMPNoSuchInstanceError,
                easysnmp.exceptions.EasySNMPConnectionError,
                easysnmp.exceptions.EasySNMPNoSuchNameError,
                easysnmp.exceptions.EasySNMPNoSuchObjectError,
                easysnmp.exceptions.EasySNMPTimeoutError,
                easysnmp.exceptions.EasySNMPUndeterminedTypeError,
                easysnmp.exceptions.EasySNMPUnknownObjectIDError):
            pass

    def setattr_ipadentifindex(self):
        """
        snmp walk .1.3.6.1.2.1.4.20.1.2
        .1.3.6.1.2.1.4.20.1.2 = RFC1213-MIB::ipAdEntIfIndex)
        """
        try:
            self.ipAdEntIfIndex = self.walk('.1.3.6.1.2.1.4.20.1.2')
        except (easysnmp.exceptions.EasySNMPError,
                easysnmp.exceptions.EasySNMPNoSuchInstanceError,
                easysnmp.exceptions.EasySNMPConnectionError,
                easysnmp.exceptions.EasySNMPNoSuchNameError,
                easysnmp.exceptions.EasySNMPNoSuchObjectError,
                easysnmp.exceptions.EasySNMPTimeoutError,
                easysnmp.exceptions.EasySNMPUndeterminedTypeError,
                easysnmp.exceptions.EasySNMPUnknownObjectIDError):
            pass
    
    def setattr_ipadentaddr(self):
        """
        snmp walk .1.3.6.1.2.1.4.20.1.1
        .1.3.6.1.2.1.4.20.1.1 = RFC1213-MIB::ipAdEntAddr
        """

        try:
            self.ipAdEntAddr = self.walk('.1.3.6.1.2.1.4.20.1.1')
        except (easysnmp.exceptions.EasySNMPError,
                easysnmp.exceptions.EasySNMPNoSuchInstanceError,
                easysnmp.exceptions.EasySNMPConnectionError,
                easysnmp.exceptions.EasySNMPNoSuchNameError,
                easysnmp.exceptions.EasySNMPNoSuchObjectError,
                easysnmp.exceptions.EasySNMPTimeoutError,
                easysnmp.exceptions.EasySNMPUndeterminedTypeError,
                easysnmp.exceptions.EasySNMPUnknownObjectIDError):
            pass
    
    def setattr_ipadentnetmask(self):
        """
        snmp walk .1.3.6.1.2.1.4.20.1.3
        .1.3.6.1.2.1.4.20.1.3 = RFC1213-MIB::ipAdEntNetMask
        """
        try:
            self.ipAdEntNetMask = self.walk('.1.3.6.1.2.1.4.20.1.3')
        except (easysnmp.exceptions.EasySNMPError,
                easysnmp.exceptions.EasySNMPNoSuchInstanceError,
                easysnmp.exceptions.EasySNMPConnectionError,
                easysnmp.exceptions.EasySNMPNoSuchNameError,
                easysnmp.exceptions.EasySNMPNoSuchObjectError,
                easysnmp.exceptions.EasySNMPTimeoutError,
                easysnmp.exceptions.EasySNMPUndeterminedTypeError,
                easysnmp.exceptions.EasySNMPUnknownObjectIDError):
            pass
    
    def setattr_ifalias(self):
        """
        snmp walk .1.3.6.1.2.1.31.1.1.1.18
        .1.3.6.1.2.1.31.1.1.1.18 = IF-MIB::ifAlias
        """

        try:
            self.ifAlias = self.walk('.1.3.6.1.2.1.31.1.1.1.18')
        except (easysnmp.exceptions.EasySNMPError,
                easysnmp.exceptions.EasySNMPNoSuchInstanceError,
                easysnmp.exceptions.EasySNMPConnectionError,
                easysnmp.exceptions.EasySNMPNoSuchNameError,
                easysnmp.exceptions.EasySNMPNoSuchObjectError,
                easysnmp.exceptions.EasySNMPTimeoutError,
                easysnmp.exceptions.EasySNMPUndeterminedTypeError,
                easysnmp.exceptions.EasySNMPUnknownObjectIDError):
            pass
    
    def setattr_ifname(self):
        """
        snmp walk .1.3.6.1.2.1.31.1.1.1.1
        .1.3.6.1.2.1.31.1.1.1.1 = IF-MIB::ifName
        """
        try:
            self.ifName = self.walk('.1.3.6.1.2.1.31.1.1.1.1')
        except (easysnmp.exceptions.EasySNMPError,
                easysnmp.exceptions.EasySNMPNoSuchInstanceError,
                easysnmp.exceptions.EasySNMPConnectionError,
                easysnmp.exceptions.EasySNMPNoSuchNameError,
                easysnmp.exceptions.EasySNMPNoSuchObjectError,
                easysnmp.exceptions.EasySNMPTimeoutError,
                easysnmp.exceptions.EasySNMPUndeterminedTypeError,
                easysnmp.exceptions.EasySNMPUnknownObjectIDError):
            pass
    
    def setattr_ifdescr(self):
        """
        snmp walk .1.3.6.1.2.1.2.2.1.2
        .1.3.6.1.2.1.2.2.1.2 = IF-MIB::ifDescr
        """
        try:
            self.ifDescr = self.walk('.1.3.6.1.2.1.2.2.1.2')
        except (easysnmp.exceptions.EasySNMPError,
                easysnmp.exceptions.EasySNMPNoSuchInstanceError,
                easysnmp.exceptions.EasySNMPConnectionError,
                easysnmp.exceptions.EasySNMPNoSuchNameError,
                easysnmp.exceptions.EasySNMPNoSuchObjectError,
                easysnmp.exceptions.EasySNMPTimeoutError,
                easysnmp.exceptions.EasySNMPUndeterminedTypeError,
                easysnmp.exceptions.EasySNMPUnknownObjectIDError):
            pass
    
    def setattr_entphysicalmfgname(self):
        """
        snmp walk .1.3.6.1.2.1.47.1.1.1.1.12
        .1.3.6.1.2.1.47.1.1.1.1.12 = ENTITY-MIB::entPhysicalMfgName)
        """

        try:
            self.entPhysicalMfgName = self.walk('.1.3.6.1.2.1.47.1.1.1.1.12')
        except (easysnmp.exceptions.EasySNMPError,
                easysnmp.exceptions.EasySNMPNoSuchInstanceError,
                easysnmp.exceptions.EasySNMPConnectionError,
                easysnmp.exceptions.EasySNMPNoSuchNameError,
                easysnmp.exceptions.EasySNMPNoSuchObjectError,
                easysnmp.exceptions.EasySNMPTimeoutError,
                easysnmp.exceptions.EasySNMPUndeterminedTypeError,
                easysnmp.exceptions.EasySNMPUnknownObjectIDError):
            pass
    
    def setattr_entphysicalserialnum(self):
        """snmp walk .1.3.6.1.2.1.47.1.1.1.1.11
        .1.3.6.1.2.1.47.1.1.1.1.11 = ENTITY-MIB::entPhysicalSerialNum
        """

        try:
            self.entPhysicalSerialNum = self.walk('.1.3.6.1.2.1.47.1.1.1.1.11')
        except (easysnmp.exceptions.EasySNMPError,
                easysnmp.exceptions.EasySNMPNoSuchInstanceError,
                easysnmp.exceptions.EasySNMPConnectionError,
                easysnmp.exceptions.EasySNMPNoSuchNameError,
                easysnmp.exceptions.EasySNMPNoSuchObjectError,
                easysnmp.exceptions.EasySNMPTimeoutError,
                easysnmp.exceptions.EasySNMPUndeterminedTypeError,
                easysnmp.exceptions.EasySNMPUnknownObjectIDError):
            pass
    
    def setattr_entphysicalmodelname(self):
        """snmp walk .1.3.6.1.2.1.47.1.1.1.1.13
        .1.3.6.1.2.1.47.1.1.1.1.13 = ENTITY-MIB::entPhysicalModelName
        """

        try:
            self.entPhysicalModelName = self.walk('.1.3.6.1.2.1.47.1.1.1.1.13')
        except (easysnmp.exceptions.EasySNMPError,
                easysnmp.exceptions.EasySNMPNoSuchInstanceError,
                easysnmp.exceptions.EasySNMPConnectionError,
                easysnmp.exceptions.EasySNMPNoSuchNameError,
                easysnmp.exceptions.EasySNMPNoSuchObjectError,
                easysnmp.exceptions.EasySNMPTimeoutError,
                easysnmp.exceptions.EasySNMPUndeterminedTypeError,
                easysnmp.exceptions.EasySNMPUnknownObjectIDError):
            pass
        
    def set_all_attr_values(self):
        """
        Execute all the SNMP get/walk methods whose name starts with
        "setattr_".

        Create a generator variable containing a list of instance attributes
        that start with "setattr_". Interate through the generator executing
        each element in the generator. This is a handy way to execute the
        instance methods beginning with "setattr_" without needing to add
        each method to this method.

        This method is meant to simplify the "bulk" execution of the methods
        that retrieve SNMP data from a network managed device.
        """
        setattr_methods = (getattr(self, attribute)
                           for attribute in dir(self)
                           if attribute.startswith('setattr_'))

        for setattr_method in setattr_methods:
            setattr_method()

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.__dict__)
