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

from itertools import zip_longest
from pysnmp.entity.rfc3413.oneliner import cmdgen


class SnmpObjId:
    __slots__ = ['request_oid_astuple', 'request_oid_asstring', 'result_oid_astuple', 'result_oid_asstring', 'oid',
                 'oid_index_astuple', 'oid_index', 'oid_value']

    def __init__(self, **kwargs):
        self.request_oid_astuple: tuple = kwargs.get('request_oid_astuple', tuple())
        self.request_oid_asstring: str = '.'.join([str(x) for x in self.request_oid_astuple])
        self.result_oid_astuple: tuple = kwargs.get('result_oid_astuple', tuple())
        self.result_oid_asstring = '.'.join([str(x) for x in self.result_oid_astuple])
        self.oid_value: str = kwargs.get('result_oid_value_asstring', '')
        self.oid_index = ''

        if self.request_oid_astuple and self.result_oid_astuple:
            self._find_oid_index()
            # self.oid_index: str = '.'.join([str(x) for x in self.oid_index_astuple])
        # else:
        #     self.oid_index_astuple: tuple = tuple()
        #     self.oid_index: str = '.'.join([str(x) for x in self.oid_index_astuple])

    def _find_oid_index(self):
        if self.request_oid_astuple == self.result_oid_astuple:
            self.oid_index = self.result_oid_astuple[-1],
        else:
            oid_index = '.'.join([str(y) for x, y in
                                  zip_longest(self.request_oid_astuple, self.result_oid_astuple) if not x == y])
            self.oid_index = oid_index

    def __repr__(self):
        oid = ''
        if self.request_oid_astuple and self.result_oid_astuple:
            if self.request_oid_astuple == self.result_oid_astuple:
                oid = '.'.join(self.result_oid_asstring.split('.')[0:-1])
            else:
                oid = self.request_oid_asstring
            
            # self._find_oid_index()

        repr_string = '<{}(full_oid={}, oid={}, oid_index={}, oid_value={})>'

        return repr_string.format(self.__class__.__name__, self.result_oid_asstring, oid, self.oid_index,
                                  self.oid_value)


