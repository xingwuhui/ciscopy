# -*- coding: utf-8 -*-
'''
A PYTHON PACKAGE FOR CISCO IOS-BASED DEVICES
'''

from ciscopy.ciscopyconf import CiscoPyConf
from ciscopy.ciscopyconf import CiscoPyConfAsList
from ciscopy.ciscopydevice import CiscoPyDevice
from ciscopy.ciscopyinterface import CiscoPyInterface
from ciscopy.ciscopynetwork import CiscoPyNetwork
from ciscopy.ciscopysnmp import CiscoPySNMP

__all__ = [CiscoPyConf,
           CiscoPyConfAsList,
           CiscoPyDevice,
           CiscoPyInterface,
           CiscoPyNetwork,
           CiscoPySNMP]
__author__ = 'John Natschev'
__maintainer__ = 'John Natschev'
__email__ = 'jnatschev@optusnet.com.au'
__status__ = 'Development'
__version__ = '0.0.2'
