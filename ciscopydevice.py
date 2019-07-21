# -*- coding: utf-8 -*-
from .ciscopyconf import CiscoPyConf, CiscoPyNetwork
from .ciscopyinterface import ipaddress
from .ciscopysnmp import CiscoPySNMP, SnmpObjId


class CiscoPyDevice:
    def __init__(self, host_ip, host_name, snmp_community, ssh_username, ssh_password, enable_secret='cisco',
                 mpmodel=1):
        self.host_ip = ipaddress.IPv4Address(host_ip)
        self.host_name = host_name
        self.snmp_community = snmp_community
        self.ssh_username: str = ssh_username
        self.ssh_password: str = ssh_password
        self.enable_secret: str = enable_secret
        self.cpnetwork = CiscoPyNetwork()
        self.cpsnmp = CiscoPySNMP(host_ip, snmp_community=self.snmp_community, mpmodel=mpmodel)
        self.deviceclass: str = ''
        self.oid_index: str = ''
        self.serial_number: str = ''
        self.model_name: str = ''
        self.os_version: str = ''
        self.all_interfaces: list = list()
        self.physical_interfaces: list = list()
        self.virtual_interfaces: list = list()

        if self.cpnetwork.reachable(str(self.host_ip)):
            self.cpnetwork.status = True
        #     self.set_all_attr_values()
            self.cpconf = CiscoPyConf()
        #     self.cpconf.conf_fromdevice(self.host_ip,
        #                                 self.host_name,
        #                                 ssh_username=self.ssh_username,
        #                                 ssh_password=self.ssh_password)

    def get_ifindex(self, interface: str) -> str:
        oid_index = None
    
        if not self.cpsnmp.ifDescr:
            self.cpsnmp.setattr_ifdescr()
    
        if not self.cpsnmp.ifDescr:
            raise ValueError('Unable to snmp walk ifDescr of {}, {}'.format(self.host_ip, self.host_name))
    
        for snmpobjid in self.cpsnmp.ifDescr:
            if interface == snmpobjid.oid_value:
                oid_index = snmpobjid.oid_index
    
        return oid_index

    def get_ifip(self, interface: str) -> ipaddress.IPv4Interface:
        ipv4interface = None
        ip_address = None
        
        self.cpsnmp.setattr_ipadentifindex()
        if not self.cpsnmp.ipAdEntIfIndex:
            value_err_msg = 'Unable to snmp walk ipAdEntIfIndex of {}, {}'
            raise ValueError(value_err_msg.format(self.host_ip, self.host_name))
        
        self.cpsnmp.setattr_ipadentaddr()
        if not self.cpsnmp.ipAdEntAddr:
            value_err_msg = 'Unable to snmp walk ipAdEntAddr of {}, {}'
            raise ValueError(value_err_msg.format(self.host_ip, self.host_name))
        
        self.cpsnmp.setattr_ipadentnetmask()
        if not self.cpsnmp.ipAdEntNetMask:
            value_err_msg = 'Unable to snmp walk ipAdEntNetMask of {}, {}'
            raise ValueError(value_err_msg.format(self.host_ip, self.host_name))

        for snmpobjid in self.cpsnmp.ipAdEntIfIndex:
            if snmpobjid.oid_value == self.get_ifindex(interface):
                ip_address = snmpobjid.oid_index
    
        for ipadentaddr, ipadentnetmask in zip(self.cpsnmp.ipAdEntAddr, self.cpsnmp.ipAdEntNetMask):
            if ipadentaddr.oid_index == ip_address:
                ipv4interface = ipaddress.IPv4Interface('{}/{}'.format(ipadentaddr.oid_index, ipadentnetmask.oid_value))
    
        if ipv4interface is None:
            raise ValueError('`IPv4Interface` error: device {}, {},  interface {}'.format(self.host_ip,
                                                                                          self.host_name,
                                                                                          interface))
        else:
            return ipv4interface

    def get_ifalias(self, interface: str) -> str:
        ifindex = self.get_ifindex(interface)
        ifalias = ''
        
        self.cpsnmp.setattr_ifalias()
        if not self.cpsnmp.ifAlias:
            raise ValueError('Method get_ifalias() fail: unable to set instance attribute ifAlias.')
    
        for snmpobjid in self.cpsnmp.ifAlias:
            if snmpobjid.oid_index == ifindex:
                ifalias = snmpobjid.oid_value
    
        return ifalias

    def get_ifvrfname(self, interface: str) -> str:
        ifvrfname = ''
    
        cvvrfname_oid_astuple = (1, 3, 6, 1, 4, 1, 9, 9, 711, 1, 1, 1, 1, 2)
        
        self.cpsnmp.setattr_cvvrfinterfacerowstatus()
        if self.cpsnmp.cvVrfInterfaceRowStatus is None:
            value_err_msg = 'Unable to snmp walk cvVrfInterfaceRowStatus of {}, {}'
            raise ValueError(value_err_msg.format(self.host_ip, self.host_name))
    
        for snmpobjid in self.cpsnmp.cvVrfInterfaceRowStatus:
            if snmpobjid.oid_index.split('.')[-1] == self.get_ifindex(interface):
                res_oid_index_aslist = list(snmpobjid.oid_index_astuple)
                res_oid_index_aslist.pop(-1)
                req_oid_astuple = cvvrfname_oid_astuple + tuple(res_oid_index_aslist)
                for snmpobjid_ in self.cpsnmp.snmpwalk(req_oid_astuple):
                    ifvrfname = snmpobjid_.oid_value
    
        return ifvrfname

    def get_hostname(self) -> str:
        self.cpsnmp.setattr_sysname()
        if self.cpsnmp.sysName is None:
            value_err_msg = 'Unable to snmp get sysName.0 of {}, {}'
            raise ValueError(value_err_msg.format(self.host_ip, self.host_name))
    
        return self.cpsnmp.sysName.oid_value.split('.')[0]

    @staticmethod
    def _normalise_interfacename(interface):
        if interface.startswith('Lo'):
            return interface.lower()
        elif interface.startswith('Et'):
            return interface.lower()
        elif interface.startswith('Fa'):
            return interface.lower().replace('a', 'e')
        elif interface.startswith('Gi'):
            return interface.lower().replace('i', 'e')
        elif interface.startswith('Te'):
            return interface.lower()

    def setattr_deviceclass(self):
        self.cpsnmp.setattr_entlogicaltype()
        self.cpsnmp.setattr_entphysicalserialnum()
        self.cpsnmp.setattr_entphysicalmodelname()
        self.cpsnmp.setattr_entphysicalsoftwarerev()
        self.cpsnmp.setattr_entphysicaldescr()
        self.cpsnmp.setattr_cswmaxswitchnum()
        self.cpsnmp.setattr_cswswitchnumcurrent()
        self.cpsnmp.setattr_cswswitchrole()
        self.cpsnmp.setattr_cswswitchstate()
        self.cpsnmp.setattr_cvsswitchmode()
        self.cpsnmp.setattr_cvschassisswitchid()
        self.cpsnmp.setattr_cvschassisrole()
        self.cpsnmp.setattr_cvsmoduleslotnumber()

        if not self.cpsnmp.entLogicalType:
            self.deviceclass = 'Unknown'

        if not all(isinstance(v, SnmpObjId) for v in self.cpsnmp.entLogicalType):
            raise TypeError('Not all attribute `entLogicalType` list elements are type `SnmpObjId`')

        entlogicaltype_set = set([snmpobjid.oid_value for snmpobjid in self.cpsnmp.entLogicalType])

        if ('1.3.6.1.2.1' in entlogicaltype_set) or ('mib-2' in entlogicaltype_set):
            self.deviceclass = 'IP Router'
            self.__class__ = CiscoPyRouter
            self.oid_index = '1'
        elif (('1.3.6.1.2.1' not in entlogicaltype_set and 'mib-2' not in entlogicaltype_set) and
              ('1.3.6.1.2.1.17' in entlogicaltype_set or 'dot1dBridge' in entlogicaltype_set)):
            if hasattr(self.cpsnmp.cvsSwitchMode, 'oid_value') and self.cpsnmp.cvsSwitchMode.oid_value == '1':
                self.deviceclass = 'Switch'
                self.__class__ = CiscoPySwitch
            
            if hasattr(self.cpsnmp.cvsSwitchMode, 'oid_value') and self.cpsnmp.cvsSwitchMode.oid_value == '2':
                self.deviceclass = 'Virtual Switch System'
                for snmpobjid in self.cpsnmp.cvsChassisSwitchID:
                    if int(snmpobjid.oid_value) is 1:
                        self.deviceclass = 'Virtual Switch System'
                        self.__class__ = CiscoPyVSSMember
                        self.oid_index = snmpobjid.oid_index
                        setattr(self, 'ent_oid_index', '1000')
                        break

            if hasattr(self.cpsnmp.cswMaxSwitchNum, 'oid_value'):
                if int(self.cpsnmp.cswMaxSwitchNum.oid_value) is 1:
                    self.deviceclass = 'Standalone'
                    self.__class__ = CiscoPySwitch
                    for snmpobjid in self.cpsnmp.cswSwitchNumCurrent:
                        if int(snmpobjid.oid_value) is 1:
                            self.oid_index = snmpobjid.oid_index

            if hasattr(self.cpsnmp.cswMaxSwitchNum, 'oid_value'):
                if int(self.cpsnmp.cswMaxSwitchNum.oid_value) > 1:
                    for snmpobjid in self.cpsnmp.cswSwitchRole:
                        if int(snmpobjid.oid_value) is 1:
                            self.deviceclass = 'Switch Stack Master'
                            self.__class__ = CiscoPySwitchStackMaster
                            self.oid_index = snmpobjid.oid_index

            if (not hasattr(self.cpsnmp.cswMaxSwitchNum, 'oid_value') and
                    not hasattr(self.cpsnmp.cvsSwitchMode, 'oid_value')):
                self.deviceclass = 'Switch'
        
    def __repr__(self):
        repr_string = '<{}(host_ip={}, host_name={}, oid_index={}, model_name={}, os_version={}, serial_number={})>'
        return repr_string.format(self.__class__.__name__, self.host_ip, self.host_name, self.oid_index,
                                  self.model_name, self.os_version, self.serial_number)


