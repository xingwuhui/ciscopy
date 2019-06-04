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
from pysnmp.hlapi import nextCmd, SnmpEngine, CommunityData, UdpTransportTarget, ContextData
from pysnmp.hlapi import ObjectIdentity, ObjectType


class SnmpObjId:
    __slots__ = ['req_oid_astuple', 'req_oid_asstring', 'oid_astuple', 'full_oid', 'oid', 'oid_index_astuple',
                 'oid_index', 'oid_value']

    def __init__(self, request_oid_astuple: tuple = (), result_oid_astuple: tuple = (),
                 result_oid_index_astuple: tuple = (), result_oid_value_asstring: str = ''):
        self.req_oid_astuple = request_oid_astuple
        self.req_oid_asstring = '.'.join([str(x) for x in self.req_oid_astuple])
        self.oid_astuple = result_oid_astuple
        self.full_oid = '.'.join([str(x) for x in self.oid_astuple])
        self.oid = self.req_oid_asstring
        self.oid_index_astuple = result_oid_index_astuple
        self.oid_index = '.'.join([str(x) for x in self.oid_index_astuple])
        self.oid_value = result_oid_value_asstring

    def __repr__(self):
        repr_string = '<{} (full_oid={}, oid={}, oid_index={}, oid_value={})>'
        return repr_string.format(self.__class__.__name__, self.full_oid, self.oid, self.oid_index, self.oid_value)


