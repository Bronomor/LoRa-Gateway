# Copyright ##year## AVSystem <avsystem@avsystem.com>
# AVSystem SVD
# Version ##version##
# ALL RIGHTS RESERVED

import traceback

from .cmdline_parser import *
from .coap_error import CoapError


class InstancesHandler(object):
    @property
    def _is_creatable(self):
        return hasattr(self, 'create')

    @property
    def _is_deletable(self):
        return hasattr(self, 'delete')

    def _do_create(self, args):
        if not self._is_creatable:
            raise CoapError.METHOD_NOT_ALLOWED

        self.create(instance_id=args.instance)

    def _do_delete(self, args):
        if not self._is_deletable:
            raise CoapError.METHOD_NOT_ALLOWED

        self.delete(instance_id=args.instance)
    
    def _do_describe(self, _args):
        external_notify = ('true' if getattr(self, 'EXTERNAL_NOTIFY', False) else 'false')
        print('{"external-notify":%s}' % (external_notify))


    def main(self):
        actions = {
            'describe': ActionDefinition(callback=self._do_describe,
                                         help='Display object metadata'),
            'list': ActionDefinition(callback=lambda _: self.list(),
                                     help='List existing instances')
        }

        if self._is_creatable:
            actions['create'] = ActionDefinition(callback=self._do_create,
                                                 help='Create object instance',
                                                 args=[CmdlineArgument(name='instance',
                                                                       shortcut='i',
                                                                       type=int,
                                                                       help='Instance ID to create')])

        if self._is_deletable:
            actions['delete'] = ActionDefinition(callback=self._do_delete,
                                                 help='Delete object instance',
                                                 args=[CmdlineArgument(name='instance',
                                                                       shortcut='i',
                                                                       type=int,
                                                                       help='Instance ID to delete')])

        try:
            args = parse_cmdline(actions, description='Manage object instances')
            actions[args.action].callback(args)
        except Exception as e:
            traceback.print_exc()
            if isinstance(e, CoapError):
                sys.exit(e.exit_status)
            elif isinstance(e, NotImplementedError):
                sys.exit(CoapError.NOT_IMPLEMENTED.exit_status)
            else:
                sys.exit(CoapError.INTERNAL_SERVER_ERROR.exit_status)