class CiscoPySNMP:
    def __init__(self, host_ip, snmp_community, mpmodel=1):
        self.host_ip: str = host_ip
        self.snmp_community: str = snmp_community
        self.mpmodel: int = mpmodel
        self.ipAdEntIfIndex: list = list()
        self.entLogicalType: list = list()
        self.sysName: SnmpObjId = SnmpObjId()
        self.ipAdEntAddr: list = list()
        self.ipAdEntNetMask: list = list()
        self.ifDescr: list = list()
        self.ifName: list = list()
        self.ifAlias: list = list()
        self.ifAdminStatus: list = list()
        self.ifOperStatus: list = list()
        self.ifPhysAddress: list = list()
        self.ifSpeed: list = list()
        self.vlanTrunkPortDynamicState: list = list()
        self.entPhysicalMfgName = list()
        self.entPhysicalSerialNum = list()
        self.entPhysicalModelName = list()
        self.entPhysicalSoftwareRev = list()
        self.entPhysicalDescr = list()
        self.cvVrfInterfaceRowStatus = list()
        self.cswMaxSwitchNum: SnmpObjId = SnmpObjId()
        self.cswSwitchNumCurrent = list()
        self.cswSwitchState = list()
        self.cswSwitchRole = list()
        self.cvsSwitchMode = 'Standalone'
        self.cvsChassisSwitchID = list()
        self.cvsChassisRole = list()
        self.cvsModuleSlotNumber = list()
        self.command_generator = cmdgen.CommandGenerator()
        self.snmp_engine = cmdgen.SnmpEngine()
        self.auth_data = cmdgen.CommunityData(self.snmp_community, mpModel=self.mpmodel)
        self.transport_target = cmdgen.UdpTransportTarget((self.host_ip, 161), timeout=10.0, retries=1)

    def __hasattribute(self, attribute):
        if not hasattr(self, attribute):
            return False
        else:
            return True

    def snmpwalk(self, oid_astuple: tuple):
        if not isinstance(oid_astuple, tuple):
            error_message = 'Method `snmpwalk`: Parameter `oid_astuple` error: parameter is not type `tuple`.'
            raise TypeError(error_message)
        
        if not all(isinstance(v, int) for v in oid_astuple):
            error_message = 'Method `snmpwalk`: Parameter `oid_astuple` error: not all elements are type `int`.'
            raise TypeError(error_message)
    
        request_oid_astuple = oid_astuple
        mib_variable = cmdgen.MibVariable(request_oid_astuple)

        (error_indication,
         error_status,
         error_index,
         varbinds) = self.command_generator.bulkCmd(self.auth_data, self.transport_target, 0, 25, mib_variable,
                                                    lookupMib=False, lexicographicMode=False,
                                                    ignoreNonIncreasingOid=True)
        
        if error_indication:
            error_message = 'Method `snmpwalk`: error indication: {}'
            raise AssertionError(error_message.format(error_indication))
        elif error_status:
            error_message = 'Method `snmpwalk`: Error status: {} {}'
            raise AssertionError(error_message.format(error_status.prettyPrint(),
                                                      error_index and varbinds[int(error_index)-1][0] or '?'))
        else:
            for varbind in varbinds:
                for oid, oid_value in varbind:
                    result_oid_asstring = oid.prettyPrint()
                    result_oid_astuple = tuple([int(v) for v in result_oid_asstring.split('.')])
                    result_oid_value_asstring = oid_value.prettyPrint()
                    yield SnmpObjId(request_oid_astuple=request_oid_astuple,
                                    result_oid_astuple=result_oid_astuple,
                                    result_oid_value_asstring=result_oid_value_asstring)

    def snmpget(self, oid_astuple: tuple):
        if not isinstance(oid_astuple, tuple):
            error_message = 'Method `snmpget`: Parameter `oid_astuple` error: parameter is not type `tuple`.'
            raise TypeError(error_message)
    
        if not all(isinstance(v, int) for v in oid_astuple):
            error_message = 'Method `snmpget`: Parameter `oid_astuple` error: not all elements are type `int`.'
            raise TypeError(error_message)
    
        request_oid_astuple = oid_astuple
        mib_variable = cmdgen.MibVariable(request_oid_astuple)
        
        (error_indication,
         error_status,
         error_index,
         varbinds) = self.command_generator.getCmd(self.auth_data, self.transport_target, mib_variable)

        if error_indication:
            error_message = 'Method `snmpget`: Error indication: {}'
            raise AssertionError(error_message.format(error_indication))
        elif error_status:
            error_message = 'Method `snmpget`: Error status: {} {}'
            raise AssertionError(error_message.format(error_status.prettyPrint(),
                                                      error_index and varbinds[int(error_index)-1][0] or '?'))
        else:
            for varbind in varbinds:
                for oid, oid_value in varbind:
                    result_oid_asstring = oid.prettyPrint()
                    result_oid_astuple = tuple([int(v) for v in result_oid_asstring.split('.')])
                    result_oid_value_asstring = oid_value.prettyPrint()
                    yield SnmpObjId(request_oid_astuple=request_oid_astuple,
                                    result_oid_astuple=result_oid_astuple,
                                    result_oid_value_asstring=result_oid_value_asstring)

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

    def setattr_ifadminstatus(self):
        """
        snmp walk 1.3.6.1.2.1.2.2.1.7
        1.3.6.1.2.1.2.2.1.7 = IF-MIB::ifAdminStatus
        """
        oid_astuple = (1, 3, 6, 1, 2, 1, 2, 2, 1, 7)

        if self.ifAdminStatus:
            self.ifAdminStatus = list()

        for snmpobjid in self.snmpwalk(oid_astuple):
            self.ifAdminStatus.append(snmpobjid)

    def setattr_ifoperstatus(self):
        """
        snmp walk 1.3.6.1.2.1.2.2.1.8
        1.3.6.1.2.1.2.2.1.7 = IF-MIB::ifOperStatus
        """
        oid_astuple = (1, 3, 6, 1, 2, 1, 2, 2, 1, 8)

        if self.ifOperStatus:
            self.ifOperStatus = list()

        for snmpobjid in self.snmpwalk(oid_astuple):
            self.ifOperStatus.append(snmpobjid)

    def setattr_ifphysaddress(self):
        """
        snmp walk 1.3.6.1.2.1.2.2.1.6
        1.3.6.1.2.1.2.2.1.6 = IF-MIB::ifHighSpeed
        """
        oid_astuple = (1, 3, 6, 1, 2, 1, 2, 2, 1, 6)

        if self.ifPhysAddress:
            self.ifPhysAddress = list()

        for snmpobjid in self.snmpwalk(oid_astuple):
            self.ifPhysAddress.append(snmpobjid)

    def setattr_ifspeed(self):
        """
        snmp walk 1.3.6.1.2.1.31.1.1.1.15
        1.3.6.1.2.1.2.2.1.7 = IF-MIB::ifHighSpeed
        """
        oid_astuple = (1, 3, 6, 1, 2, 1, 31, 1, 1, 1, 15)

        if self.ifSpeed:
            self.ifSpeed = list()

        for snmpobjid in self.snmpwalk(oid_astuple):
            self.ifSpeed.append(snmpobjid)

    def setattr_vlantrunkportdynamicstate(self):
        """
        snmp walk 1.3.6.1.4.1.9.9.46.1.6.1.1.13
        1.3.6.1.4.1.9.9.46.1.6.1.1.13 = CISCO-VTP-MIB::vlanTrunkPortDynamicState
        """
        oid_astuple = (1, 3, 6, 1, 4, 1, 9, 9, 46, 1, 6, 1, 1, 13)

        if self.vlanTrunkPortDynamicState:
            self.vlanTrunkPortDynamicState = list()

        for snmpobjid in self.snmpwalk(oid_astuple):
            self.vlanTrunkPortDynamicState.append(snmpobjid)

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
