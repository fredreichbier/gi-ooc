import re

ALIASES = {
    'String': 'GString',
    'Time': 'GTime',
}

def upper_first(name):
    if not name:
        return name
    if name[0].islower():
        return name[0].upper() + name[1:]
    else:
        return name

def oocize(name):
    if not name:
        return '_' # TODO: that should not be necessary
    # lower first letters
    name = re.sub('^([A-Z]+)', lambda m: m.group(1).lower(), name)
    # set_this -> setThis
    # underscores at the start are kept.
    underscored = False
    if name.startswith('_') or name[0].isdigit():
        underscored = True
    name = re.sub('_([^_]*)', lambda m: upper_first(oocize(m.group(1))), name)
    if underscored:
        name = '_' + name
    return censor(name)

def oocize_type(name):
    if name in ALIASES:
        return ALIASES[name]
    if not name:
        return '_' # TODO: that should not be necessary  
    # set_this -> setThis
    # underscores at the start are kept.
    underscored = False
    if name.startswith('_') or name[0].isdigit():
        underscored = True
    name = re.sub('_([^_]*)', lambda m: upper_first(oocize(m.group(1))), name)
    if underscored:
        name = '_' + name
    return censor(upper_first(name))

class Visitor(object):
    def visit(self, node):
        method_name = 'visit_%s' % node.__class__.__name__
        if hasattr(self, method_name):
            return getattr(self, method_name)(node)
        else:
            return self.visit_default(node)

    def visit_default(self, node):
        print 'no visitor for %s' % node.__class__.__name__, node
        return ''

KEYWORDS = 'class, cover, interface, implement, func, abstract, extends, from, this, super, new, const, final, static, include, import, use, extern, inline, proto, break, continue, fallthrough, operator, if, else, for, while, do, switch, case, as, in, version, return, true, false, null, default, match'.split(', ') + ["auto",
                "break",
                "case",
                "char",
                "const",
                "continue",
                "default",
                "do",
                "double",
                "else",
                "enum",
                "extern",
                "float",
                "for",
                "goto",
                "if",
                "int",
                "long",
                "register",
                "return",
                "short",
                "signed",
                "static",
                "struct",
                "switch",
                "typedef",
                "union",
                "unsigned",
                "void",
                "volatile",
                "while",
                "inline",
                "_Imaginary",
                "_Complex",
                "_Bool",
                "restrict", "Func", "NULL", "TRUE", "FALSE"]

def censor(name):
    if name in KEYWORDS:
        return censor(name + '_')
    else:
        return name

