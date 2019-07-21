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
from itertools import zip_longest
from pysnmp.hlapi import getCmd, nextCmd, SnmpEngine, CommunityData, UdpTransportTarget, ContextData
from pysnmp.hlapi import ObjectIdentity, ObjectType


class SnmpObjId:
    __slots__ = ['req_oid_astuple', 'req_oid_asstring', 'res_oid_astuple', 'full_oid', 'oid', 'oid_index_astuple',
                 'oid_index', 'oid_value']

    def __init__(self, request_oid_astuple: tuple = (), result_oid_astuple: tuple = (),
                 result_oid_value_asstring: str = ''):
        self.req_oid_astuple = request_oid_astuple
        self.req_oid_asstring = '.'.join([str(x) for x in self.req_oid_astuple])
        self.res_oid_astuple = result_oid_astuple
        self.full_oid = '.'.join([str(tuple_value) for tuple_value in self.res_oid_astuple])
        
        if self.req_oid_astuple == self.res_oid_astuple:
            self.oid = '.'.join(self.full_oid.split('.')[0:-1])
        else:
            self.oid = '.'.join([str(tuple_value) for tuple_value in self.req_oid_astuple])
        
        self.oid_index_astuple = self._find_oid_index(self.req_oid_astuple, self.res_oid_astuple)
        self.oid_index = '.'.join([str(x) for x in self.oid_index_astuple])
        self.oid_value = result_oid_value_asstring

    @staticmethod
    def _find_oid_index(req_oid_tuple: tuple, res_oid_tuple: tuple) -> tuple:
        if req_oid_tuple == res_oid_tuple:
            return res_oid_tuple[-1],
        else:
            return tuple([y for x, y in zip_longest(req_oid_tuple, res_oid_tuple) if not x == y])

    def __repr__(self):
        repr_string = '<{}(full_oid={}, oid={}, oid_index={}, oid_value={})>'
        return repr_string.format(self.__class__.__name__, self.full_oid, self.oid, self.oid_index, self.oid_value)


