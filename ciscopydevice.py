# -*- coding: utf-8 -*-
from .ciscopyconf import CiscoPyConf, CiscoPyNetwork
from .ciscopyinterface import ipaddress
from .ciscopysnmp import CiscoPySNMP, CommunityData, ContextData, SnmpObjId, SnmpEngine, UdpTransportTarget


class CiscoPyDevice(CiscoPySNMP, CiscoPyNetwork):
    def __init__(self, host_ip, host_name, snmp_community, ssh_username, ssh_password):
        super(CiscoPyDevice, self).__init__(host_ip, snmp_community)
        self.host_ip: ipaddress.IPv4Address = ipaddress.ip_address(host_ip)
        self.host_name: str = host_name
        self.snmp_community: str = snmp_community
        self.ssh_username: str = ssh_username
        self.ssh_password: str = ssh_password
        self.deviceclass = None
        self.serial_number: str = ''
        self.model_name: str = ''
        self.os_version: str = ''
        self.all_interfaces: list = list()
        self.physical_interfaces: list = list()
        self.virtual_interfaces: list = list()
        self.mpmodel: int = 1
        self.snmpEngine: SnmpEngine = SnmpEngine()
        self.communityData: CommunityData = CommunityData(self.snmp_community, mpModel=self.mpmodel)
        self.udpTransportTarget: UdpTransportTarget = UdpTransportTarget((str(self.host_ip), 161), timeout=10.0,
                                                                         retries=3)
        self.contextData: ContextData = ContextData()

        if self.reachable(str(self.host_ip)):
            self.status = True
            # self.set_all_attr_values()
            self.cpconf = CiscoPyConf()
            # self.cpconf.conf_fromdevice(self.host_ip,
            #                             self.host_name,
            #                             ssh_username=self.ssh_username,
            #                             ssh_password=self.ssh_password)

    def get_ifindex(self, interface: str) -> str:
        oid_index = None
    
        if not self.ifDescr:
            self.setattr_ifdescr()
    
        if not self.ifDescr:
            raise ValueError('Unable to snmp walk ifDescr of {}, {}'.format(self.host_ip, self.host_name))
    
        for snmpobjid in self.ifDescr:
            if interface == snmpobjid.oid_value:
                oid_index = snmpobjid.oid_index
    
        return oid_index

    def get_ifip(self, interface: str) -> ipaddress.IPv4Interface:
        ipv4interface = None
        ip_address = None
        
        if not hasattr(self, 'ipAdEntIfIndex'):
            self.setattr_ipadentifindex()
        
        if not hasattr(self, 'ipAdEntAddr'):
            self.setattr_ipadentaddr()
        
        if not hasattr(self, 'ipAdEntNetMask'):
            self.setattr_ipadentnetmask()
        
        if not self.ipAdEntIfIndex:
            value_err_msg = 'Unable to snmp walk ipAdEntIfIndex of {}, {}'
            raise ValueError(value_err_msg.format(self.host_ip, self.host_name))
        
        if not self.ipAdEntAddr:
            value_err_msg = 'Unable to snmp walk ipAdEntAddr of {}, {}'
            raise ValueError(value_err_msg.format(self.host_ip, self.host_name))
        
        if not self.ipAdEntNetMask:
            value_err_msg = 'Unable to snmp walk ipAdEntNetMask of {}, {}'
            raise ValueError(value_err_msg.format(self.host_ip, self.host_name))

        for snmpobjid in self.ipAdEntIfIndex:
            if snmpobjid.oid_value == self.get_ifindex(interface):
                ip_address = snmpobjid.oid_index
    
        for ipadentaddr, ipadentnetmask in zip(self.ipAdEntAddr, self.ipAdEntNetMask):
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
    
        if not hasattr(self, 'ifAlias'):
            self.setattr_ifalias()
    
        if not self.ifAlias:
            raise ValueError('Method get_ifalias() fail: unable to set instance attribute ifAlias.')
    
        for snmpobjid in self.ifAlias:
            if snmpobjid.oid_index == ifindex:
                ifalias = snmpobjid.oid_value
    
        return ifalias

    def get_ifvrfname(self, interface: str) -> str:
        ifvrfname = ''
    
        cvvrfname_oid_astuple = (1, 3, 6, 1, 4, 1, 9, 9, 711, 1, 1, 1, 1, 2)
        
        if not hasattr(self, 'cvVrfInterfaceRowStatus'):
            self.setattr_cvvrfinterfacerowstatus()
    
        if self.cvVrfInterfaceRowStatus is None:
            value_err_msg = 'Unable to snmp walk cvVrfInterfaceRowStatus of {}, {}'
            raise ValueError(value_err_msg.format(self.host_ip, self.host_name))
    
        for snmpobjid in self.cvVrfInterfaceRowStatus:
            if snmpobjid.oid_index.split('.')[-1] == self.get_ifindex(interface):
                res_oid_index_aslist = list(snmpobjid.oid_index_astuple)
                res_oid_index_aslist.pop(-1)
                req_oid_astuple = cvvrfname_oid_astuple + tuple(res_oid_index_aslist)
                for snmpobjid_ in self._snmpwalk(req_oid_astuple):
                    ifvrfname = snmpobjid_.oid_value
    
        return ifvrfname

    def get_hostname(self) -> str:
        if not hasattr(self, 'sysName'):
            self.setattr_sysname()
        
        if self.sysName is None:
            value_err_msg = 'Unable to snmp get sysName.0 of {}, {}'
            raise ValueError(value_err_msg.format(self.host_ip, self.host_name))
    
        return self.sysName.oid_value.split('.')[0]

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
        self.setattr_entlogicaltype()
        self.setattr_cswmaxswitchnum()
        self.setattr_cvsswitchmode()

        if not self.entLogicalType:
            self.deviceclass = 'Unknown'

        if not all(isinstance(v, SnmpObjId) for v in self.entLogicalType):
            raise TypeError('Not all attribute `entLogicalType` list elements are type `SnmpObjId`')

        entlogicaltype_set = set([snmpobjid.oid_value for snmpobjid in self.entLogicalType])

        if ('1.3.6.1.2.1' in entlogicaltype_set) or ('mib-2' in entlogicaltype_set):
            self.deviceclass = 'IP Router'
        elif (('1.3.6.1.2.1' not in entlogicaltype_set and 'mib-2' not in entlogicaltype_set) and
              ('1.3.6.1.2.1.17' in entlogicaltype_set or 'dot1dBridge' in entlogicaltype_set)):
            if hasattr(self.cvsSwitchMode, 'oid_value') and self.cvsSwitchMode.oid_value == '1':
                self.deviceclass = 'Switch'
            
            if hasattr(self.cvsSwitchMode, 'oid_value') and self.cvsSwitchMode.oid_value == '2':
                self.deviceclass = 'Virtual Switch System'

            if hasattr(self.cswMaxSwitchNum, 'oid_value'):
                self.deviceclass = 'Switch Stack'

            if not hasattr(self.cswMaxSwitchNum, 'oid_value') and not hasattr(self.cvsSwitchMode, 'oid_value'):
                self.deviceclass = 'Switch'
    
    def setup_switch_stack_data(self):
        if self.deviceclass == 'Switch Stack':
            pass
        

# class CiscoPyRouter(CiscoPyDevice):
#     pass
#
#
# class CiscoPySwitch(CiscoPyDevice):
#     pass
#
#
# class CiscoPySwitchStack(CiscoPyDevice):
#     def __init__(self):
#        super(CiscoPySwitchStack, self).__init__()
#        self.switches_in_stack = list()
#
#
# class CiscoPySwitchStackMember(CiscoPySwitch):
#     pass
#
#
# class CiscoPyVirtualSwitchSystem(CiscoPySwitch):
#     pass
