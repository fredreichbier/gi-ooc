from .wraplib.odict import odict
from .wraplib.ooc import Function, Cover, Attribute
from .utils import Visitor, oocize, upper_first, oocize_type

OOC_TYPEMAP = {
    'gint': 'Int',
    'guint': 'UInt',
    'gdouble': 'Double',
    'gboolean': 'Bool',
    'gchar': 'Char',
    'gchar*': 'String',
    'gsize': 'SizeT',
    'gssize': 'SSizeT',
    'utf8': 'String',
    'any': 'Pointer',
    'int': 'Int',
    'uint': 'UInt',
    'int8': 'Int8',
    'uint8': 'UInt8',
    'int16': 'Int16',
    'uint16': 'UInt16',
    'int32': 'Int32',
    'uint32': 'UInt32',
    'int64': 'Int64',
    'uint64': 'UInt64',
}

CONSTANT_RESOLVERS = {
    'int': lambda s: s,
    'utf8': lambda s: '"%s"' % s,
    'double': lambda s: s,
}

class CodegenVisitor(Visitor):
    def __init__(self):
        self.typemap = OOC_TYPEMAP.copy()

    def get_ooc_type(self, type):
        if isinstance(type, basestring):
            return self.typemap.get(type, type)
        else:
            if type.ctype in self.typemap:
                return self.typemap[type.ctype]
            elif type.name in self.typemap:
                return self.typemap[type.name]
            elif type.name == 'none':
                return None
            else:
                name = oocize_type(type.name)
                self.typemap[type.ctype] = name
            return name

    def visit_parser(self, parser):
        return self.visit(parser.get_namespace())

    def visit_Namespace(self, node):
        return map(self.visit, node.nodes)

    def visit_Function(self, node):
        # get da name
        name = oocize(node.name)
        # arguments
        args = odict()
        varargs = False
        for parameter in node.parameters:
            if parameter.type.name == '<varargs>':
                varargs = True
            else:
                args[parameter.name] = self.get_ooc_type(parameter.type)
        # return type
        rettype = self.get_ooc_type(node.retval.type)
        # put em together
        func = Function(name,
            ('extern(%s)' % node.symbol,),
            args,
            rettype
        )
        func.varargs = varargs 
        return func

    def visit_Alias(self, node):
        self.typemap[node.name] = name = oocize_type(node.name)
        cover = Cover(name, self.get_ooc_type(node.target))
        return cover
       
    def visit_Constant(self, node):
        value = CONSTANT_RESOLVERS[node.type.name](node.value)
        attr = Attribute(node.name, self.get_ooc_type(node.type), ('const',), value)
        return attr

    def visit_Callback(self, node):
        self.typemap[node.name] = name = oocize_type(node.name)
        # TODO: we need more specific function signatures
        cover = Cover(name, 'Func')
        return cover
