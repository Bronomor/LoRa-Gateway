# Copyright ##year## AVSystem <avsystem@avsystem.com>
# AVSystem SVD
# Version ##version##
# ALL RIGHTS RESERVED

import collections
import operator
import os
import string
import textwrap
import xml.etree

import jinja2


def _node_text(n: xml.etree.ElementTree.Element) -> str:
    return (n.text if n.text is not None else '').strip()


class ResourceDef(collections.namedtuple('ResourceDef', ['rid', 'name', 'operations', 'multiple', 'mandatory', 'type',
                                                         'range_enumeration', 'units', 'description'])):
    @property
    def datatype(self):
        return self.type.upper()

    @property
    def is_readable(self):
        return 'R' in self.operations

    @property
    def is_writable(self):
        return 'W' in self.operations

    @property
    def is_executable(self):
        return 'E' in self.operations

    @property
    def is_resettable(self):
        return self.is_writable

    @property
    def is_listable(self):
        return self.multiple

    @property
    def sanitized_name(self):
        def sanitized_char(c):
            if c in string.ascii_letters:
                return c
            if c in string.digits:
                return c
            return '_'

        return ''.join(sanitized_char(c) for c in self.name)

    @property
    def default_value(self):
        return {
            'STRING': '"TODO"',
            'OPAQUE': '"TODO"',
            'OBJLNK': '"0:0"',
            'INTEGER': 0,
            'INT': 0,
            'FLOAT': 0.0,
            'BOOLEAN': 0,
            'TIME': 0,
        }.get(self.datatype)

    @classmethod
    def from_etree(cls, res: xml.etree.ElementTree.Element) -> 'ResourceDef':
        return cls(rid=int(res.get('ID')),
                   name=_node_text(res.find('Name')),
                   operations=_node_text(res.find('Operations')).upper(),
                   multiple={'Single': False, 'Multiple': True}[_node_text(res.find('MultipleInstances'))],
                   mandatory={'Optional': False, 'Mandatory': True}[_node_text(res.find('Mandatory'))],
                   type=(_node_text(res.find('Type')).lower() or 'N/A'),
                   range_enumeration=(_node_text(res.find('RangeEnumeration')) or 'N/A'),
                   units=(_node_text(res.find('Units')) or 'N/A'),
                   description=textwrap.fill(_node_text(res.find('Description'))).replace('\n', '\n * '))


class ObjectDef(collections.namedtuple('ObjectDef',
                                       ['oid', 'name', 'description', 'urn', 'multiple', 'mandatory', 'resources'])):
    @classmethod
    def from_etree(cls, obj: xml.etree.ElementTree) -> 'ObjectDef':
        return cls(name=_node_text(obj.find('Name')),
                   description=textwrap.fill(_node_text(obj.find('Description1'))).replace('\n', '\n * '),
                   oid=int(_node_text(obj.find('ObjectID'))),
                   urn=_node_text(obj.find('ObjectURN')),
                   multiple={'Single': False, 'Multiple': True}[_node_text(obj.find('MultipleInstances'))],
                   mandatory={'Optional': False, 'Mandatory': True}[_node_text(obj.find('Mandatory'))],
                   resources=sorted([ResourceDef.from_etree(item) for item in obj.find('Resources').findall('Item')],
                                    key=operator.attrgetter('rid')))


class Template(collections.namedtuple('Template', ['resource', 'instances'])):
    pass


class Generator:
    def __init__(self,
                 name: str,
                 template: Template):
        self._name = name
        self._template = template

    @property
    def name(self):
        return self._name

    def generate(self,
                 obj: ObjectDef,
                 target_directory: str,
                 **kwargs):
        jinja_env = jinja2.Environment(trim_blocks=True)

        # resource scripts
        resources_dir = os.path.join(target_directory, 'resources')
        os.makedirs(resources_dir)
        for res in obj.resources:
            script_path = os.path.join(resources_dir, str(res.rid))

            with open(script_path, 'w') as f:
                f.write(jinja_env
                        .from_string(self._template.resource)
                        .render(class_name=('ResourceHandler_%d_%d' % (obj.oid, res.rid)),
                                resource=res,
                                **kwargs))

            os.chmod(script_path, 0o755)
            os.symlink('resources/' + str(res.rid), os.path.join(target_directory, res.sanitized_name))

        # instances script
        if obj.multiple:
            instances_path = os.path.join(target_directory, 'instances')

            with open(instances_path, 'w') as f:
                f.write(jinja_env
                        .from_string(self._template.instances)
                        .render(class_name=('InstancesHandler_%d' % (obj.oid,)),
                                **kwargs))

            os.chmod(instances_path, 0o755)
