#! /usr/bin/env python
# encoding: utf-8
"""
Show value of a fully-qualified symbol (in a module or builtins).

Usage:
    pyval [-r | -j | -p | -f SPEC] [EXPR]...

Options:
    -r, --repr                  Print `repr(obj)`
    -j, --json                  Print `json.dumps(obj)`
    -p, --pprint                Print `pprint.pformat(obj)`
    -f SPEC, --format SPEC      Print `format(obj, SPEC)`

Examples:
    $ pyval sys.platform
    linux

    $ pyval math.pi**2
    9.869604401089358

    $ pyval 'math.sin(math.pi/4)'
    0.7071067811865475

    $ pyval -f .3f math.pi
    3.142
"""

__version__ = '0.0.5'

import ast
import argparse


class NameResolver(ast.NodeVisitor):

    """Resolve names within the given expression and updates ``locals`` with
    the imported modules."""

    def __init__(self, locals):
        super(NameResolver, self).__init__()
        self.locals = locals

    def visit_Name(self, node):
        resolve(node.id, self.locals)

    def visit_Attribute(self, node):
        parts = []
        while isinstance(node, ast.Attribute):
            parts.insert(0, node.attr)
            node = node.value
        if isinstance(node, ast.Name):
            parts.insert(0, node.id)
            resolve('.'.join(parts), self.locals)
        else:
            # We landed here due to an attribute access on some other
            # expression (function call, literal, tuple, etc…), and must
            # recurse in order to handle attributes or names within this
            # subexpression:
            self.visit(node)


def resolve(symbol, locals):
    """Resolve a fully-qualified name by importing modules as necessary."""
    parts = symbol.split('.')
    for i in range(len(parts)):
        name = '.'.join(parts[:i+1])
        try:
            exec('import ' + name, locals, locals)
        except ImportError:
            break


def formatter(args):
    """Return formatter requested by the command line arguments."""
    if args.repr:
        return repr
    elif args.json:
        from json import dumps
        return dumps
    elif args.pprint:
        from pprint import pformat
        return pformat
    elif args.format:
        return lambda value: format(value, args.format)
    else:
        return str


def main(args=None):
    """Show the value for all given expressions."""
    parser = argument_parser()
    args = parser.parse_args()
    fmt = formatter(args)
    for expr in args.EXPRS:
        locals = {}
        NameResolver(locals).visit(ast.parse(expr))
        value = eval(expr, locals)
        print(fmt(value))


def argument_parser():
    """Create parser for this script's command line arguments."""
    parser = argparse.ArgumentParser(
        description='Show value of given expressions, resolving names as'
        ' necessary through module imports.')
    parser.add_argument('--repr', '-r', action='store_true',
                        help='Print `repr(obj)`')
    parser.add_argument('--json', '-j', action='store_true',
                        help='Print `json.dumps(obj)`')
    parser.add_argument('--pprint', '-p', action='store_true',
                        help='Print `pformat(obj)`')
    parser.add_argument('--format', '-f', metavar='SPEC',
                        help='Print `format(obj, SPEC)`')
    parser.add_argument('EXPRS', nargs='+', help='Expressions to be evaluated')
    return parser


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv[1:]))