class CiscoPyRouter(CiscoPyDevice):
    @property
    def serial_number(self):
        for snmpobjid in self.cpsnmp.entPhysicalSerialNum:
            if snmpobjid.oid_index == '1':
                return snmpobjid.oid_value
    
    @property
    def model_name(self):
        for snmpobjid in self.cpsnmp.entPhysicalModelName:
            if snmpobjid.oid_index == '1':
                return snmpobjid.oid_value
    
    @property
    def os_version(self):
        for snmpobjid in self.cpsnmp.entPhysicalSoftwareRev:
            if snmpobjid.oid_index == '1' and snmpobjid.oid_value:
                return snmpobjid.oid_value.strip().split()[0].strip(',')
            else:
                for snmpobjid_a in self.cpsnmp.entPhysicalDescr:
                    if 'Route Processor' in snmpobjid_a.oid_value:
                        oid_index = snmpobjid_a.oid_index
                        for snmpobjid_b in self.cpsnmp.entPhysicalSoftwareRev:
                            if oid_index == snmpobjid_b.oid_index:
                                return snmpobjid_b.oid_value
    

class CiscoPySwitch(CiscoPyDevice):
    @property
    def switch_number(self):
        for snmpobjid in self.cpsnmp.cswSwitchNumCurrent:
            if self.oid_index == snmpobjid.oid_index:
                return snmpobjid.oid_value
    
    @property
    def switch_role(self):
        for snmpobjid in self.cpsnmp.cswSwitchRole:
            if self.oid_index == snmpobjid.oid_index:
                if int(snmpobjid.oid_value) is 1:
                    return 'master'
                elif int(snmpobjid.oid_value) is 2:
                    return 'member'
                elif int(snmpobjid.oid_value) is 3:
                    return 'notMember'
                elif int(snmpobjid.oid_value) is 4:
                    return 'standby'
                else:
                    return 'unknown'

    @property
    def serial_number(self):
        for snmpobjid in self.cpsnmp.entPhysicalSerialNum:
            if self.oid_index == snmpobjid.oid_index:
                return snmpobjid.oid_value
    
    @property
    def model_name(self):
        for snmpobjid in self.cpsnmp.entPhysicalModelName:
            if self.oid_index == snmpobjid.oid_index:
                return snmpobjid.oid_value
    
    @property
    def os_version(self):
        for snmpobjid in self.cpsnmp.entPhysicalSoftwareRev:
            if self.oid_index == snmpobjid.oid_index:
                return snmpobjid.oid_value.split()[-1]
    
    def __repr__(self):
        repr_string = '<{}(host_ip={}, host_name={}, oid_index={}, model_name={}, switch_number={}, switch_role={}, ' \
                      'os_version={}, serial_number={})>'
        return repr_string.format(self.__class__.__name__, self.host_ip, self.host_name, self.oid_index,
                                  self.model_name, self.switch_number, self.switch_role, self.os_version,
                                  self.serial_number)


