import re

def upper_first(name):
    if not name:
        return name
    if name[0].islower():
        return name[0].upper() + name[1:]
    else:
        return name

def oocize(name):
    # lower first letters
    name = re.sub('^([A-Z]+)', lambda m: m.group(1).lower(), name)
    # set_this -> setThis
    # underscores at the start are kept.
    underscored = False
    if name.startswith('_'):
        underscored = True
    name = re.sub('_([^_]*)', lambda m: upper_first(oocize(m.group(1))), name)
    if underscored:
        name = '_' + name
    return name

def oocize_type(name):
    # set_this -> setThis
    # underscores at the start are kept.
    underscored = False
    if name.startswith('_'):
        underscored = True
    name = re.sub('_([^_]*)', lambda m: upper_first(oocize(m.group(1))), name)
    if underscored:
        name = '_' + name
    return upper_first(name)

class Visitor(object):
    def visit(self, node):
        method_name = 'visit_%s' % node.__class__.__name__
        if hasattr(self, method_name):
            return getattr(self, method_name)(node)
        else:
            return self.visit_default(node)

    def visit_default(self, node):
        print 'no visitor for %s' % node.__class__.__name__
        return ''
