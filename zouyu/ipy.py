import ast
import builtins

import pandas as pd

from functools import partial
from collections import OrderedDict

from earthdragon.tools.timer import Timer

class LoadVisitor(ast.NodeVisitor):
    def __init__(self):
        self.names = []

    def visit(self, node):
        if self.is_load_name(node):
            self.names.append(node.id)
        self.generic_visit(node)

    def is_load_name(self, node):
        if not isinstance(node, ast.Name):
            return False

        if isinstance(node.ctx, ast.Load):
            return True

def load_vars(code):
    visitor = LoadVisitor()
    visitor.generic_visit(code)
    return visitor.names

def zframe(line, cell):
    """
    Allows a multi-cell. Basically, it will break up the cell by %% blocks
    and then execute each one in turn.
    """
    ip = get_ipython()
    user_ns = get_ipython().user_ns  # flake8: noqa
    code = ast.parse(cell)
    for line in code.body:
        names = load_vars(line)
        print(names)

        # for now, if not in blah
        if skip_run(names, user_ns):
            continue

        module = ast.Module()
        module.body = [line]
        c = compile(module, '<>', 'exec')
        exec(c, user_ns)

def _is_valid(name, ns):
    # built in that is not shadowed in scope
    if name not in ns and hasattr(builtins, name):
        return True

    # not in scope
    if name not in ns:
        return False

    # at this point, we have the var in our scope

    val = ns[name]
    if isinstance(val, pd.DataFrame):
        print(name)
        return False

    return True

def skip_run(names, ns):
    for name in names:
        if not _is_valid(name, ns):
            print('not valid', name)
            return True

#output[line] = ip.run_cell(line + "\n" + cell)

ip = get_ipython()
ip.register_magic_function(zframe, 'cell')

text = """
import os; import numpy
res = pd.rolling_sum(df.iloc[df.a > 5], 5)
pd.concat(df1, df2)
df.iloc[:10] = 1
"""

body = ast.parse(text).body