class CiscoPySNMP:
    def __init__(self, host, community, mpmodel=1):
        self.host = host
        self.snmp_community = community
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
        self.cvVrfInterfaceRowStatus = list()
        self.snmpEngine = SnmpEngine()
        self.communityData = CommunityData(self.snmp_community, mpModel=self.mpmodel)
        self.udpTransportTarget = UdpTransportTarget((self.host, 161), timeout=10.0, retries=3)
        self.contextData = ContextData()

    def __hasattribute(self, attribute):
        if not hasattr(self, attribute):
            return False
        else:
            return True

    @staticmethod
    def _find_oid_index(req_oid_tuple: tuple, res_oid_tuple: tuple) -> tuple:
        return tuple([y for x, y in zip_longest(req_oid_tuple, res_oid_tuple) if not x == y])

    def _snmpwalk(self, oid_astuple: tuple):
        if not isinstance(oid_astuple, tuple):
            raise TypeError('_snmpwalk method paramter oid_astuple value {} is not type tuple'.format(oid_astuple))

        method_name = inspect.currentframe().f_code.co_name
        inspect_stack = inspect.stack()[0]
        inspect_stack_function = inspect_stack.function
        req_oid_astuple = oid_astuple
        object_identity = ObjectIdentity(req_oid_astuple)
        object_type = ObjectType(object_identity)

        for (error_indication,
             error_status,
             error_index,
             var_binds) in nextCmd(self.snmpEngine, self.communityData, self.udpTransportTarget, self.contextData,
                                   object_type, lexicographicMode=False):
            if error_indication:
                raise AssertionError('Method', method_name, 'error indication:', inspect_stack_function)
            elif error_status:
                raise AssertionError('Method', method_name, 'error status:', error_status.prettyPrint(),
                                     error_index and var_binds[int(error_index) - 1][0] or '?', inspect_stack_function)
            else:
                obj_type = var_binds[0]
                obj_identity = obj_type[0]
                res_oid = obj_identity.getOid()
                res_oid_astuple = res_oid.asTuple()
                res_oid_index_astuple = self._find_oid_index(req_oid_astuple, res_oid_astuple)
                res_oid_value = obj_type[1].prettyPrint()
                yield SnmpObjId(req_oid_astuple, res_oid_astuple, res_oid_index_astuple, res_oid_value)

    def get_ifindex(self, interface: str) -> str:
        oid_index = None

        if not self.ifDescr:
            self.setattr_ifdescr()

        if not self.ifDescr:
            raise ValueError('Unable to snmp walk ifDescr of {}'.format(self.host))

        for v in self.ifDescr:
            if interface == v.oid_value:
                oid_index = v.oid_index

        return oid_index

    def get_ifip(self, interface: str) -> ipaddress.IPv4Interface:
        ipv4interface = None
        ip_address = None

        if not self.ipAdEntIfIndex:
            self.setattr_ipadentifindex()
            self.setattr_ipadentaddr()
            self.setattr_ipadentnetmask()

        if not self.ipAdEntIfIndex:
            value_err_msg = 'Unable to snmp walk ipAdEntIfIndex of {}'
            raise ValueError(value_err_msg.format(self.host))

        for v in self.ipAdEntIfIndex:
            if v.oid_value == self.get_ifindex(interface):
                ip_address = v.oid_index

        for ipadentaddr, ipadentnetmask in zip(self.ipAdEntAddr, self.ipAdEntNetMask):
            if ipadentaddr.oid_index == ip_address:
                ipv4interface = ipaddress.IPv4Interface('{}/{}'.format(ipadentaddr.oid_index, ipadentnetmask.oid_value))

        if ipv4interface is None:
            raise ValueError('`IPv4Interface` error: device {} interface {}'.format(self.host, interface))
        else:
            return ipv4interface

    def get_ifalias(self, interface: str) -> str:
        ifindex = self.get_ifindex(interface)
        ifalias = ''

        if not self.ifAlias:
            self.setattr_ifalias()

        if not self.ifAlias:
            raise ValueError('Method get_ifalias() fail: unable to set instance attribute ifAlias.')

        for v in self.ifAlias:
            if v.oid_index == ifindex:
                ifalias = v.oid_value

        return ifalias

    def get_ifvrfname(self, interface: str) -> str:
        ifvrfname = ''

        cvvrfname_oid_astuple = (1, 3, 6, 1, 4, 1, 9, 9, 711, 1, 1, 1, 1, 2)

        if self.cvVrfInterfaceRowStatus is None:
            self.setattr_cvvrfinterfacerowstatus()

        if self.cvVrfInterfaceRowStatus is None:
            value_err_msg = 'Unable to snmp walk cvVrfInterfaceRowStatus of {}'
            raise ValueError(value_err_msg.format(self.host))

        for v in self.cvVrfInterfaceRowStatus:
            if v.oid_index.split('.')[-1] == self.get_ifindex(interface):
                res_oid_index_aslist = list(v.oid_index_astuple)
                res_oid_index_aslist.pop(-1)
                req_oid_astuple = cvvrfname_oid_astuple + tuple(res_oid_index_aslist)
                for e in self._snmpwalk(req_oid_astuple):
                    ifvrfname = e.oid_value

        return ifvrfname

    @property
    def get_hostname(self) -> str:
        if self.sysName is None:
            self.setattr_sysname()

        if self.sysName is None:
            value_err_msg = 'Unable to snmp get sysName.0 of {}'
            raise ValueError(value_err_msg.format(self.host))

        return self.sysName.oid_value.split('.')[0]

    def setattr_entlogicaltype(self):
        """
        snmp walk 1.3.6.1.2.1.47.1.2.1.1.3
        1.3.6.1.2.1.47.1.2.1.1.3 = ENTITY-MIB::entLogicalType
        """
        oid_astuple = (1, 3, 6, 1, 2, 1, 47, 1, 2, 1, 1, 3)

        if not hasattr(self, 'entLogicalType'):
            self.entLogicalType = list()

        for v in self._snmpwalk(oid_astuple):
            self.entLogicalType.append(v)

    def setattr_sysname(self):
        """
        snmp get 1.3.6.1.2.1.1.5.0
        OID = 1.3.6.1.2.1.1.5 = SNMPv2-MIB::sysName
        OID Index = 0
        """
        oid_astuple = (1, 3, 6, 1, 2, 1, 1, 5)

        if not hasattr(self, 'sysName'):
            self.sysName = None

        for oid in self._snmpwalk(oid_astuple):
            self.sysName = oid

    def setattr_ipadentifindex(self):
        """
        snmp walk 1.3.6.1.2.1.4.20.1.2
        1.3.6.1.2.1.4.20.1.2 = RFC1213-MIB::ipAdEntIfIndex
        """
        oid_astuple = (1, 3, 6, 1, 2, 1, 4, 20, 1, 2)

        if not hasattr(self, 'ipAdEntIfIndex'):
            self.ipAdEntIfIndex = list()

        for oid in self._snmpwalk(oid_astuple):
            self.ipAdEntIfIndex.append(oid)

    def setattr_ipadentaddr(self):
        """
        snmp walk 1.3.6.1.2.1.4.20.1.1
        1.3.6.1.2.1.4.20.1.1 = RFC1213-MIB::ipAdEntAddr
        """
        oid_astuple = (1, 3, 6, 1, 2, 1, 4, 20, 1, 1)

        if not hasattr(self, 'ipAdEntAddr'):
            self.ipAdEntAddr = list()

        for oid in self._snmpwalk(oid_astuple):
            self.ipAdEntAddr.append(oid)

    def setattr_ipadentnetmask(self):
        """
        snmp walk 1.3.6.1.2.1.4.20.1.3
        1.3.6.1.2.1.4.20.1.3 = RFC1213-MIB::ipAdEntNetMask
        """
        oid_astuple = (1, 3, 6, 1, 2, 1, 4, 20, 1, 3)

        if not hasattr(self, 'ipAdEntNetMask'):
            self.ipAdEntNetMask = list()

        for oid in self._snmpwalk(oid_astuple):
            self.ipAdEntNetMask.append(oid)

    def setattr_ifalias(self):
        """
        snmp walk 1.3.6.1.2.1.31.1.1.1.18
        1.3.6.1.2.1.31.1.1.1.18 = IF-MIB::ifAlias
        """
        oid_astuple = (1, 3, 6, 1, 2, 1, 31, 1, 1, 1, 18)

        if not hasattr(self, 'ifAlias'):
            self.ifAlias = list()

        for oid in self._snmpwalk(oid_astuple):
            self.ifAlias.append(oid)

    def setattr_ifname(self):
        """
        snmp walk 1.3.6.1.2.1.31.1.1.1.1
        1.3.6.1.2.1.31.1.1.1.1 = IF-MIB::ifName
        """
        oid_astuple = (1, 3, 6, 1, 2, 1, 31, 1, 1, 1, 1)

        if not hasattr(self, 'ifName'):
            self.ifName = list()

        for oid in self._snmpwalk(oid_astuple):
            self.ifName.append(oid)

    def setattr_ifdescr(self):
        """
        snmp walk 1.3.6.1.2.1.2.2.1.2
        1.3.6.1.2.1.2.2.1.2 = IF-MIB::ifDescr
        """
        oid_astuple = (1, 3, 6, 1, 2, 1, 2, 2, 1, 2)

        if not hasattr(self, 'ifDescr'):
            self.ifDescr = list()

        for oid in self._snmpwalk(oid_astuple):
            self.ifDescr.append(oid)

    def setattr_entphysicalserialnum(self):
        """
        snmp walk 1.3.6.1.2.1.47.1.1.1.1.11
        1.3.6.1.2.1.47.1.1.1.1.11 = ENTITY-MIB::entPhysicalSerialNum
        """
        oid_astuple = (1, 3, 6, 1, 2, 1, 47, 1, 1, 1, 1, 11)

        if not hasattr(self, 'entPhysicalSerialNum'):
            self.entPhysicalSerialNum = list()

        for oid in self._snmpwalk(oid_astuple):
            self.entPhysicalSerialNum.append(oid)

    def setattr_entphysicalmodelname(self):
        """
        snmp walk 1.3.6.1.2.1.47.1.1.1.1.13
        1.3.6.1.2.1.47.1.1.1.1.13 = ENTITY-MIB::entPhysicalModelName
        """
        oid_astuple = (1, 3, 6, 1, 2, 1, 47, 1, 1, 1, 1, 13)

        if not hasattr(self, 'entPhysicalModelName'):
            self.entPhysicalModelName = list()

        for oid in self._snmpwalk(oid_astuple):
            self.entPhysicalModelName.append(oid)

    def setattr_cvvrfinterfacerowstatus(self):
        """
        snmp walk 1.3.6.1.4.1.9.9.711.1.2.1.1.5
        1.3.6.1.4.1.9.9.711.1.2.1.1.5 = ciscoVrfMIB::cvVrfInterfaceRowStatus
        """
        oid_astuple = (1, 3, 6, 1, 4, 1, 9, 9, 711, 1, 2, 1, 1, 5)

        if not hasattr(self, 'cvVrfInterfaceRowStatus'):
            self.cvVrfInterfaceRowStatus = list()

        for oid in self._snmpwalk(oid_astuple):
            self.cvVrfInterfaceRowStatus.append(oid)

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
        return '<{}(host={}, snmp_community={}, sysName={})'.format(self.__class__.__name__, self.host,
                                                                    self.snmp_community,
                                                                    self.get_hostname)
