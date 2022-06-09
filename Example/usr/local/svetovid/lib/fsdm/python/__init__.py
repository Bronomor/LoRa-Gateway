# Copyright ##year## AVSystem <avsystem@avsystem.com>
# AVSystem SVD
# Version ##version##
# ALL RIGHTS RESERVED

from .coap_error import CoapError
from .resource_handler import ResourceHandler
from .instances_handler import InstancesHandler
from .store import KvStore

class DataType:
    BOOLEAN = 'boolean'
    INTEGER = 'integer'
    FLOAT = 'float'
    STRING = 'string'
    OPAQUE = 'opaque'
    TIME = 'time'
    OBJLNK = 'objlnk'
