# -*- coding: utf-8 -*-
import re
import netaddr
from .ciscopyconf import CiscoPyConf, CiscoPyNetwork
from .ciscopyinterface import CiscoPyInterfaces, CiscoPyInterface
from .ciscopyinterface.ipaddress import ip_address
from .ciscopysnmp import CiscoPySNMP, SnmpObjId


class CiscoPyDevice:
    def __init__(self, obtac_host_ip, obtac_host_name, snmp_community, ssh_username, ssh_password, nat_router_ip,
                 enable_secret='cisco', mpmodel=1):
        self.obtac_host_ip = ip_address(obtac_host_ip)
        self.real_host_ip = ip_address(0)
        self.obtac_host_name = obtac_host_name
        self.real_host_name = ''
        self.snmp_community = snmp_community
        self.ssh_username: str = ssh_username
        self.ssh_password: str = ssh_password
        self.enable_secret: str = enable_secret
        self.cpnetwork = CiscoPyNetwork()
        self.cpsnmp = CiscoPySNMP(self.obtac_host_ip.compressed, snmp_community=self.snmp_community, mpmodel=mpmodel)
        self.deviceclass: str = ''
        self.oid_index: str = ''
        self.serial_number: str = ''
        self.model_name: str = ''
        self.os_version: str = ''
        self.all_interfaces: list = CiscoPyInterfaces()
        self.physical_interfaces: list = list()
        self.virtual_interfaces: list = list()
        self.nat_router_ip = ip_address(nat_router_ip)

        if self.cpnetwork.reachable(self.obtac_host_ip.compressed):
            self.cpnetwork.status = True
        #     self.set_all_attr_values()
            self.cpconf = CiscoPyConf()
        #     self.cpconf.conf_fromdevice(self.host_ip,
        #                                 self.host_name,
        #                                 ssh_username=self.ssh_username,
        #                                 ssh_password=self.ssh_password)

    @staticmethod
    def _character_convert(character: str):
        try:
            return int(character)
        except ValueError:
            return character
    
    def _alphanumeric_key(self, interface_object):
        return [self._character_convert(character) for character in re.split('([0-9]+)', interface_object.name)]
    
    def _interface_sort(self):
        if self.all_interfaces:
            self.all_interfaces.sort(key=self._alphanumeric_key)

    def setattr_interface_name(self):
        for ifdescr_snmpobjid in self.cpsnmp.ifDescr:
            if (
                    re.match(r'^Ether.*?\d$', ifdescr_snmpobjid.oid_value) or
                    re.match(r'^FastEthernet.*?\d$', ifdescr_snmpobjid.oid_value) or
                    re.match(r'^GigabitEthernet.*?\d$', ifdescr_snmpobjid.oid_value) or
                    re.match(r'^TenGigabitEthernet.*?\d$', ifdescr_snmpobjid.oid_value) or
                    re.match(r'^Vlan\d{1,4}$', ifdescr_snmpobjid.oid_value) or
                    re.match(r'^Loopback\d{1,4}$', ifdescr_snmpobjid.oid_value)):
                interface = CiscoPyInterface(name=ifdescr_snmpobjid.oid_value,
                                             oid_index=ifdescr_snmpobjid.oid_index)
                self.all_interfaces.append(interface)

    def setattr_interface_shortname(self):
        for interface in self.all_interfaces:
            for ifname_snmpobjid in self.cpsnmp.ifName:
                if interface.oid_index == ifname_snmpobjid.oid_index:
                    interface.short_name = ifname_snmpobjid.oid_value

    def setattr_interface_description(self):
        for interface in self.all_interfaces:
            for ifalias_snmpobjid in self.cpsnmp.ifAlias:
                if interface.oid_index == ifalias_snmpobjid.oid_index:
                    interface.description = ifalias_snmpobjid.oid_value

    def setattr_interface_adminstatus(self):
        for interface in self.all_interfaces:
            for ifadminstatus_snmpobjid in self.cpsnmp.ifAdminStatus:
                if interface.oid_index == ifadminstatus_snmpobjid.oid_index:
                    if int(ifadminstatus_snmpobjid.oid_value) is 1:
                        interface.admin_status = 'up'
                    elif int(ifadminstatus_snmpobjid.oid_value) is 2:
                        interface.admin_status = 'down'
                    elif int(ifadminstatus_snmpobjid.oid_value) is 3:
                        interface.admin_status = 'testing'
                    else:
                        interface.admin_status = 'unknown'

    def setattr_interface_operationalstatus(self):
        for interface in self.all_interfaces:
            for ifoperstatus_snmpobjid in self.cpsnmp.ifOperStatus:
                if interface.oid_index == ifoperstatus_snmpobjid.oid_index:
                    if int(ifoperstatus_snmpobjid.oid_value) is 1:
                        interface.operational_status = 'up'
                    elif int(ifoperstatus_snmpobjid.oid_value) is 2:
                        interface.operational_status = 'down'
                    elif int(ifoperstatus_snmpobjid.oid_value) is 3:
                        interface.operational_status = 'testing'
                    elif int(ifoperstatus_snmpobjid.oid_value) is 5:
                        interface.operational_status = 'dormant'
                    elif int(ifoperstatus_snmpobjid.oid_value) is 6:
                        interface.operational_status = 'notPresent'
                    elif int(ifoperstatus_snmpobjid.oid_value) is 7:
                        interface.operational_status = 'lowerLayerDown'
                    else:
                        interface.operational_status = 'unknown'

    def setattr_interface_physicaladdress(self):
        for interface in self.all_interfaces:
            for ifphysaddr_snmpobjid in self.cpsnmp.ifPhysAddress:
                if interface.oid_index == ifphysaddr_snmpobjid.oid_index:
                    try:
                        mac_address_asint = int(ifphysaddr_snmpobjid.oid_value, base=16)
                    except ValueError:
                        mac_address_asint = 0
                    mac_addr_aseui = netaddr.EUI(mac_address_asint, dialect=netaddr.mac_unix_expanded())
                    mac_addr = mac_addr_aseui
                    interface.physical_address = mac_addr

    def setattr_interface_speed(self):
        for interface in self.all_interfaces:
            for ifspeed_snmpobjid in self.cpsnmp.ifSpeed:
                if interface.oid_index == ifspeed_snmpobjid.oid_index:
                    interface.speed = ifspeed_snmpobjid.oid_value

    def setattr_interface_vlantrunkportdynamicstate(self):
        for interface in self.all_interfaces:
            for vlantrunkportdynamicstate_snmpobjid in self.cpsnmp.vlanTrunkPortDynamicState:
                if interface.oid_index == vlantrunkportdynamicstate_snmpobjid.oid_index:
                    if int(vlantrunkportdynamicstate_snmpobjid.oid_value) is 1:
                        interface.trunking = True

    def setattr_interface_ipaddress(self):
        for interface in self.all_interfaces:
            for ipadentifindex in self.cpsnmp.ipAdEntIfIndex:
                if interface.oid_index == ipadentifindex.oid_value:
                    interface.ip_address = self.get_ifip(interface.name)

    def setattr_real_host_ip(self):
        """
        set the real host ip of a device.
        
        A bit of recursion is required in the case of network address
        translation relative to OBTAC.
        
        In a LAN environment where an extranet address is used directly on an
        interface or a network address translation is performed and the
        interface description is strictly adhered to, finding the real host ip
        is straight forward.
        
        The problem arises when a network address translation is performed and
        and there is no way to identify the real host ip interface of a device
        if the device has multiple layer 3 interfaces. For example, the
        Cisco Identity Services Engine (ISE).
        
        The only way that will work looks to be to supply the obtac extranet
        address of the wan router at the location of this device.
        """
        for interface in self.all_interfaces:
            if self.obtac_host_ip.compressed == interface.ip_address.ip.compressed:
                # self.obtac_host_ip = interface.ip_address
                self.real_host_ip = interface.ip_address
                return
        
        for interface in self.all_interfaces:
            if interface.description == '*** EMC Management Interface ***':
                self.real_host_ip = interface.ip_address
                return
        
        cpconf = CiscoPyConf()
        cpconf.conf_fromdevice(self.nat_router_ip.compressed, '', self.ssh_username, self.ssh_password)
        for ipnatinside_conf in cpconf.include('^ip nat inside'):
            if self.obtac_host_ip.compressed in ipnatinside_conf:
                real_host_ip = ipnatinside_conf.strip().split()[-4]
                for interface in self.all_interfaces:
                    if real_host_ip in interface.ip_address.compressed:
                        self.real_host_ip = interface.ip_address
                        return

    def setattr_all_interfaces(self):
        self.all_interfaces = CiscoPyInterfaces()
    
        self.cpsnmp.populate_ifdescr()
        self.cpsnmp.populate_ifname()
        self.cpsnmp.populate_ifalias()
        self.cpsnmp.populate_ifadminstatus()
        self.cpsnmp.populate_ifoperstatus()
        self.cpsnmp.populate_ifphysaddress()
        self.cpsnmp.populate_ifspeed()
        self.cpsnmp.populate_vlantrunkportdynamicstate()
        self.cpsnmp.populate_ipadentifindex()
        self.cpsnmp.populate_ipadentaddr()
        self.cpsnmp.populate_ipadentnetmask()
        
        if not self.cpsnmp.ifDescr:
            error_string = 'snmpwalk of ifDescr failed: obtac_host_ip={}, obtac_host_name={}.'
            raise ValueError(error_string.format(self.obtac_host_ip, self.obtac_host_name))
        
        if not self.cpsnmp.ifName:
            error_string = 'snmpwalk of ifName failed: obtac_host_ip={}, obtac_host_name={}.'
            raise ValueError(error_string.format(self.obtac_host_ip, self.obtac_host_name))
        
        if not self.cpsnmp.ifAlias:
            error_string = 'snmpwalk of ifAlias failed: obtac_host_ip={}, obtac_host_name={}.'
            raise ValueError(error_string.format(self.obtac_host_ip, self.obtac_host_name))
        
        if not self.cpsnmp.ifAdminStatus:
            error_string = 'snmpwalk of ifAdminStatus failed: obtac_host_ip={}, obtac_host_name={}.'
            raise ValueError(error_string.format(self.obtac_host_ip, self.obtac_host_name))

        if not self.cpsnmp.ifOperStatus:
            error_string = 'snmpwalk of ifOperStatus failed: obtac_host_ip={}, obtac_host_name={}.'
            raise ValueError(error_string.format(self.obtac_host_ip, self.obtac_host_name))

        if not self.cpsnmp.ifPhysAddress:
            error_string = 'snmpwalk of ifPhysAddress failed: obtac_host_ip={}, obtac_host_name={}.'
            raise ValueError(error_string.format(self.obtac_host_ip, self.obtac_host_name))

        if not self.cpsnmp.ifSpeed:
            error_string = 'snmpwalk of ifSpeed failed: obtac_host_ip={}, obtac_host_name={}.'
            raise ValueError(error_string.format(self.obtac_host_ip, self.obtac_host_name))
        
        self.setattr_interface_name()
        self.setattr_interface_shortname()
        self.setattr_interface_description()
        self.setattr_interface_adminstatus()
        self.setattr_interface_operationalstatus()
        self.setattr_interface_physicaladdress()
        self.setattr_interface_speed()
        self.setattr_interface_vlantrunkportdynamicstate()
        self.setattr_interface_ipaddress()
        self.setattr_real_host_ip()
        
        self._interface_sort()
        
    def get_ifindex(self, interface: str) -> str:
        oid_index = None
    
        if not self.cpsnmp.ifDescr:
            self.cpsnmp.populate_ifdescr()
    
        if not self.cpsnmp.ifDescr:
            value_err_msg = 'Unable to snmp walk ifDescr of {}, {}'
            raise ValueError(value_err_msg.format(self.obtac_host_ip, self.obtac_host_name))
    
        for snmpobjid in self.cpsnmp.ifDescr:
            if interface == snmpobjid.oid_value:
                oid_index = snmpobjid.oid_index
    
        return oid_index

    def get_ifip(self, interface: str) -> ipaddress.IPv4Interface:
        ipv4interface = None
        ip_address = None
        
        self.cpsnmp.populate_ipadentifindex()
        if not self.cpsnmp.ipAdEntIfIndex:
            value_err_msg = 'Unable to snmp walk ipAdEntIfIndex of {}, {}'
            raise ValueError(value_err_msg.format(self.obtac_host_ip, self.obtac_host_name))
        
        self.cpsnmp.populate_ipadentaddr()
        if not self.cpsnmp.ipAdEntAddr:
            value_err_msg = 'Unable to snmp walk ipAdEntAddr of {}, {}'
            raise ValueError(value_err_msg.format(self.obtac_host_ip, self.obtac_host_name))
        
        self.cpsnmp.populate_ipadentnetmask()
        if not self.cpsnmp.ipAdEntNetMask:
            value_err_msg = 'Unable to snmp walk ipAdEntNetMask of {}, {}'
            raise ValueError(value_err_msg.format(self.obtac_host_ip, self.obtac_host_name))

        for snmpobjid in self.cpsnmp.ipAdEntIfIndex:
            if snmpobjid.oid_value == self.get_ifindex(interface):
                ip_address = snmpobjid.oid_index
    
        for ipadentaddr, ipadentnetmask in zip(self.cpsnmp.ipAdEntAddr, self.cpsnmp.ipAdEntNetMask):
            if ipadentaddr.oid_index == ip_address:
                ipv4interface = ipaddress.IPv4Interface('{}/{}'.format(ipadentaddr.oid_index, ipadentnetmask.oid_value))
    
        if ipv4interface is None:
            value_err_msg = '`IPv4Interface` error: device {}, {},  interface {}'
            raise ValueError(value_err_msg.format(self.obtac_host_ip,self.obtac_host_name, interface))
        else:
            return ipv4interface

    def get_ifalias(self, interface: str) -> str:
        ifindex = self.get_ifindex(interface)
        ifalias = ''
        
        self.cpsnmp.populate_ifalias()
        if not self.cpsnmp.ifAlias:
            raise ValueError('Method get_ifalias() fail: unable to set instance attribute ifAlias.')
    
        for snmpobjid in self.cpsnmp.ifAlias:
            if snmpobjid.oid_index == ifindex:
                ifalias = snmpobjid.oid_value
    
        return ifalias

    def get_ifvrfname(self, interface: str) -> str:
        ifvrfname = ''
    
        cvvrfname_oid_astuple = (1, 3, 6, 1, 4, 1, 9, 9, 711, 1, 1, 1, 1, 2)
        
        self.cpsnmp.populate_cvvrfinterfacerowstatus()
        if self.cpsnmp.cvVrfInterfaceRowStatus is None:
            value_err_msg = 'Unable to snmp walk cvVrfInterfaceRowStatus of {}, {}'
            raise ValueError(value_err_msg.format(self.obtac_host_ip, self.obtac_host_name))
    
        for snmpobjid_a in self.cpsnmp.cvVrfInterfaceRowStatus:
            if snmpobjid_a.oid_index.split('.')[-1] == self.get_ifindex(interface):
                res_oid_index_aslist = list(snmpobjid_a.oid_index_astuple)
                res_oid_index_aslist.pop(-1)
                req_oid_astuple = cvvrfname_oid_astuple + tuple(res_oid_index_aslist)
                for snmpobjid_b in self.cpsnmp.snmpwalk(req_oid_astuple):
                    ifvrfname = snmpobjid_b.oid_value
    
        return ifvrfname

    def get_hostname(self) -> str:
        self.cpsnmp.populate_sysname()
        if self.cpsnmp.sysName is None:
            value_err_msg = 'Unable to snmp get sysName.0 of {}, {}'
            raise ValueError(value_err_msg.format(self.obtac_host_ip, self.obtac_host_name))
    
        return self.cpsnmp.sysName.oid_value.split('.')[0]

    def setattr_deviceclass(self):
        self.cpsnmp.populate_sysname()
        self.cpsnmp.populate_entlogicaltype()
        self.cpsnmp.populate_entphysicalserialnum()
        self.cpsnmp.populate_entphysicalmodelname()
        self.cpsnmp.populate_entphysicalsoftwarerev()
        self.cpsnmp.populate_entphysicaldescr()
        self.cpsnmp.populate_cswmaxswitchnum()
        self.cpsnmp.populate_cswswitchnumcurrent()
        self.cpsnmp.populate_cswswitchrole()
        self.cpsnmp.populate_cswswitchstate()
        self.cpsnmp.populate_cvsswitchmode()
        self.cpsnmp.populate_cvschassisswitchid()
        self.cpsnmp.populate_cvschassisrole()
        self.cpsnmp.populate_cvsmoduleslotnumber()

        if isinstance(self.cpsnmp.sysName, SnmpObjId) and self.cpsnmp.sysName.oid_value:
            self.real_host_name = self.get_hostname()
        
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
                            self.deviceclass = 'Switch Stack Member'
                            self.__class__ = CiscoPySwitch
                            self.oid_index = snmpobjid.oid_index

            if (not hasattr(self.cpsnmp.cswMaxSwitchNum, 'oid_value') and
                    not hasattr(self.cpsnmp.cvsSwitchMode, 'oid_value')):
                self.deviceclass = 'Switch'
        
    def __repr__(self):
        repr_string = '<{}(' \
                      'obtac_host_ip={}, ' \
                      'real_host_ip={}, ' \
                      'obtac_host_name={}, ' \
                      'real_host_name={}, ' \
                      'oid_index={}, ' \
                      'model_name={}, ' \
                      'os_version={}, ' \
                      'serial_number={}' \
                      ')>'
        return repr_string.format(self.__class__.__name__,
                                  self.obtac_host_ip,
                                  self.real_host_ip,
                                  self.obtac_host_name,
                                  self.real_host_name,
                                  self.oid_index,
                                  self.model_name,
                                  self.os_version,
                                  self.serial_number)


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
    def switch_state(self):
        for snmpobjid in self.cpsnmp.cswSwitchState:
            if self.oid_index == snmpobjid.oid_index:
                if int(snmpobjid.oid_value) is 1:
                    return 'waiting(1)'
                elif int(snmpobjid.oid_value) is 2:
                    return 'progressing(2)'
                elif int(snmpobjid.oid_value) is 3:
                    return 'added(3)'
                elif int(snmpobjid.oid_value) is 4:
                    return 'ready(4)'
                elif int(snmpobjid.oid_value) is 5:
                    return 'sdmMismatch(5)'
                elif int(snmpobjid.oid_value) is 6:
                    return 'verMismatch(6)'
                elif int(snmpobjid.oid_value) is 7:
                    return 'featureMismatch(7)'
                elif int(snmpobjid.oid_value) is 8:
                    return 'newMasterInit(8)'
                elif int(snmpobjid.oid_value) is 9:
                    return 'provisioned(9)'
                elif int(snmpobjid.oid_value) is 10:
                    return 'invalid(10)'
                elif int(snmpobjid.oid_value) is 11:
                    return 'removed(11)'
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
        repr_string = '<{}(' \
                      'obtac_host_ip={}, ' \
                      'real_host_ip={}, ' \
                      'obtac_host_name={}, ' \
                      'real_host_name={}, ' \
                      'oid_index={}, ' \
                      'model_name={}, ' \
                      'switch_number={}, ' \
                      'switch_role={}, ' \
                      'switch_state={}, ' \
                      'os_version={}, ' \
                      'serial_number={})>'
        return repr_string.format(self.__class__.__name__,
                                  self.obtac_host_ip,
                                  self.real_host_ip,
                                  self.obtac_host_name,
                                  self.real_host_name,
                                  self.oid_index,
                                  self.model_name,
                                  self.switch_number,
                                  self.switch_role,
                                  self.switch_state,
                                  self.os_version,
                                  self.serial_number)


