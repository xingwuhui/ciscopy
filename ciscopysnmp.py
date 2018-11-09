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

from collections import namedtuple
from pysnmp.hlapi import *
# import easysnmp


class CiscoPySNMP(object):
    def __init__(self, host, community, mpmodel=1):
        self.host_nameorip = host
        self.snmp_community = community
        self.mpmodel = mpmodel
        self.SNMP = namedtuple('SNMP', ['oid', 'oid_index', 'value'])
        self.ifDescr = list()
        self.ipAdEntIfIndex = list()
        self.entLogicalType = list()
        self.sysName = None
        self.ipAdEntAddr = list()
        self.ipAdEntNetMask = list()
        self.ifAlias = list()
        self.ifName = list()
        self.entPhysicalMfgName = list()
        self.entPhysicalSerialNum = list()
        self.entPhysicalModelName = list()
        self.cvVrfInterfaceRowStatus = list()
        self.udpTransportTarget = UdpTransportTarget((self.host_nameorip, 161), timeout=5, retries=2)
        self.snmpEngine = SnmpEngine()
        self.communityData = CommunityData(self.snmp_community, mpModel=self.mpmodel)
        self.contextData = ContextData()

    def get_ifindex(self, interface):
        r = None
        
        if self.ifDescr is None:
            self.setattr_ifdescr()

        if self.ifDescr is None:
            raise ValueError('Unable to snmp walk ifDescr of {}'.format(self.host_nameorip))

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
            self.setattr_ipadentifindex()
            self.setattr_ipadentaddr()
            self.setattr_ipadentnetmask()

        if self.ipAdEntIfIndex is None:
            value_err_msg = 'Unable to snmp walk ipAdEntIfIndex of {}'
            raise ValueError(value_err_msg.format(self.host_nameorip))
        
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

        if ipv4network is None:
            raise ValueError('ipv4network error: device {} interface {}'.format(self.host, interface))
        else:
            return ipv4network

    def get_ifalias(self, interface):
        ifindex = self.get_ifindex(interface)

        ifalias = nextCmd(self.snmpEngine, self.communityData, self.udpTransportTarget, self.contextData, )

        return ifalias.value
    
    def get_ifvrfname(self, interface):
        ifvrfname = ''

        if self.cvVrfInterfaceRowStatus is None:
            self.setattr_cvvrfinterfacerowstatus()

        if self.cvVrfInterfaceRowStatus is None:
            value_err_msg = 'Unable to snmp walk cvVrfInterfaceRowStatus of {}'
            raise ValueError(value_err_msg.format(self.host_nameorip))

        for v in self.cvVrfInterfaceRowStatus:
            if v.oid_index.split('.')[-1] == self.get_ifindex(interface):
                ifvrfname = self.get(('1.3.6.1.4.1.9.9.711.1.1.1.1.2', v.oid_index.split('.')[0])).value

        return ifvrfname

    def get_hostname(self):
        if self.sysName is None:
            self.setattr_sysname()

        if self.sysName is None:
            value_err_msg = 'Unable to snmp get sysName.0 of {}'
            raise ValueError(value_err_msg.format(self.host_nameorip))

        return self.sysName.value.split('.')[0]

    def setattr_entlogicaltype(self):
        """snmp walk 1.3.6.1.2.1.47.1.2.1.1.3
        1.3.6.1.2.1.47.1.2.1.1.3 = ENTITY-MIB::entLogicalType
        """
        oid = ('1', '3', '6', '1', '2', '1', '47', '1', '2', '1', '1', '3')
        full_oid = '.'.join(oid)
        objectidentity = ObjectIdentity(full_oid)
        objecttype = ObjectType(objectidentity)
        for (errIndication,
             errStatus,
             errIndex,
             varBinds) in nextCmd(self.snmpEngine,
                                  self.communityData,
                                  self.udpTransportTarget,
                                  self.contextData,
                                  objecttype,
                                  lexicographicMode=False):
            if errIndication:
                pass

    def setattr_sysname(self):
        """
        snmp get 1.3.6.1.2.1.1.5.0
        OID = 1.3.6.1.2.1.1.5 = SNMPv2-MIB::sysName
        OID Index = 0
        """
        oid = ('1', '3', '6', '1', '2', '1', '1', '5')
        oid_index = ('0',)
        full_oid = oid + oid_index
        full_oid_asstring = '.'.join(full_oid)
        objectidentity = ObjectIdentity(full_oid_asstring)
        objecttype = ObjectType(objectidentity)
        (errIndication,
         errStatus,
         errIndex,
         varBinds) = next(getCmd(self.snmpEngine,
                                 self.communityData,
                                 self.udpTransportTarget,
                                 self.contextData,
                                 objecttype))

        if errIndication:
            raise AssertionError('Function', __name__, 'errIndication:', errIndication)
        elif errStatus:
            raise AssertionError('Method', __name__, 'errStatus:',
                                 errStatus.prettyPrint(),
                                 errIndex and varBinds[int(errIndex) - 1][0] or '?')
        else:
            oid = '.'.join(oid)
            oid_index = '.'.join(oid_index)
            objecttype = varBinds[0]
            value = objecttype[-1].prettyPrint()
            self.sysName = self.SNMP(oid, oid_index, value)

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

    def setattr_cvvrfinterfacerowstatus(self):
        """snmp walk .1.3.6.1.4.1.9.9.711.1.2.1.1.5
        .1.3.6.1.4.1.9.9.711.1.2.1.1.5 = ciscoVrfMIB::cvVrfInterfaceRowStatus
        """

        try:
            self.cvVrfInterfaceRowStatus = self.walk('.1.3.6.1.4.1.9.9.711.1.2.1.1.5')
        except (easysnmp.exceptions.EasySNMPError, easysnmp.exceptions.EasySNMPNoSuchInstanceError,
                easysnmp.exceptions.EasySNMPConnectionError, easysnmp.exceptions.EasySNMPNoSuchNameError,
                easysnmp.exceptions.EasySNMPNoSuchObjectError, easysnmp.exceptions.EasySNMPTimeoutError,
                easysnmp.exceptions.EasySNMPUndeterminedTypeError, easysnmp.exceptions.EasySNMPUnknownObjectIDError):
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
