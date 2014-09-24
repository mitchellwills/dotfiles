from collections import defaultdict

__all__ = ['RelationalDatabaseNode', 'RelationalDatabase', 'make_inverse_relationships', 'Relationship']
__abstract__ = True

class RelationalDatabaseNode(object):
    def __init__(self, key):
        self._key = key
        self._relationships = defaultdict(set)
        self._database = None

    @property
    def key(self):
        return self._key

    def add_relationship(self, relationship, other_name):
        self._database.add_relationship(self.key, relationship, other_name)

    def get_related(self, relationship):
        return set(self._relationships[relationship])

class Relationship(object):
    def __init__(self, name):
        self._name = name
    @property
    def name(self):
        return self._name
    def __repr__(self):
        return self.name


def get_inverse_relationship(relationship):
    if hasattr(relationship, 'INVERSE'):
        return relationship.INVERSE
    return None

def make_inverse_relationships(relationship1, relationship2):
    relationship1.INVERSE = relationship2
    relationship2.INVERSE = relationship1

class RelationalDatabase(object):
    def __init__(self, node_factory = None):
        self._nodes = dict()
        self.node_factory = node_factory

    def ensure_node(self, name):
        if name not in self._nodes:
            self.add_node(self.node_factory(name))
        return self._nodes[name]

    def add_node(self, node):
        if not isinstance(node, RelationalDatabaseNode):
            raise Exception('The node must derrive from RelationalDatabaseNode')
        if node.key in self._nodes:
            raise Exception('The node '+node.key+'was already added to the database')
        if node._database is not None:
            raise Exception('The node '+node.key+'was already added to a different database')
        node._database = self
        self._nodes[node.key] = node

    def add_relationship(self, node1_name, relationship, node2_name):
        self.ensure_node(node1_name)
        self.ensure_node(node2_name)
        return self._add_relationship(self._nodes[node1_name], relationship, self._nodes[node2_name])

    def _add_relationship(self, node1, relationship, node2):
        if node1 is None or relationship is None or node2 is None:
            raise Exception('All argurments must not be None')
        node1._relationships[relationship].add(node2)
        inverse_relationship = get_inverse_relationship(relationship)
        if inverse_relationship is not None:
            node2._relationships[inverse_relationship].add(node1)

    def __getitem__(self, name):
        return self._nodes[name]

    def __contains__(self, x):
        return x in self._nodes

    def keys(self):
        return self._nodes.keys()
    def nodes(self):
        return self._nodes.values()


    def write_graphviz(self, f):
        def to_graphviz(key):
            return 'p_'+key.replace('-', '_').replace('*', '_').replace(':', '_')
        f.write('digraph G {\n')
        for node_key in self._nodes:
            f.write(' ' + to_graphviz(node_key) + ' [ label="'+node_key+'" ];\n')
        for node_key in self._nodes:
            node = self._nodes[node_key]
            for relationship in node._relationships:
                for other in node._relationships[relationship]:
                    f.write(' ' + to_graphviz(node_key) + ' -> ' + to_graphviz(other.key) + ' [ label="'+str(relationship)+'" ];\n')
        f.write('}\n')
