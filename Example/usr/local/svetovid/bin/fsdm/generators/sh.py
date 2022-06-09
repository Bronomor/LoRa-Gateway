# Copyright ##year## AVSystem <avsystem@avsystem.com>
# AVSystem SVD
# Version ##version##
# ALL RIGHTS RESERVED

import os
from typing import Mapping

from .generator import Generator, Template, ObjectDef


_RESOURCE_TEMPLATE = """\
#!/bin/sh

{{ load_runtime }}

RESOURCE_NAME="{{resource.name}}"
RESOURCE_DESCRIPTION="$(cat <<EOF
{{resource.description}}
EOF
)"
{% if not resource.is_executable %}
RESOURCE_DATATYPE="{{resource.datatype}}"
{% endif %}
{% if resource.multiple %}
RESOURCE_MULTIPLE=true
{% endif %}
{% if resource.is_readable %}
RESOURCE_EXTERNAL_NOTIFY=false

{{ class_name }}_read() {
    # environment variables set:
    # $INSTANCE_ID - int
    # $RESOURCE_INSTANCE_ID - int for multiple resources, unset otherwise

    # TODO: print value to stdout
    echo {{resource.default_value}}
}
{% endif %}

{% if resource.is_writable %}
{{ class_name }}_write() {
    # environment variables set:
    # $INSTANCE_ID - int
    # $RESOURCE_INSTANCE_ID - int for multiple resources, unset otherwise

    # TODO: read value from stdin
    exit $COAP_ERROR_NOT_IMPLEMENTED
}

{% endif %}
{% if resource.is_executable %}
{{ class_name }}_execute() {
    # environment variables set:
    # $INSTANCE_ID - int
    # Execute arguments available through $1 ... $9 and $# is number of passed
    # arguments. Each argument is in the form of either N or N=CONTENT. Nth
    # argument does not have to be under $N.

    # TODO: implement
    exit $COAP_ERROR_NOT_IMPLEMENTED
}

{% endif %}
{% if resource.is_resettable %}
{{ class_name }}_reset() {
    # environment variables set:
    # $INSTANCE_ID - int

{% if resource.multiple %}
    # TODO: reset resource to its original state. You can either clear it to
    # have 0 resource instances or delete the resource altogether.
    exit $COAP_ERROR_NOT_IMPLEMENTED
{% else %}
    # TODO: reset resource to its original state. You can either set it to a
    # default value or delete the resource.
    true
{% endif %}
}

{% endif %}
{% if resource.is_listable %}
{{ class_name }}_list() {
    # environment variables set:
    # $INSTANCE_ID - int

    # TODO: print whitespace-separated list of existing Resource Instance IDs
    exit $COAP_ERROR_NOT_IMPLEMENTED
}

{% endif %}

fsdm_main resource "{{ class_name }}" "$@"
"""

_INSTANCES_TEMPLATE = """\
#!/bin/sh

{{ load_runtime }}

INSTANCES_EXTERNAL_NOTIFY=false

{{ class_name }}_create() {
    # environment variables set:
    # $INSTANCE_ID - int

    # TODO: create new instance
    exit $COAP_ERROR_NOT_IMPLEMENTED
}

{{ class_name }}_delete() {
    # environment variables set:
    # $INSTANCE_ID - int

    # TODO: delete instance
    exit $COAP_ERROR_NOT_IMPLEMENTED
}

{{ class_name }}_list() {
    # TODO: print whitespace-separated list of existing Instance IDs
    echo 0
}


fsdm_main instances "{{ class_name }}" "$@"
"""

# TODO: what if it's installed somewhere else?
_LOAD_RUNTIME_FORMAT = """\
. {runtime_install_dir}/sh/utils.sh
"""

class ShGenerator(Generator):
    def __init__(self):
        super().__init__('sh', Template(_RESOURCE_TEMPLATE, _INSTANCES_TEMPLATE))

    def generate(self,
                 obj: ObjectDef,
                 target_directory: str,
                 runtime_install_dir: str):
        load_runtime = _LOAD_RUNTIME_FORMAT.format(runtime_install_dir=runtime_install_dir)
        super().generate(obj, target_directory, load_runtime=load_runtime)
