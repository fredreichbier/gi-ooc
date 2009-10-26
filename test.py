import sys
sys.path.append('/usr/lib/gobject-introspection/')
import re

import giscanner
from giscanner import girparser

from giooc import CodegenVisitor 
from giooc.wraplib.codegen import Codegen

parser = girparser.GIRParser()
parser.parse(sys.argv[1])

gen = CodegenVisitor()

print Codegen()(gen.visit_parser(parser)).buf


