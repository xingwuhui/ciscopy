# -*- coding: utf-8 -*-
# from .ciscopyinterface import CiscoPyIPv4Interface


class CiscoPyDevice(object):
    def __init__(self):
        self.deviceclass = None
        self.all_interfaces = []
        self.physical_interfaces = []

    @staticmethod
    def _reset_interfacename(interface):
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
    def __init__(self):
        super(CiscoPySwitch, self).__init__()
        self.switchvirtual_interfaces


class CiscoPySwitchStack(CiscoPySwitch):
    pass

