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

import inspect
import ipaddress
from collections import namedtuple
from itertools import zip_longest
from pysnmp.hlapi import *


class CiscoPySNMP(object):
    def __init__(self, host, community, mpmodel=1):
        self.host = host
        self.snmp_community = community
        self.mpmodel = mpmodel
        self.SNMP = namedtuple('SNMP', ['req_oid_astuple',
                                        'req_oid_asstring',
                                        'res_oid_astuple',
                                        'res_oid_asstring',
                                        'res_oid_index_astuple',
                                        'res_oid_index_asstring',
                                        'res_oid_value_asstring'])
        self.ipAdEntIfIndex = list()
        self.entLogicalType = list()
        self.sysName = None
        self.ipAdEntAddr = list()
        self.ipAdEntNetMask = list()
        self.ifAlias = list()
        self.ifDescr = list()
        self.ifName = list()
        self.entPhysicalMfgName = list()
        self.entPhysicalSerialNum = list()
        self.entPhysicalModelName = list()
        self.cvVrfInterfaceRowStatus = list()
        self.udpTransportTarget = UdpTransportTarget((self.host, 161), timeout=5, retries=2)
        self.snmpEngine = SnmpEngine()
        self.communityData = CommunityData(self.snmp_community, mpModel=self.mpmodel)
        self.contextData = ContextData()

    @staticmethod
    def _find_oid_index(req_oid_tuple, res_oid_tuple):
        return tuple([y for x, y in zip_longest(req_oid_tuple, res_oid_tuple) if not x == y])

    def get_ifindex(self, interface):
        r = None
        if not self.ifDescr:
            self.setattr_ifdescr()

        if not self.ifDescr:
            raise ValueError('Unable to snmp walk ifDescr of {}'.format(self.host))

        for v in self.ifDescr:
            if interface == v.res_oid_value_asstring:
                r = v.res_oid_index_asstring

        return r

    def get_ifip(self, interface):
        ipv4network = None
        ip_address = None

        if not self.ipAdEntIfIndex:
            self.setattr_ipadentifindex()
            self.setattr_ipadentaddr()
            self.setattr_ipadentnetmask()

        if not self.ipAdEntIfIndex:
            value_err_msg = 'Unable to snmp walk ipAdEntIfIndex of {}'
            raise ValueError(value_err_msg.format(self.host))
        
        for v in self.ipAdEntIfIndex:
            if v.res_oid_value_asstring == self.get_ifindex(interface):
                ip_address = v.res_oid_index_asstring

        for ipadentaddr, ipadentnetmask in zip(self.ipAdEntAddr,
                                               self.ipAdEntNetMask):
            if ipadentaddr.res_oid_index_asstring == ip_address:
                ipv4network = ipaddress.IPv4Interface('{}/{}'.format(ipadentaddr.res_oid_index_asstring,
                                                                     ipadentnetmask.res_oid_value_asstring))

        if ipv4network is None:
            raise ValueError('ipv4network error: device {} interface {}'.format(self.host, interface))
        else:
            return ipv4network

    def get_ifalias(self, interface):
        ifindex = self.get_ifindex(interface)
        ifalias = ''

        if not self.ifAlias:
            self.setattr_ifalias()

        if not self.ifAlias:
            raise ValueError('Method get_ifalias() fail: unable to set instance attribute ifAlias.')

        for v in self.ifAlias:
            if v.oid_index == ifindex:
                ifalias = v.value

        return ifalias
    
    def get_ifvrfname(self, interface):
        ifvrfname = ''

        if self.cvVrfInterfaceRowStatus is None:
            self.setattr_cvvrfinterfacerowstatus()

        if self.cvVrfInterfaceRowStatus is None:
            value_err_msg = 'Unable to snmp walk cvVrfInterfaceRowStatus of {}'
            raise ValueError(value_err_msg.format(self.host))

        for v in self.cvVrfInterfaceRowStatus:
            if v.oid_index.split('.')[-1] == self.get_ifindex(interface):
                ifvrfname = self.get(('1.3.6.1.4.1.9.9.711.1.1.1.1.2', v.oid_index.split('.')[0])).value

        return ifvrfname

    def get_hostname(self):
        if self.sysName is None:
            self.setattr_sysname()

        if self.sysName is None:
            value_err_msg = 'Unable to snmp get sysName.0 of {}'
            raise ValueError(value_err_msg.format(self.host))

        return self.sysName.res_oid_value_asstring.split('.')[0]

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
        method_name = inspect.currentframe().f_code.co_name
        req_oid_astuple = (1, 3, 6, 1, 2, 1, 1, 5)
        req_oid_asstring = '.'.join(str(x) for x in req_oid_astuple)
        object_identity = ObjectIdentity(req_oid_astuple)
        object_type = ObjectType(object_identity)

        for (error_indication,
             error_status,
             error_index,
             var_binds) in nextCmd(self.snmpEngine,
                                   self.communityData,
                                   self.udpTransportTarget,
                                   self.contextData,
                                   object_type,
                                   lexicographicMode=False):
            if error_indication:
                raise AssertionError('Method', method_name, 'error indication')
            elif error_status:
                raise AssertionError('Method', method_name, 'error status:', error_status.prettyPrint(),
                                     error_index and var_binds[int(error_index) - 1][0] or '?')
            else:
                obj_type = var_binds[0]
                obj_identity = obj_type[0]
                res_oid = obj_identity.getOid()
                res_oid_astuple = res_oid.asTuple()
                res_oid_asstring = res_oid.prettyPrint()
                res_oid_index_astuple = self._find_oid_index(req_oid_astuple, res_oid_astuple)
                res_oid_index_astring = '.'.join([str(x) for x in res_oid_index_astuple])
                res_oid_value = obj_type[1].prettyPrint()
                self.sysName = self.SNMP(req_oid_astuple,
                                         req_oid_asstring,
                                         res_oid_astuple,
                                         res_oid_asstring,
                                         res_oid_index_astuple,
                                         res_oid_index_astring,
                                         res_oid_value)

    def setattr_ipadentifindex(self):
        """
        snmp walk 1.3.6.1.2.1.4.20.1.2
        1.3.6.1.2.1.4.20.1.2 = RFC1213-MIB::ipAdEntIfIndex)
        """
        method_name = inspect.currentframe().f_code.co_name
        req_oid_astuple = (1, 3, 6, 1, 2, 1, 4, 20, 1, 2)
        req_oid_asstring = '.'.join(str(x) for x in req_oid_astuple)
        object_identity = ObjectIdentity(req_oid_astuple)
        object_type = ObjectType(object_identity)

        for (error_indication,
             error_status,
             error_index,
             var_binds) in nextCmd(self.snmpEngine,
                                   self.communityData,
                                   self.udpTransportTarget,
                                   self.contextData,
                                   object_type,
                                   lexicographicMode=False):
            if error_indication:
                raise AssertionError('Method', method_name, 'error indication')
            elif error_status:
                raise AssertionError('Method', method_name, 'error status:', error_status.prettyPrint(),
                                     error_index and var_binds[int(error_index) - 1][0] or '?')
            else:
                obj_type = var_binds[0]
                obj_identity = obj_type[0]
                res_oid = obj_identity.getOid()
                res_oid_astuple = res_oid.asTuple()
                res_oid_asstring = res_oid.prettyPrint()
                res_oid_index_astuple = self._find_oid_index(req_oid_astuple, res_oid_astuple)
                res_oid_index_astring = '.'.join([str(x) for x in res_oid_index_astuple])
                res_oid_value = obj_type[1].prettyPrint()
                self.ipAdEntIfIndex.append(self.SNMP(req_oid_astuple,
                                                     req_oid_asstring,
                                                     res_oid_astuple,
                                                     res_oid_asstring,
                                                     res_oid_index_astuple,
                                                     res_oid_index_astring,
                                                     res_oid_value))

    def setattr_ipadentaddr(self):
        """
        snmp walk 1.3.6.1.2.1.4.20.1.1
        1.3.6.1.2.1.4.20.1.1 = RFC1213-MIB::ipAdEntAddr
        """
        method_name = inspect.currentframe().f_code.co_name
        req_oid_astuple = (1, 3, 6, 1, 2, 1, 4, 20, 1, 1)
        req_oid_asstring = '.'.join(str(x) for x in req_oid_astuple)
        object_identity = ObjectIdentity(req_oid_astuple)
        object_type = ObjectType(object_identity)

        for (error_indication,
             error_status,
             error_index,
             var_binds) in nextCmd(self.snmpEngine,
                                   self.communityData,
                                   self.udpTransportTarget,
                                   self.contextData,
                                   object_type,
                                   lexicographicMode=False):
            if error_indication:
                raise AssertionError('Method', method_name, 'error indication')
            elif error_status:
                raise AssertionError('Method', method_name, 'error status:', error_status.prettyPrint(),
                                     error_index and var_binds[int(error_index) - 1][0] or '?')
            else:
                obj_type = var_binds[0]
                obj_identity = obj_type[0]
                res_oid = obj_identity.getOid()
                res_oid_astuple = res_oid.asTuple()
                res_oid_asstring = res_oid.prettyPrint()
                res_oid_index_astuple = self._find_oid_index(req_oid_astuple, res_oid_astuple)
                res_oid_index_astring = '.'.join([str(x) for x in res_oid_index_astuple])
                res_oid_value = obj_type[1].prettyPrint()
                self.ipAdEntAddr.append(self.SNMP(req_oid_astuple,
                                                  req_oid_asstring,
                                                  res_oid_astuple,
                                                  res_oid_asstring,
                                                  res_oid_index_astuple,
                                                  res_oid_index_astring,
                                                  res_oid_value))
    
    def setattr_ipadentnetmask(self):
        """
        snmp walk 1.3.6.1.2.1.4.20.1.3
        1.3.6.1.2.1.4.20.1.3 = RFC1213-MIB::ipAdEntNetMask
        """
        method_name = inspect.currentframe().f_code.co_name
        req_oid_astuple = (1, 3, 6, 1, 2, 1, 4, 20, 1, 3)
        req_oid_asstring = '.'.join(str(x) for x in req_oid_astuple)
        object_identity = ObjectIdentity(req_oid_astuple)
        object_type = ObjectType(object_identity)

        for (error_indication,
             error_status,
             error_index,
             var_binds) in nextCmd(self.snmpEngine,
                                   self.communityData,
                                   self.udpTransportTarget,
                                   self.contextData,
                                   object_type,
                                   lexicographicMode=False):
            if error_indication:
                raise AssertionError('Method', method_name, 'error indication')
            elif error_status:
                raise AssertionError('Method', method_name, 'error status:', error_status.prettyPrint(),
                                     error_index and var_binds[int(error_index) - 1][0] or '?')
            else:
                obj_type = var_binds[0]
                obj_identity = obj_type[0]
                res_oid = obj_identity.getOid()
                res_oid_astuple = res_oid.asTuple()
                res_oid_asstring = res_oid.prettyPrint()
                res_oid_index_astuple = self._find_oid_index(req_oid_astuple, res_oid_astuple)
                res_oid_index_astring = '.'.join([str(x) for x in res_oid_index_astuple])
                res_oid_value = obj_type[1].prettyPrint()
                self.ipAdEntNetMask.append(self.SNMP(req_oid_astuple,
                                                     req_oid_asstring,
                                                     res_oid_astuple,
                                                     res_oid_asstring,
                                                     res_oid_index_astuple,
                                                     res_oid_index_astring,
                                                     res_oid_value))
    
    def setattr_ifalias(self):
        """
        snmp walk 1.3.6.1.2.1.31.1.1.1.18
        1.3.6.1.2.1.31.1.1.1.18 = IF-MIB::ifAlias
        """
        method_name = inspect.currentframe().f_code.co_name
        req_oid_astuple = (1, 3, 6, 1, 2, 1, 31, 1, 1, 1, 18)
        req_oid_asstring = '.'.join([str(x) for x in req_oid_astuple])
        object_identity = ObjectIdentity(req_oid_astuple)
        object_type = ObjectType(object_identity)

        for (error_indication,
             error_status,
             error_index,
             var_binds) in nextCmd(self.snmpEngine,
                                   self.communityData,
                                   self.udpTransportTarget,
                                   self.contextData,
                                   object_type,
                                   lexicographicMode=False):
            if error_indication:
                raise AssertionError('Method', method_name, 'error indication')
            elif error_status:
                raise AssertionError('Method', method_name, 'error status:', error_status.prettyPrint(),
                                     error_index and var_binds[int(error_index) - 1][0] or '?')
            else:
                obj_type = var_binds[0]
                obj_identity = obj_type[0]
                res_oid = obj_identity.getOid()
                res_oid_astuple = res_oid.asTuple()
                res_oid_asstring = res_oid.prettyPrint()
                res_oid_index_astuple = self._find_oid_index(req_oid_astuple, res_oid_astuple)
                res_oid_index_astring = '.'.join([str(x) for x in res_oid_index_astuple])
                res_oid_value = obj_type[1].prettyPrint()
                self.ifAlias.append(self.SNMP(req_oid_astuple,
                                              req_oid_asstring,
                                              res_oid_astuple,
                                              res_oid_asstring,
                                              res_oid_index_astuple,
                                              res_oid_index_astring,
                                              res_oid_value))

    def setattr_ifname(self):
        """
        snmp walk 1.3.6.1.2.1.31.1.1.1.1
        1.3.6.1.2.1.31.1.1.1.1 = IF-MIB::ifName
        """
        method_name = inspect.currentframe().f_code.co_name
        req_oid_astuple = (1, 3, 6, 1, 2, 1, 31, 1, 1, 1, 1)
        req_oid_asstring = '.'.join([str(x) for x in req_oid_astuple])
        object_identity = ObjectIdentity(req_oid_astuple)
        object_type = ObjectType(object_identity)

        for (error_indication,
             error_status,
             error_index,
             var_binds) in nextCmd(self.snmpEngine,
                                   self.communityData,
                                   self.udpTransportTarget,
                                   self.contextData,
                                   object_type,
                                   lexicographicMode=False):
            if error_indication:
                raise AssertionError('Method', method_name, 'error indication')
            elif error_status:
                raise AssertionError('Method', method_name, 'error status:', error_status.prettyPrint(),
                                     error_index and var_binds[int(error_index) - 1][0] or '?')
            else:
                obj_type = var_binds[0]
                obj_identity = obj_type[0]
                res_oid = obj_identity.getOid()
                res_oid_astuple = res_oid.asTuple()
                res_oid_asstring = res_oid.prettyPrint()
                res_oid_index_astuple = self._find_oid_index(req_oid_astuple, res_oid_astuple)
                res_oid_index_astring = '.'.join([str(x) for x in res_oid_index_astuple])
                res_oid_value = obj_type[1].prettyPrint()
                self.ifName.append(self.SNMP(req_oid_astuple,
                                             req_oid_asstring,
                                             res_oid_astuple,
                                             res_oid_asstring,
                                             res_oid_index_astuple,
                                             res_oid_index_astring,
                                             res_oid_value))
    
    def setattr_ifdescr(self):
        """
        snmp walk 1.3.6.1.2.1.2.2.1.2
        1.3.6.1.2.1.2.2.1.2 = IF-MIB::ifDescr
        """
        method_name = inspect.currentframe().f_code.co_name
        req_oid_astuple = (1, 3, 6, 1, 2, 1, 2, 2, 1, 2)
        req_oid_asstring = '.'.join([str(x) for x in req_oid_astuple])
        object_identity = ObjectIdentity(req_oid_astuple)
        object_type = ObjectType(object_identity)

        for (error_indication,
             error_status,
             error_index,
             var_binds) in nextCmd(self.snmpEngine,
                                   self.communityData,
                                   self.udpTransportTarget,
                                   self.contextData,
                                   object_type,
                                   lexicographicMode=False):
            if error_indication:
                raise AssertionError('Method', method_name, 'error indication')
            elif error_status:
                raise AssertionError('Method', method_name, 'error status:', error_status.prettyPrint(),
                                     error_index and var_binds[int(error_index) - 1][0] or '?')
            else:
                obj_type = var_binds[0]
                obj_identity = obj_type[0]
                res_oid = obj_identity.getOid()
                res_oid_astuple = res_oid.asTuple()
                res_oid_asstring = res_oid.prettyPrint()
                res_oid_index_astuple = self._find_oid_index(req_oid_astuple, res_oid_astuple)
                res_oid_index_astring = '.'.join([str(x) for x in res_oid_index_astuple])
                res_oid_value = obj_type[1].prettyPrint()
                self.ifDescr.append(self.SNMP(req_oid_astuple,
                                              req_oid_asstring,
                                              res_oid_astuple,
                                              res_oid_asstring,
                                              res_oid_index_astuple,
                                              res_oid_index_astring,
                                              res_oid_value))
    
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
