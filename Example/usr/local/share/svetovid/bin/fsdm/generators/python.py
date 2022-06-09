# Copyright ##year## AVSystem <avsystem@avsystem.com>
# AVSystem SVD
# Version ##version##
# ALL RIGHTS RESERVED

import os
from typing import Mapping

from .generator import Generator, Template, ObjectDef


_RESOURCE_TEMPLATE = """\
#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

from fsdm import ResourceHandler, CoapError, DataType, KvStore


class {{ class_name }}(ResourceHandler):
    NAME = "{{resource.name}}"
    DESCRIPTION = '''\\
{{resource.description}}'''
{% if not resource.is_executable %}
    DATATYPE = DataType.{{resource.datatype}}
{% endif %}
{% if resource.is_readable %}
    EXTERNAL_NOTIFY = False

    def read(self,
             instance_id,            # int
             resource_instance_id):  # int for multiple resources, None otherwise
        # TODO: print value to stdout
        print({{resource.default_value}})

{% endif %}

{% if resource.is_writable %}
    def write(self,
              instance_id,            # int
              resource_instance_id):  # int for multiple resources, None otherwise
        # TODO: read value from stdin
        raise CoapError.NOT_IMPLEMENTED

{% endif %}
{% if resource.is_executable %}
    def execute(self,
                instance_id,  # int
                args):        # int -> (str or None)
        # TODO: implement
        raise CoapError.NOT_IMPLEMENTED

{% endif %}
{% if resource.is_resettable %}
    def reset(self,
              instance_id):  # int
{% if resource.multiple %}
        # TODO: reset resource to its original state. You can either clear it to
        # have 0 resource instances or delete the resource altogether.
        raise CoapError.NOT_IMPLEMENTED
{% else %}
        # TODO: reset resource to its original state. You can either set it to
        # a default value or delete the resource.
        pass
{% endif %}

{% endif %}
{% if resource.is_listable %}
    def list(self,
             instance_id):  # int
        # TODO: print space-separated list of available Resource Instance IDs
        raise CoapError.NOT_IMPLEMENTED
{% endif %}


if __name__ == '__main__':
    {{ class_name }}().main()

"""

_INSTANCES_TEMPLATE = """\
#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

from fsdm import InstancesHandler, CoapError


class {{ class_name }}(InstancesHandler):
    EXTERNAL_NOTIFY = False

    def create(self,
               instance_id):  # int
        # TODO: create new instance
        raise CoapError.NOT_IMPLEMENTED

    def delete(self,
               instance_id):  # int
        # TODO: delete instance
        # TODO: raise CoapError.BAD_REQUEST if instance does not exist
        raise CoapError.NOT_IMPLEMENTED

    def list(self):
        # TODO: print space-separated list of existing instances to stdout
        print("0")


if __name__ == '__main__':
    {{ class_name }}().main()

"""

class PythonGenerator(Generator):
    def __init__(self):
        super().__init__('python', Template(_RESOURCE_TEMPLATE, _INSTANCES_TEMPLATE))

    def generate(self,
                 obj: ObjectDef,
                 target_directory: str,
                 runtime_install_dir: str):
        super().generate(obj, target_directory)
