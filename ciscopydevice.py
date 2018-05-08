# -*- coding: utf-8 -*-
from ipaddress import ip_interface
from ciscopy.ciscopyinterface import CiscoPyInterface


class CiscoPyDevice(object):
    @staticmethod
    def _obtac_if_name(self, interface):
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
    
    @property
    def obtac_snmp_community(self):
        rx = r'^snmp-server community [\x21-\x7E]+ rw snmp-access'
        try:
            return self.cc.include(rx)[0].split()[-3]
        except AttributeError:
            return None

    def reset_device_class(self):
        entlogicaltype_set = set([le.value for le in self.cs.entLogicalType])
        
        if ({'.1.3.6.1.2.1'} or
                {'.1.3.6.1.2.1', '.1.3.6.1.2.1.17'}) == entlogicaltype_set:
            if self.__class__ is CiscoPyDevice:
                self.__class__ = CiscoPyRouter
        elif  {'.1.3.6.1.2.1.17'} == entlogicaltype_set:
            if self.__class__ is CiscoPyDevice:
                self.__class__ = CiscoPySwitch

    @property
    def cmdb_class(self):
        entlogicaltype_set = set([le.value for le in self.cs.entLogicalType])
        
        if ({'.1.3.6.1.2.1'} or
                {'.1.3.6.1.2.1', '.1.3.6.1.2.1.17'}) == entlogicaltype_set:
            return 'IP Router'
        elif {'.1.3.6.1.2.1.17'} == entlogicaltype_set:
            return 'Switch'
        else:
            return 'Unknown'
    
    @property
    def obtac_node_interface(self):
        node_interface = CiscoPyInterface()
        
        for ifa, ifn in zip(self.cs.ifAlias, self.cs.ifName):
            if (ifa.value.lower().startswith('*n**')
                    or ifa.value.lower().startswith('*** emc')):
                node_interface['name'] = self._obtac_if_name(ifn.value)
                node_interface['oid index'] = ifa.oid_index
                node_interface['description'] = ifa.value
                
                for iaeii, iaea, iaenm in zip(self.cs.ipAdEntIfIndex,
                                              self.cs.ipAdEntAddr,
                                              self.cs.ipAdEntNetMask):
                    if ifa.oid_index == iaeii.value:
                        ipint = '/'.join([iaea.value, iaenm.value])
                        node_interface['ip address'] = ip_interface(ipint)
        
        return node_interface
    
    @property
    def wan_interfaces(self):
        wan_interface_list = list()
        
        for ifa, ifn in zip(self.cs.ifAlias, self.cs.ifName):
            # if ifa.value.lower().startswith('*** ovpi_poll'):
            if 'wan' in ifa.value.lower():
                wan_interface = {'name': self._obtac_if_name(ifn.value),
                                 'oid_index': ifa.oid_index,
                                 'description': ifa.value,
                                 'circuit_id': ifa.value.strip(' *').split('is ')[-1]}
                
                for iaeii, iaea, iaenm in zip(self.cs.ipAdEntIfIndex,
                                              self.cs.ipAdEntAddr,
                                              self.cs.ipAdEntNetMask):
                    if iaeii.value == ifa.oid_index:
                        wan_interface['ip address'] = (
                            ip_interface('/'.join([iaea.value, iaenm.value])))
                
                wan_interface_list.append(wan_interface)
        
        return tuple(wan_interface_list)


class CiscoPyRouter(CiscoPyDevice):
    pass


class CiscoPySwitch(CiscoPyDevice):
    pass
    #WAN_INTERFACES NEEDS TO BE UPDATED SO THAT WE GRAB
    #THE UPSTREAM (WAN ACCESS) NEIGHBOUR AND INTERFACE
    #PER SWITCH INTERFACE THAT CONTAINS OVPI_POLL IN THE
    #DESCRIPTION. THIS IS HOW WE DETERMINE WHAT WE NEED FOR
    #SWITCH CMDB CI RELATIONS
    #@property
    #def wan_interfaces(self):
    #    wan_interface_list = list()
    #    
    #    for ifa, ifn in zip(self.cs.ifAlias, self.cs.ifName):
    #        if ifa.value.lower().startswith('*** ovpi_poll'):
    #            wan_interface = {'name': self._obtac_if_name(ifn.value),
    #                             'oid_index': ifa.oid_index,
    #                             'description': ifa.value,
    #                             'circuit_id': ifa.value.strip(' *').split('is ')[-1]}
    #            
    #            for iaeii, iaea, iaenm in zip(self.cs.ipAdEntIfIndex,
    #                                          self.cs.ipAdEntAddr,
    #                                          self.cs.ipAdEntNetMask):
    #                if iaeii.value == ifa.oid_index:
    #                    wan_interface['ip address'] = (
    #                        ip_interface('/'.join([iaea.value, iaenm.value])))
    #            
    #            wan_interface_list.append(wan_interface)
    #    
    #    return (wi for wi in tuple(wan_interface_list))