class CiscoPySwitchStack(list):
    cpconf = CiscoPyConf()
    
    @property
    def obtac_host_ip(self):
        if self:
            return self[0].obtac_host_ip
        else:
            return ipaddress.IPv4Address(0)
    
    @property
    def obtac_host_name(self):
        if self:
            return self[0].obtac_host_name
        else:
            return ''
    
    @property
    def real_host_ip(self):
        if self:
            return self[0].real_host_ip
        else:
            return ipaddress.IPv4Address(0)
    
    @property
    def real_host_name(self):
        if self:
            return self[0].real_host_name
        else:
            return ''
    
    @property
    def ssh_username(self):
        if self:
            return self[0].ssh_username
        else:
            return ''
    
    @property
    def ssh_password(self):
        if self:
            return self[0].ssh_password
        else:
            return ''
    
    @property
    def all_interfaces(self):
        if self:
            return self[0].all_interfaces
        else:
            return ''
    
    def __repr__(self):
        repr_asstring = '<{}([{}])>'
        if self:
            return repr_asstring.format(self.__class__.__name__, ', '.join(map(str, self)))
        else:
            return repr_asstring.format(self.__class__.__name__, '')


class CiscoPyVSS(list):
    cpconf = CiscoPyConf()
    
    @property
    def obtac_host_ip(self):
        if self:
            return self[0].obtac_host_ip
        else:
            return ipaddress.IPv4Address(0)
    
    @property
    def obtac_host_name(self):
        if self:
            return self[0].obtac_host_name
        else:
            return ''
    
    @property
    def real_host_ip(self):
        if self:
            return self[0].real_host_ip
        else:
            return ipaddress.IPv4Address(0)
    
    @property
    def real_host_name(self):
        if self:
            return self[0].real_host_name
        else:
            return ''
    
    @property
    def ssh_username(self):
        if self:
            return self[0].ssh_username
        else:
            return ''
    
    @property
    def ssh_password(self):
        if self:
            return self[0].ssh_password
        else:
            return ''
    
    @property
    def all_interfaces(self):
        if self:
            return self[0].all_interfaces
        else:
            return ''
    
    def __repr__(self):
        repr_asstring = '<{}([{}])>'
        if self:
            return repr_asstring.format(self.__class__.__name__, ', '.join(map(str, self)))
        else:
            return repr_asstring.format(self.__class__.__name__, '')


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

    @property
    def serial_number(self):
        for snmpobjid in self.cpsnmp.entPhysicalSerialNum:
            if self.ent_oid_index == snmpobjid.oid_index:
                return snmpobjid.oid_value

    @property
    def model_name(self):
        for snmpobjid in self.cpsnmp.entPhysicalModelName:
            if self.ent_oid_index == snmpobjid.oid_index:
                return snmpobjid.oid_value

    @property
    def os_version(self):
        for snmpobjid in self.cpsnmp.entPhysicalSoftwareRev:
            if self.ent_oid_index == snmpobjid.oid_index:
                return snmpobjid.oid_value.split()[-1]

    ent_oid_index = ''

    def __repr__(self):
        repr_string = '<{}(' \
                      'obtac_host_ip={}, ' \
                      'real_host_ip={}, ' \
                      'obtac_host_name={}, ' \
                      'real_host_name={}, ' \
                      'oid_index={}, ' \
                      'ent_oid_index={}, ' \
                      'model_name={}, ' \
                      'chassis_switch_id={}, ' \
                      'chassis_switch_role={}, ' \
                      'os_version={}, ' \
                      'serial_number={}' \
                      ')>'

        return repr_string.format(self.__class__.__name__,
                                  self.obtac_host_ip,
                                  self.real_host_ip,
                                  self.obtac_host_name,
                                  self.real_host_name,
                                  self.oid_index,
                                  self.ent_oid_index,
                                  self.model_name,
                                  self.chassis_switch_id,
                                  self.chassis_role,
                                  self.os_version,
                                  self.serial_number)
