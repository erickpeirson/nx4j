import py2neo
import networkx as nx

func_names = ['function', 'method', 'builtin_function_or_method',
              'classmethod', 'instancemethod']


def _get_graph(host='localhost', protocol='http', port=7474, path='db/data',
               user=None, password=None, **kwargs):
    if user is not None and password is not None:
        auth = '{0}:{1}'.format(user, password)
    else:
        auth = ''

    dbpath = '{0}://{1}{2}:{3}/{4}/'.format(protocol, auth, host, port, path)
    neoGraph = py2neo.Graph(dbpath)
    return neoGraph


def _get_attrs(inst):
    try:
        attrs = {attr: value for attr, value in inst.__dict__.iteritems()
                 if type(value).__name__ not in func_names
                 and not attr.startswith('_')}
        return attrs
    except AttributeError:  # inst has no __dict__
        return {}


def _cast(node):
    classname = node.properties['_class']
    modname = node.properties['_module']

    if modname == '':
        _class = __builtins__[classname]
        inst = _class(node.properties['name'])
    else:
        _module = getattr(__import__(modname), modname.split('.')[-1])
        _class = getattr(_module, classname)
        inst = _class()

    for property, value in node.properties.iteritems():
        if property.startswith('_classattr'):
            pname = property.replace('_classattr_', '')
            setattr(inst, pname, value)

    return inst


def write_graph(graph, *args, **kwargs):
    """

    Parameters
    ----------
    graph : :class:`networkx.Graph`
    host : str
    protocol : str
    port : int
    path : str
    user : str
    password : str
    label_key : str
        Property in NetworkX graph node to use as a node label in Neo4j. If not
        set, will use the `__name__` of the node object's class.
    rel_key : str
        Property in the NetworkX graph edge to use as the relationship label in
        Neo4j. If not set, will use 'RELATED_TO'.

    Returns
    -------
    neoGraph : :class:`py2neo.Graph`
    """

    label_key = kwargs.get('label_key', None)
    rel_key = kwargs.get('rel_key', None)
    neoGraph = _get_graph(*args, **kwargs)
    unique_constraints = set()
    neoNodes = {}

    # Write nodes.
    for node, properties in graph.nodes(data=True):
        if label_key is not None and label_key in properties:
            label = properties[label_key]
        else:
            label = type(node).__name__

        if (label, "name") not in unique_constraints:   # Avoid setting twice.
            try:    # But this constraint may have been set before.
                neoGraph.schema.create_uniqueness_constraint(label, "name")
                unique_constraints.add((label, "name"))
            except:     # For some reason ConstraintViolationException
                pass    # doesn't play nicely.

        neoNode = py2neo.Node(label, name=str(node))

        for k, v in properties.iteritems():  # TODO: serialization?
            neoNode.properties[k] = v

        try:
            modname = node.__module__
        except:
            modname = ''
        neoNode.properties['_module'] = modname
        neoNode.properties['_class'] = node.__class__.__name__

        for attr, value in _get_attrs(node).iteritems():
            neoNode.properties['_classattr_{0}'.format(attr)] = value

        neoGraph.create(neoNode)
        neoNodes[node] = neoNode
        neoNode.push()

    # Write edges
    for source, target, properties in graph.edges(data=True):
        snode = neoNodes[source]
        tnode = neoNodes[target]

        if rel_key is not None and rel_key in properties:
            rel_label = properties[rel_key]
        else:
            rel_label = 'RELATED_TO'

        neoRel = py2neo.Relationship(snode, rel_label, tnode)
        neoGraph.create(neoRel)
        neoRel.push()

    return neoGraph


def read_graph(*args, **kwargs):
    query = kwargs.get('query',     # Get all nodes and edges, by default.
                       'MATCH ()-[r]-() RETURN *')

    graph = nx.MultiGraph()
    nodes = {}

    neoGraph = _get_graph(*args, **kwargs)
    results = neoGraph.cypher.execute(query)
    subgraph = results.to_subgraph()

    for edge in subgraph.relationships:
        if edge.start_node.properties['name'] in nodes:
            snode = nodes[edge.start_node.properties['name']]
        else:
            snode = _cast(edge.start_node)
            nodes[edge.start_node.properties['name']] = snode
            graph.add_node(snode, edge.start_node.properties)

        if edge.end_node.properties['name'] in nodes:
            enode = nodes[edge.end_node.properties['name']]
        else:
            enode = _cast(edge.end_node)
            nodes[edge.end_node.properties['name']] = enode
            graph.add_node(enode, edge.end_node.properties)

        graph.add_edge(snode, enode)

    return graph
