from giscanner import ast

from .wraplib.odict import odict
from .wraplib.ooc import Function, Cover, Attribute, Class
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
    'double': 'Double',
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
            if isinstance(type, ast.Array):
                elem_type = self.get_ooc_type(type.element_type)
                return '%s*' % elem_type
            elif type.ctype in self.typemap:
                return self.typemap[type.ctype]
            elif '.' in type.name: # n-n-namespace!
                willi, top = type.name.rsplit('.', 1)
                return self.get_ooc_type(top)
            elif type.name in self.typemap:
                return self.typemap[type.name]
            elif type.name == 'none':
                return None
            elif type.ctype is None:
                assert 0, type
            else:
                name = oocize_type(type.name)
                self.typemap[type.ctype] = name
                return name

    def visit_parser(self, parser):
        out = []
        for include in parser.get_includes():
            out.append('import %s' % include.name)
        out.extend(self.visit(parser.get_namespace()))
        return out

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
        if node.target == 'none':
            cover = Cover(name)
        else:
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

    def visit_Enum(self, node):
        name = oocize_type(node.name)
        self.typemap[node.name] = 'Int' # enums are ints.
        klass = Class(name)
        for member in node.members:
            m_name = oocize(member.name)
            attr = Attribute(m_name, 'Int', ('const', 'static'), member.value)
            klass.add_member(attr)
        return klass

    def visit_Record(self, node):
        name = oocize_type(node.name)
        self.typemap[node.name] = name
        cover = Cover(name, modifiers=('extern',))
        for field in node.fields:
            # TODO: bitfield!
            m_name = oocize(field.name)
            if isinstance(field, ast.Field):
                attr = Attribute(m_name, self.get_ooc_type(field.type))
            elif isinstance(field, (ast.Callback, ast.Function)):
                attr = Attribute(m_name, 'Func') # TODO: more specific.
            else:
                assert 0, field
            cover.add_member(attr)
        return cover

    def visit_Union(self, node):
        name = oocize_type(node.name)
        self.typemap[node.name] = name
        cover = Cover(name, modifiers=('extern',))
        # TODO: union member getting support
        return cover

    def visit_GLibObject(self, node):
        name = oocize_type(node.name)
        cover = Cover(name, modifiers=('extern',))
        cover.from_ = node.name + '*'
        self.typemap[node.name + '*'] = name
        for member in node.methods:
            cover.add_member(self.visit(member))
        return cover

    def visit_GLibBoxedStruct(self, node):
        # TODO: complete this when you know what a boxed struct is
        name = oocize_type(node.name)
        cover = Cover(name, modifiers=('extern',))
        self.typemap[node.name] = name
        return cover

    def visit_GLibEnum(self, node):
        return self.visit_Enum(node) # TODO: heeeeh? any changes needed?
