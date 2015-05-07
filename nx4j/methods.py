import py2neo


def _get_graph(host='localhost', protocol='http', port=7474, path='db/data',
               user=None, password=None, **kwargs):
    if user is not None and password is not None:
        auth = '{0}:{1}'.format(user, password)
    else:
        auth = ''

    dbpath = '{0}://{1}{2}:{3}/{4}/'.format(protocol, auth, host, port, path)
    neoGraph = py2neo.Graph(dbpath)
    return neoGraph


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
    neoGraph = _get_graph(*args, **kwargs)
    return neoGraph
