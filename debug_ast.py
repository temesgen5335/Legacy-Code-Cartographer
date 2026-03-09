import tree_sitter_python as tspython
from tree_sitter import Language, Parser

PY_LANGUAGE = Language(tspython.language())
parser = Parser(PY_LANGUAGE)

code = """
import os
from pathlib import Path
from typing import Dict, List, Set
"""

tree = parser.parse(bytes(code, "utf8"))

def print_node(node, depth=0):
    print("  " * depth + f"{node.type} [{node.start_byte}-{node.end_byte}]")
    for child in node.children:
        print_node(child, depth + 1)

print_node(tree.root_node)
