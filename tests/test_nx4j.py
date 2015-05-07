import unittest
import networkx as nx
import py2neo
import random

from nx4j import write_graph, read_graph


class BobNode(object):
    def __init__(self, *args, **kwargs):
        for k, v in kwargs.iteritems():
            setattr(self, k, v)


class TestReadGraph(unittest.TestCase):
    def setUp(self):
        neoGraph = py2neo.Graph()
        neoGraph.delete_all()

    def tearDown(self):
        neoGraph = py2neo.Graph()
        neoGraph.delete_all()

    def test_read(self):
        """
        :func:`nx4j.read_graph` should return a :class:`networkx.Graph` object
        with the appropriate number of nodes and edges.
        """

        graph = nx.generators.random_graphs.barabasi_albert_graph(20, 10)
        i = 0
        for node in graph.nodes():
            graph.node[node]['a'] = i
            graph.node[node]['size'] = 'bob'
            graph.node[node]['label'] = 'TestNode'
            i += 1

        neoGraph = write_graph(graph)

        graph2 = read_graph()
        self.assertIsInstance(graph2, nx.Graph)
        self.assertEqual(neoGraph.size, len(graph2.edges()))
        self.assertEqual(neoGraph.order, len(graph2.nodes()))

        for n, properties in graph2.nodes(data=True):
            self.assertIn('a', properties)
            self.assertIn('size', properties)
            self.assertEqual('bob', properties['size'])

    def test_read_objects(self):
        """
        Should be able to write NetworkX nodes that are non-native objects.
        """

        bobs = [BobNode(asdf=i) for i in xrange(21)]
        graph = nx.Graph()
        for i, j in zip([random.randint(0, 20) for x in xrange(40)],
                        [random.randint(0, 20) for x in xrange(40)]):
            graph.add_edge(bobs[i], bobs[j])

        write_graph(graph)

        graph2 = read_graph()
        self.assertIsInstance(graph2, nx.Graph)
        self.assertEqual(len(graph2.nodes()), len(graph.nodes()))

        for node in graph2.nodes():
            self.assertIsInstance(node, BobNode)
            self.assertTrue(hasattr(node, 'asdf'))
            self.assertIsInstance(getattr(node, 'asdf'), int)

    def test_read_cypher(self):
        """
        Passing a kwarg `cypher` should result in a :class:`networkx.Graph`
        object containing only nodes and edges that respond to the cypher
        query.
        """
        pass


class TestWriteGraph(unittest.TestCase):
    def setUp(self):
        neoGraph = py2neo.Graph()
        neoGraph.delete_all()
        self.host = 'http://localhost:7474'

    def tearDown(self):
        neoGraph = py2neo.Graph()
        neoGraph.delete_all()

    def test_write(self):
        """
        :func:`nx4j.write_graph` should return a :class:`py2neo.Graph` object
        with the appropriate number of nodes and edges.
        """

        graph = nx.generators.random_graphs.barabasi_albert_graph(20, 10)
        neoGraph = write_graph(graph)
        self.assertIsInstance(neoGraph, py2neo.Graph)
        self.assertEqual(neoGraph.size, len(graph.edges()))
        self.assertEqual(neoGraph.order, len(graph.nodes()))

        neoGraph2 = py2neo.Graph()
        self.assertEqual(neoGraph2.size, len(graph.edges()))
        self.assertEqual(neoGraph2.order, len(graph.nodes()))

    def test_write_objects(self):
        """
        Should be able to write NetworkX nodes that are non-native objects.
        """

        bobs = [BobNode(asdf=i) for i in xrange(21)]
        graph = nx.Graph()
        for i, j in zip([random.randint(0, 20) for x in xrange(40)],
                        [random.randint(0, 20) for x in xrange(40)]):
            graph.add_edge(bobs[i], bobs[j])

        neoGraph = write_graph(graph)
        self.assertIsInstance(neoGraph, py2neo.Graph)
        self.assertEqual(neoGraph.size, len(graph.edges()))
        self.assertEqual(neoGraph.order, len(graph.nodes()))

        subgraph = neoGraph.cypher.execute('MATCH (n) RETURN *').to_subgraph()

        for node in subgraph.nodes:
            self.assertEqual(node.properties['_class'], 'BobNode')

    def test_write_labels(self):
        """
        :func:`nx4j.write_graph` should return a :class:`py2neo.Graph` object
        with the appropriate number of nodes and edges.
        """

        graph = nx.generators.random_graphs.barabasi_albert_graph(20, 10)
        for node in graph.nodes():
            graph.node[node]['label'] = 'TestNode'

        neoGraph = write_graph(graph, label_key='label')
        self.assertEqual(len([n for n in neoGraph.find('TestNode')]),
                         neoGraph.order)

    def test_write_properties(self):
        """
        :func:`nx4j.write_graph` should return a :class:`py2neo.Graph` object
        with the appropriate number of nodes and edges.
        """

        graph = nx.generators.random_graphs.barabasi_albert_graph(20, 10)
        i = 0
        for node in graph.nodes():
            graph.node[node]['a'] = i
            graph.node[node]['size'] = 'bob'
            graph.node[node]['label'] = 'TestNode'
            i += 1

        neoGraph = write_graph(graph, label_key='label')
        for n in neoGraph.find('TestNode'):
            self.assertIn('a', n.properties)
            self.assertIn('size', n.properties)
            self.assertEqual('bob', n.properties['size'])

    def test_write_digraph(self):
        """
        :func:`nx4j.write_graph` should return a :class:`py2neo.Graph` object
        with the appropriate number of nodes and edges.
        """

        graph = nx.DiGraph()
        for i, j in zip([random.randint(0, 20) for x in xrange(40)],
                        [random.randint(0, 20) for x in xrange(40)]):
            graph.add_edge(i, j)

        neoGraph = write_graph(graph)
        self.assertIsInstance(neoGraph, py2neo.Graph)
        self.assertEqual(neoGraph.size, len(graph.edges()))
        self.assertEqual(neoGraph.order, len(graph.nodes()))

    def test_write_multigraph(self):
        """
        :func:`nx4j.write_graph` should return a :class:`py2neo.Graph` object
        with the appropriate number of nodes and edges.
        """

        graph = nx.MultiGraph()
        for i, j in zip([random.randint(0, 20) for x in xrange(40)],
                        [random.randint(0, 20) for x in xrange(40)]):
            graph.add_edge(i, j)

        neoGraph = write_graph(graph)
        self.assertIsInstance(neoGraph, py2neo.Graph)
        self.assertEqual(neoGraph.size, len(graph.edges()))
        self.assertEqual(neoGraph.order, len(graph.nodes()))

    def test_write_multidigraph(self):
        """
        :func:`nx4j.write_graph` should return a :class:`py2neo.Graph` object
        with the appropriate number of nodes and edges.
        """

        graph = nx.MultiDiGraph()
        for i, j in zip([random.randint(0, 20) for x in xrange(40)],
                        [random.randint(0, 20) for x in xrange(40)]):
            graph.add_edge(i, j)

        neoGraph = write_graph(graph)
        self.assertIsInstance(neoGraph, py2neo.Graph)
        self.assertEqual(neoGraph.size, len(graph.edges()))
        self.assertEqual(neoGraph.order, len(graph.nodes()))


if __name__ == '__main__':
    unittest.main()