class CiscoPySwitchStack(list):
    pass


class CiscoPySwitchStackMaster(CiscoPySwitch):
    pass


class CiscoPySwitchStackMember(CiscoPySwitch):
    pass


class CiscoPyVSS(list):
    pass


class CiscoPyVSSMember(CiscoPySwitch):
    @property
    def chassis_switch_id(self):
        for snmpobjid in self.cpsnmp.cvsChassisSwitchID:
            if self.oid_index == snmpobjid.oid_index:
                return snmpobjid.oid_value

    @property
    def chassis_role(self):
        for snmpobjid in self.cpsnmp.cvsChassisRole:
            if self.oid_index == snmpobjid.oid_index:
                if int(snmpobjid.oid_value) == 2:
                    return 'active'
                elif int(snmpobjid.oid_value) == 3:
                    return 'standby'
                else:
                    return 'standalone'

    ent_oid_index = ''

    def __repr__(self):
        repr_string = '<{}(host_ip={}, host_name={}, oid_index={}, ent_oid_index={}, model_name={}, ' \
                      'chassis_switch_id={}, chassis_switch_role={}, os_version={}, serial_number={}'

        return repr_string.format(self.__class__.__name__, self.host_ip, self.host_name, self.oid_index,
                                  self.ent_oid_index, self.model_name, self.chassis_switch_id, self.chassis_role,
                                  self.os_version, self.serial_number)
