# Copyright ##year## AVSystem <avsystem@avsystem.com>
# AVSystem SVD
# Version ##version##
# ALL RIGHTS RESERVED

import os
import importlib

from .generator import ObjectDef, Generator


SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
GENERATORS = {}

for fname in os.listdir(SCRIPT_DIR):
    if fname.endswith('.py') and fname != '__init__.py':
        try:
            mod_name = os.path.splitext(fname)[0]
            mod = importlib.import_module('%s.%s' % (__name__, mod_name))

            for name, maybe_gen in mod.__dict__.items():
                if (isinstance(maybe_gen, type)
                        and issubclass(maybe_gen, Generator)
                        and maybe_gen != Generator):
                    gen = maybe_gen()
                    assert gen.name not in GENERATORS, 'duplicate generator found for ' + gen.name
                    GENERATORS[gen.name] = gen
        except ImportError:
            import traceback
            traceback.print_exc()

__all__ = ['ObjectDef', 'GENERATORS']
