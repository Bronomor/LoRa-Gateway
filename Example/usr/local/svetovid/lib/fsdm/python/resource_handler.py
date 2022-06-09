# Copyright ##year## AVSystem <avsystem@avsystem.com>
# AVSystem SVD
# Version ##version##
# ALL RIGHTS RESERVED

import traceback

from .cmdline_parser import *
from .coap_error import CoapError


class ResourceHandler(object):
    @property
    def _is_readable(self):
        return hasattr(self, 'read')

    @property
    def _is_writable(self):
        return hasattr(self, 'write')

    @property
    def _is_executable(self):
        return hasattr(self, 'execute')

    @property
    def _is_resettable(self):
        return hasattr(self, 'reset')

    @property
    def _is_listable(self):
        return hasattr(self, 'list')

    def _do_read(self, args):
        self.read(instance_id=args.instance,
                  resource_instance_id=args.resource_instance)

    def _do_write(self, args):
        self.write(instance_id=args.instance,
                   resource_instance_id=args.resource_instance)

    def _do_execute(self, args):
        def convert_arg_to_key_value(arg):
            converted = arg.split('=', 1)
            number = int(converted[0])
            try:
                value = converted[1]
            except IndexError:
                value = None
            return (number, value)

        execute_args = dict(convert_arg_to_key_value(arg) for arg in (args.args or []))

        self.execute(instance_id=args.instance, args=execute_args)

    def _do_reset(self, args):
        self.reset(instance_id=args.instance)

    def _do_list(self, args):
        self.list(instance_id=args.instance)

    def _do_describe(self, _args):
        def assert_does_not_need_json_escaping(name, str):
            for char in str:
                if ord(char) < 32 or char in {'"', '\\'}:
                    raise ValueError('Invalid %s: %s' % (name, str))

        assert_does_not_need_json_escaping('name', self.NAME)
        operations = (('R' if self._is_readable else '')
                      + ('W' if self._is_writable else '')
                      + ('E' if self._is_executable else ''))
        multiple = 'true' if self._is_listable else 'false'

        maybe_datatype = ''
        if not self._is_executable:
            datatype = str(self.DATATYPE)
            assert_does_not_need_json_escaping('datatype', datatype)
            maybe_datatype = ',"datatype":"%s"' % (datatype,)

        external_notify = ('true' if getattr(self, 'EXTERNAL_NOTIFY', False) else 'false')

        print('{"operations":"%s","multiple":%s,"name":"%s"%s,"external-notify":%s}' % (
            operations, multiple, self.NAME, maybe_datatype, external_notify))

    def main(self):
        actions = {
            'describe': ActionDefinition(callback=self._do_describe,
                                         help='Display resource metadata')
        }

        if self._is_readable:
            actions['read'] = ActionDefinition(callback=self._do_read,
                                               help='Read resource value (via stdout)',
                                               args=[CmdlineArgument(name='instance',
                                                                     shortcut='i',
                                                                     type=int,
                                                                     help='Object Instance to operate on'),
                                                     CmdlineArgument(name='resource-instance',
                                                                     shortcut='r',
                                                                     type=int,
                                                                     help='Multiple Resource Instance to operate on')])

        if self._is_writable:
            actions['write'] = ActionDefinition(callback=self._do_write,
                                                help='Write resource value (via stdin)',
                                                args=[CmdlineArgument(name='instance',
                                                                      shortcut='i',
                                                                      type=int,
                                                                      help='Object Instance to operate on'),
                                                      CmdlineArgument(name='resource-instance',
                                                                      shortcut='r',
                                                                      type=int,
                                                                      help='Multiple Resource Instance to operate on')])

        if self._is_executable:
            actions['execute'] = ActionDefinition(callback=self._do_execute,
                                                  help='Execute resource action',
                                                  args=[CmdlineArgument(name='instance',
                                                                        shortcut='i',
                                                                        type=int,
                                                                        help='Object Instance to operate on'),
                                                        CmdlineArgument(name='args',
                                                                        shortcut='a',
                                                                        type=list,
                                                                        help='Execute arguments')])

        if self._is_resettable:
            actions['reset'] = ActionDefinition(callback=self._do_reset,
                                                help='Reset Resource to its original state.',
                                                args=[CmdlineArgument(name='instance',
                                                                      shortcut='i',
                                                                      type=int,
                                                                      help='Object Instance to operate on')])

        if self._is_listable:
            actions['list'] = ActionDefinition(callback=self._do_list,
                                               help='List resorce instances',
                                               args=[CmdlineArgument(name='instance',
                                                                     shortcut='i',
                                                                     type=int,
                                                                     help='Object Instance to operate on')])

        try:
            args = parse_cmdline(actions, description=self.DESCRIPTION)
            actions[args.action].callback(args)
        except Exception as e:
            traceback.print_exc()
            if isinstance(e, CoapError):
                sys.exit(e.exit_status)
            elif isinstance(e, NotImplementedError):
                sys.exit(CoapError.NOT_IMPLEMENTED.exit_status)
            else:
                sys.exit(CoapError.INTERNAL_SERVER_ERROR.exit_status)
