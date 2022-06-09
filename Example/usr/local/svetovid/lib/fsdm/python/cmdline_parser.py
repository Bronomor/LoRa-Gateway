# Copyright ##year## AVSystem <avsystem@avsystem.com>
# AVSystem SVD
# Version ##version##
# ALL RIGHTS RESERVED

import collections
import os
import sys

from .coap_error import CoapError

CmdlineArgument = collections.namedtuple('CmdlineArgument',
                                         ['name',
                                          'shortcut',
                                          'type',
                                          'help'])

ActionDefinition = collections.namedtuple('ActionDefinition',
                                          ['callback',
                                           'help',
                                           'args'])
# __new__.__defaults__ fills in the default values of rightmost arguments
# so this effectively sets the default of 'args' to []
ActionDefinition.__new__.__defaults__ = ([],)

SUPPORTED_ACTIONS = ('execute', 'list', 'read', 'reset', 'write')

class CmdlineArgs(object):
    pass


def print_help(actions, description):
    action_names = sorted(actions.keys())
    sys.stderr.write(
        'usage: %s {%s} [options...]\n\n' % (os.path.basename(sys.argv[0]), ','.join(action_names)))
    sys.stderr.write('%s\n\n' % (description,))
    for action_name in action_names:
        action = actions[action_name]
        sys.stderr.write('%s - %s\n' % (action_name, action.help))
        for arg in action.args:
            sys.stderr.write('    -%s, --%s\n' % (arg.shortcut, arg.name))
            sys.stderr.write('        - %s\n\n' % (arg.help,))
        sys.stderr.write('\n')


def parse_cmdline(actions, *args, **kwargs):
    def attr_name(name):
        return name.replace('-', '_')

    try:
        if len(sys.argv) < 2:
            raise ValueError('command action not specified')
        cmdline_args = CmdlineArgs()
        cmdline_args.action = sys.argv[1]
        if cmdline_args.action not in actions:
            if cmdline_args.action in SUPPORTED_ACTIONS:
                sys.stderr.write('Unsupported action error: this resource supports only %s\n'
                                 % (sorted(actions.keys()),))
                raise CoapError.METHOD_NOT_ALLOWED
            else:
                raise ValueError('invalid action: %s\nValid FSDM actions are: %s'
                                 % (cmdline_args.action, SUPPORTED_ACTIONS))

        i = 2
        while i < len(sys.argv):
            arg = sys.argv[i]
            for candidate in actions[cmdline_args.action].args:
                if arg == '--' + candidate.name or arg == '-' + candidate.shortcut:
                    attr = attr_name(candidate.name)
                    if hasattr(cmdline_args, attr):
                        raise ValueError('duplicate argument: %s' % (arg,))
                    if candidate.type == int:
                        i += 1
                        setattr(cmdline_args, attr, int(sys.argv[i]))
                    elif candidate.type == list:
                        setattr(cmdline_args, attr, sys.argv[i + 1:])
                        i = len(sys.argv)
                    else:
                        raise NotImplementedError(
                            'unsupported argument type: %r' % (candidate.type,))
                    break
            else:
                raise ValueError('unknown argument: %s' % (arg,))
            i += 1

        for arg in actions[cmdline_args.action].args:
            attr = attr_name(arg.name)
            if not hasattr(cmdline_args, attr):
                setattr(cmdline_args, attr, None)

    except CoapError as e:
        sys.exit(e.exit_status)

    except Exception as e:
        sys.stderr.write('Command line parsing error: %s\n' % (e,))
        print_help(actions, *args, **kwargs)
        sys.exit(CoapError.INTERNAL_SERVER_ERROR.exit_status)

    return cmdline_args
