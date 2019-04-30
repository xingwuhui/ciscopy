# -*- coding: utf-8 -*-
# from .ciscopyinterface import CiscoPyIPv4Interface
from .ciscopynetwork import CiscoPyNetwork
from .ciscopysnmp import CiscoPySNMP
from .ciscopyconf import CiscoPyConf


class CiscoPyDevice(object):
    def __init__(self, host_ip, host_name, snmp_community, ssh_username, ssh_password):
        self.host_ip = host_ip
        self.host_name = host_name
        self.snmp_community = snmp_community
        self.ssh_username = ssh_username
        self.ssh_password = ssh_password
        self.deviceclass = None
        self.all_interfaces = []
        self.physical_interfaces = []
        self.cpnetwork = CiscoPyNetwork()
        self.cpconf = CiscoPyConf()

        if self.cpnetwork.reachable(self.host_ip):
            self.cpsnmp = CiscoPySNMP(host_ip, snmp_community)
            self.cpsnmp.set_all_attr_values()
            self.cpconf.from_device(host_ip, user=self.ssh_username, passwd=self.ssh_password)

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

    def setattr_deviceclass(self, entlogicaltype):
        entlogicaltype_set = set([le.value for le in entlogicaltype])

        if ('.1.3.6.1.2.1' in entlogicaltype_set or
                'mib-2' in entlogicaltype_set):
            self.deviceclass = 'IP Router'
            self.__class__ = CiscoPyRouter
        elif (('.1.3.6.1.2.1' not in entlogicaltype_set and
                'mib-2' not in entlogicaltype_set) and
                ('.1.3.6.1.2.1.17' in entlogicaltype_set or
                    'dot1dBridge' in entlogicaltype_set)):
            self.deviceclass = 'Switch'
            self.__class__ = CiscoPySwitch


class CiscoPyRouter(CiscoPyDevice):
    pass


class CiscoPySwitch(CiscoPyDevice):
    pass
    # def __init__(self):
    #     super(CiscoPySwitch, self).__init__()
    #     # self.switchvirtual_interfaces


class CiscoPySwitchStack(CiscoPySwitch):
    pass