class CiscoPySNMP:
    def __init__(self, host_ip, snmp_community, mpmodel=1):
        self.host_ip = host_ip
        self.snmp_community = snmp_community
        self.mpmodel = mpmodel
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
        self.entPhysicalSoftwareRev = list()
        self.entPhysicalDescr = list()
        self.cvVrfInterfaceRowStatus = list()
        self.cswMaxSwitchNum = None
        self.cswSwitchNumCurrent = list()
        self.cswSwitchState = list()
        self.cswSwitchRole = list()
        self.cvsSwitchMode = 'Standalone'
        self.cvsChassisSwitchID = list()
        self.cvsChassisRole = list()
        self.cvsModuleSlotNumber = list()
        self.snmpEngine = SnmpEngine()
        self.communityData = CommunityData(self.snmp_community, mpModel=self.mpmodel)
        self.udpTransportTarget = UdpTransportTarget((self.host_ip, 161), timeout=10.0, retries=2)
        self.contextData = ContextData()

    def __hasattribute(self, attribute):
        if not hasattr(self, attribute):
            return False
        else:
            return True

    def snmpwalk(self, oid_astuple: tuple):
        if not isinstance(oid_astuple, tuple):
            raise TypeError('snmpwalk method paramter oid_astuple value {} is not type tuple'.format(oid_astuple))

        method_name = inspect.currentframe().f_code.co_name
        # inspect_stack = inspect.stack()[0]
        # inspect_stack_function = inspect_stack.function
        req_oid_astuple = oid_astuple
        object_identity = ObjectIdentity(req_oid_astuple)
        object_type = ObjectType(object_identity)

        for (error_indication,
             error_status,
             error_index,
             var_binds) in nextCmd(self.snmpEngine, self.communityData, self.udpTransportTarget, self.contextData,
                                   object_type, lexicographicMode=False, ignoreNonIncreasingOid=True):
            if error_indication:
                raise AssertionError('Method {}: error indication: {}'.format(method_name, error_indication))
            elif error_status:
                raise AssertionError('Method {}: error status: {} {}'.format(method_name,
                                                                             error_status.prettyPrint(),
                                                                             error_index and var_binds[int(
                                                                                     error_index) - 1][0] or '?'))
            else:
                obj_type = var_binds[0]
                obj_identity = obj_type[0]
                res_oid = obj_identity.getOid()
                res_oid_astuple = res_oid.asTuple()
                # res_oid_index_astuple = self._find_oid_index(req_oid_astuple, res_oid_astuple)
                res_oid_value = obj_type[1].prettyPrint()
                yield SnmpObjId(req_oid_astuple, res_oid_astuple, res_oid_value)

    def snmpget(self, oid_astuple: tuple):
        if not isinstance(oid_astuple, tuple):
            raise TypeError('snmpwalk method paramter oid_astuple value {} is not type tuple'.format(oid_astuple))

        method_name = inspect.currentframe().f_code.co_name
        # inspect_stack = inspect.stack()[0]
        # inspect_stack_function = inspect_stack.function
        req_oid_astuple = oid_astuple
        object_identity = ObjectIdentity(req_oid_astuple)
        object_type = ObjectType(object_identity)

        for (error_indication,
             error_status,
             error_index,
             var_binds) in getCmd(self.snmpEngine, self.communityData, self.udpTransportTarget, self.contextData,
                                  object_type):
            if error_indication:
                raise AssertionError('Method', method_name, 'error indication:', error_indication)
            elif error_status:
                raise AssertionError('Method', method_name, 'error status:', error_status.prettyPrint(),
                                     error_index and var_binds[int(error_index) - 1][0] or '?')
            else:
                obj_type = var_binds[0]
                obj_identity = obj_type[0]
                res_oid = obj_identity.getOid()
                res_oid_astuple = res_oid.asTuple()
                # res_oid_index_astuple = self._find_oid_index(req_oid_astuple, res_oid_astuple)
                res_oid_value = obj_type[1].prettyPrint()
                yield SnmpObjId(req_oid_astuple, res_oid_astuple, res_oid_value)

    def setattr_entlogicaltype(self):
        """
        snmp walk 1.3.6.1.2.1.47.1.2.1.1.3
        1.3.6.1.2.1.47.1.2.1.1.3 = ENTITY-MIB::entLogicalType
        """
        oid_astuple = (1, 3, 6, 1, 2, 1, 47, 1, 2, 1, 1, 3)
        
        if self.entLogicalType:
            self.entLogicalType = list()

        for snmpobjid in self.snmpwalk(oid_astuple):
            self.entLogicalType.append(snmpobjid)

    def setattr_sysname(self):
        """
        snmp get 1.3.6.1.2.1.1.5.0
        OID = 1.3.6.1.2.1.1.5 = SNMPv2-MIB::sysName
        OID Index = 0
        """
        oid_astuple = (1, 3, 6, 1, 2, 1, 1, 5)

        if self.sysName is not None:
            self.sysName = None

        for snmpobjid in self.snmpwalk(oid_astuple):
            self.sysName = snmpobjid

    def setattr_ipadentifindex(self):
        """
        snmp walk 1.3.6.1.2.1.4.20.1.2
        1.3.6.1.2.1.4.20.1.2 = RFC1213-MIB::ipAdEntIfIndex
        """
        oid_astuple = (1, 3, 6, 1, 2, 1, 4, 20, 1, 2)
        
        if self.ipAdEntIfIndex:
            self.ipAdEntIfIndex = list()

        for snmpobjid in self.snmpwalk(oid_astuple):
            self.ipAdEntIfIndex.append(snmpobjid)

    def setattr_ipadentaddr(self):
        """
        snmp walk 1.3.6.1.2.1.4.20.1.1
        1.3.6.1.2.1.4.20.1.1 = RFC1213-MIB::ipAdEntAddr
        """
        oid_astuple = (1, 3, 6, 1, 2, 1, 4, 20, 1, 1)
        
        if self.ipAdEntAddr:
            self.ipAdEntAddr = list()

        for snmpobjid in self.snmpwalk(oid_astuple):
            self.ipAdEntAddr.append(snmpobjid)

    def setattr_ipadentnetmask(self):
        """
        snmp walk 1.3.6.1.2.1.4.20.1.3
        1.3.6.1.2.1.4.20.1.3 = RFC1213-MIB::ipAdEntNetMask
        """
        oid_astuple = (1, 3, 6, 1, 2, 1, 4, 20, 1, 3)

        if self.ipAdEntNetMask:
            self.ipAdEntNetMask = list()

        for snmpobjid in self.snmpwalk(oid_astuple):
            self.ipAdEntNetMask.append(snmpobjid)

    def setattr_ifalias(self):
        """
        snmp walk 1.3.6.1.2.1.31.1.1.1.18
        1.3.6.1.2.1.31.1.1.1.18 = IF-MIB::ifAlias
        """
        oid_astuple = (1, 3, 6, 1, 2, 1, 31, 1, 1, 1, 18)

        if self.ifAlias:
            self.ifAlias = list()

        for snmpobjid in self.snmpwalk(oid_astuple):
            self.ifAlias.append(snmpobjid)

    def setattr_ifname(self):
        """
        snmp walk 1.3.6.1.2.1.31.1.1.1.1
        1.3.6.1.2.1.31.1.1.1.1 = IF-MIB::ifName
        """
        oid_astuple = (1, 3, 6, 1, 2, 1, 31, 1, 1, 1, 1)

        if self.ifName:
            self.ifName = list()

        for snmpobjid in self.snmpwalk(oid_astuple):
            self.ifName.append(snmpobjid)

    def setattr_ifdescr(self):
        """
        snmp walk 1.3.6.1.2.1.2.2.1.2
        1.3.6.1.2.1.2.2.1.2 = IF-MIB::ifDescr
        """
        oid_astuple = (1, 3, 6, 1, 2, 1, 2, 2, 1, 2)

        if self.ifDescr:
            self.ifDescr = list()

        for snmpobjid in self.snmpwalk(oid_astuple):
            self.ifDescr.append(snmpobjid)

    def setattr_entphysicalserialnum(self):
        """
        snmp walk 1.3.6.1.2.1.47.1.1.1.1.11
        1.3.6.1.2.1.47.1.1.1.1.11 = ENTITY-MIB::entPhysicalSerialNum
        """
        oid_astuple = (1, 3, 6, 1, 2, 1, 47, 1, 1, 1, 1, 11)

        if self.entPhysicalSerialNum:
            self.entPhysicalSerialNum = list()

        for snmpobjid in self.snmpwalk(oid_astuple):
            self.entPhysicalSerialNum.append(snmpobjid)

    def setattr_entphysicalmodelname(self):
        """
        snmp walk 1.3.6.1.2.1.47.1.1.1.1.13
        1.3.6.1.2.1.47.1.1.1.1.13 = ENTITY-MIB::entPhysicalModelName
        """
        oid_astuple = (1, 3, 6, 1, 2, 1, 47, 1, 1, 1, 1, 13)

        if self.entPhysicalModelName:
            self.entPhysicalModelName = list()

        for snmpobjid in self.snmpwalk(oid_astuple):
            self.entPhysicalModelName.append(snmpobjid)

    def setattr_entphysicalsoftwarerev(self):
        """
        snmp walk 1.3.6.1.2.1.47.1.1.1.1.10
        1.3.6.1.2.1.47.1.1.1.1.10 = ENTITY-MIB::entPhysicalSoftwareRev
        """
        oid_astuple = (1, 3, 6, 1, 2, 1, 47, 1, 1, 1, 1, 10)

        if self.entPhysicalSoftwareRev:
            self.entPhysicalSoftwareRev = list()

        for snmpobjid in self.snmpwalk(oid_astuple):
            self.entPhysicalSoftwareRev.append(snmpobjid)

    def setattr_entphysicaldescr(self):
        """
        snmp walk 1.3.6.1.2.1.47.1.1.1.1.2
        1.3.6.1.2.1.47.1.1.1.1.2 = ENTITY-MIB::entPhysicalDescr
        """
        oid_astuple = (1, 3, 6, 1, 2, 1, 47, 1, 1, 1, 1, 2)

        if self.entPhysicalDescr:
            self.entPhysicalDescr = list()

        for snmpobjid in self.snmpwalk(oid_astuple):
            self.entPhysicalDescr.append(snmpobjid)

    def setattr_cvvrfinterfacerowstatus(self):
        """
        snmp walk 1.3.6.1.4.1.9.9.711.1.2.1.1.5
        1.3.6.1.4.1.9.9.711.1.2.1.1.5 = ciscoVrfMIB::cvVrfInterfaceRowStatus
        """
        oid_astuple = (1, 3, 6, 1, 4, 1, 9, 9, 711, 1, 2, 1, 1, 5)

        if self.cvVrfInterfaceRowStatus:
            self.cvVrfInterfaceRowStatus = list()

        for snmpobjid in self.snmpwalk(oid_astuple):
            self.cvVrfInterfaceRowStatus.append(snmpobjid)

    def setattr_cswmaxswitchnum(self):
        """
        snmp walk 1.3.6.1.4.1.9.9.500.1.1.1
        1.3.6.1.4.1.9.9.500.1.1.1 = CISCO-STACKWISE-MIB::cswMaxSwitchNum
        """
        oid_astuple = (1, 3, 6, 1, 4, 1, 9, 9, 500, 1, 1, 1)
    
        if self.cswMaxSwitchNum is not None:
            self.cswMaxSwitchNum = None
    
        for snmpobjid in self.snmpwalk(oid_astuple):
            # self.cswMaxSwitchNum.append(snmpobjid)
            self.cswMaxSwitchNum = snmpobjid

    def setattr_cswswitchnumcurrent(self):
        """
        snmp walk 1.3.6.1.4.1.9.9.500.1.2.1.1.1
        1.3.6.1.4.1.9.9.500.1.2.1.1.1 = CISCO-STACKWISE-MIB::cswSwitchNumCurrent
        """
        oid_astuple = (1, 3, 6, 1, 4, 1, 9, 9, 500, 1, 2, 1, 1, 1)
    
        if self.cswSwitchNumCurrent:
            self.cswSwitchNumCurrent = list()
        
        for snmpobjid in self.snmpwalk(oid_astuple):
            self.cswSwitchNumCurrent.append(snmpobjid)

    def setattr_cswswitchstate(self):
        """
        snmp walk 1.3.6.1.4.1.9.9.500.1.2.1.1.6
        1.3.6.1.4.1.9.9.500.1.2.1.1.6 = CISCO-STACKWISE-MIB::cswSwitchState
        """
        oid_astuple = (1, 3, 6, 1, 4, 1, 9, 9, 500, 1, 2, 1, 1, 6)
    
        if self.cswSwitchState:
            self.cswSwitchState = list()
    
        for snmpobjid in self.snmpwalk(oid_astuple):
            self.cswSwitchState.append(snmpobjid)

    def setattr_cswswitchrole(self):
        """
        snmp walk 1.3.6.1.4.1.9.9.500.1.2.1.1.3
        1.3.6.1.4.1.9.9.500.1.2.1.1.3 = CISCO-STACKWISE-MIB::cswSwitchRole
        """
        oid_astuple = (1, 3, 6, 1, 4, 1, 9, 9, 500, 1, 2, 1, 1, 3)
    
        if self.cswSwitchRole:
            self.cswSwitchRole = list()
    
        for snmpobjid in self.snmpwalk(oid_astuple):
            self.cswSwitchRole.append(snmpobjid)

    def setattr_cvsswitchmode(self):
        """
        snmp walk 1.3.6.1.4.1.9.9.388.1.1.4
        1.3.6.1.4.1.9.9.388.1.1.4 = CISCO-VIRTUAL-SWITCH-MIB::cvsSwitchMode
        """
        oid_astuple = (1, 3, 6, 1, 4, 1, 9, 9, 388, 1, 1, 4)
    
        if self.cvsSwitchMode is not None:
            self.cvsSwitchMode = None
    
        for snmpobjid in self.snmpwalk(oid_astuple):
            self.cvsSwitchMode = snmpobjid

    def setattr_cvschassisswitchid(self):
        """
        snmp walk 1.3.6.1.4.1.9.9.388.1.2.2.1.1
        1.3.6.1.4.1.9.9.388.1.2.2.1.1 = CISCO-VIRTUAL-SWITCH-MIB::cvsChassisSwitchID
        """
        oid_astuple = (1, 3, 6, 1, 4, 1, 9, 9, 388, 1, 2, 2, 1, 1)
    
        if self.cvsChassisSwitchID:
            self.cvsChassisSwitchID = list()
    
        for snmpobjid in self.snmpwalk(oid_astuple):
            self.cvsChassisSwitchID.append(snmpobjid)

    def setattr_cvschassisrole(self):
        """
        snmp walk 1.3.6.1.4.1.9.9.388.1.2.2.1.2
        1.3.6.1.4.1.9.9.388.1.2.2.1.2 = CISCO-VIRTUAL-SWITCH-MIB::cvsChassisRole
        """
        oid_astuple = (1, 3, 6, 1, 4, 1, 9, 9, 388, 1, 2, 2, 1, 2)
    
        if self.cvsChassisRole:
            self.cvsChassisRole = list()
    
        for snmpobjid in self.snmpwalk(oid_astuple):
            self.cvsChassisRole.append(snmpobjid)
    
    def setattr_cvsmoduleslotnumber(self):
        """
        snmp walk 1.3.6.1.4.1.9.9.388.1.4.1.1.3
        1.3.6.1.4.1.9.9.388.1.4.1.1.3 = CISCO-VIRTUAL-SWITCH-MIB::cvsModuleSlotNumber
        """
        oid_astuple = (1, 3, 6, 1, 4, 1, 9, 9, 388, 1, 4, 1, 1, 3)
        
        if self.cvsModuleSlotNumber:
            self.cvsModuleSlotNumber = list()
        
        for snmpobjid in self.snmpwalk(oid_astuple):
            self.cvsModuleSlotNumber.append(snmpobjid)

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
        setattr_methods = (getattr(self, attribute) for attribute in dir(self) if attribute.startswith('setattr_'))

        for setattr_method in setattr_methods:
            setattr_method()

    def __repr__(self):
        return '<{}(host_ip={}, snmp_community={})>'.format(self.__class__.__name__, self.host_ip, self.snmp_community)
