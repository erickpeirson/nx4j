import unittest
import networkx as nx
import py2neo
import random

from nx4j import write_graph, read_graph

class TestWriteGraph(unittest.TestCase):
    def setUp(self):
        self.host = 'http://localhost:7474'
        neoGraph = py2neo.Graph()
        neoGraph.delete_all()

    def test_write(self):
        """
        :func:`nx4j.write_graph` should return a :class:`py2neo.Graph` object with the
        appropriate number of nodes and edges.
        """

        graph = nx.generators.random_graphs.barabasi_albert_graph(20,10)
        neoGraph = write_graph(graph)
        self.assertIsInstance(neoGraph, py2neo.Graph)
        self.assertEqual(neoGraph.size, len(graph.edges()))
        self.assertEqual(neoGraph.order, len(graph.nodes()))

        neoGraph2 = py2neo.Graph()
        self.assertEqual(neoGraph2.size, len(graph.edges()))
        self.assertEqual(neoGraph2.order, len(graph.nodes()))

        neoGraph.delete_all()


    def test_write_labels(self):
        """
        :func:`nx4j.write_graph` should return a :class:`py2neo.Graph` object with the
        appropriate number of nodes and edges.
        """

        graph = nx.generators.random_graphs.barabasi_albert_graph(20,10)
        for node in graph.nodes():
            graph.node[node]['label'] = 'TestNode'

        neoGraph = write_graph(graph, label_key='label')
        self.assertEqual(len([ n for n in neoGraph.find('TestNode') ]), neoGraph.order)

        neoGraph.delete_all()


    def test_write_properties(self):
        """
        :func:`nx4j.write_graph` should return a :class:`py2neo.Graph` object with the
        appropriate number of nodes and edges.
        """

        graph = nx.generators.random_graphs.barabasi_albert_graph(20,10)
        i = 0
        for node in graph.nodes():
            graph.node[node]['a'] = i
            graph.node[node]['size'] = 'bob'
            graph.node[node]['label'] = 'TestNode'
            i += 1

        neoGraph = write_graph(graph)
        for n in neoGraph.find('TestNode'):
            self.assertIn('a', n.properties)
            self.assertIn('size', n.properties)
            self.assertEqual('bob', n.properties['size'])

        neoGraph.delete_all()


    def test_write_digraph(self):
        """
        :func:`nx4j.write_graph` should return a :class:`py2neo.Graph` object with the
        appropriate number of nodes and edges.
        """

        graph = nx.DiGraph()
        for i,j in zip([ random.randint(0,20) for x in xrange(40) ],
                       [ random.randint(0,20) for x in xrange(40) ]):
            graph.add_edge(i,j)

        neoGraph = write_graph(graph)
        self.assertIsInstance(neoGraph, py2neo.Graph)
        self.assertEqual(neoGraph.size, len(graph.edges()))
        self.assertEqual(neoGraph.order, len(graph.nodes()))

        neoGraph.delete_all()


    def test_write_multigraph(self):
        """
        :func:`nx4j.write_graph` should return a :class:`py2neo.Graph` object with the
        appropriate number of nodes and edges.
        """

        graph = nx.MultiGraph()
        for i,j in zip([ random.randint(0,20) for x in xrange(40) ],
                       [ random.randint(0,20) for x in xrange(40) ]):
            graph.add_edge(i,j)

        neoGraph = write_graph(graph)
        self.assertIsInstance(neoGraph, py2neo.Graph)
        self.assertEqual(neoGraph.size, len(graph.edges()))
        self.assertEqual(neoGraph.order, len(graph.nodes()))

        neoGraph.delete_all()


    def test_write_multidigraph(self):
        """
        :func:`nx4j.write_graph` should return a :class:`py2neo.Graph` object with the
        appropriate number of nodes and edges.
        """

        graph = nx.MultiDiGraph()
        for i,j in zip([ random.randint(0,20) for x in xrange(40) ],
                       [ random.randint(0,20) for x in xrange(40) ]):
            graph.add_edge(i,j)

        neoGraph = write_graph(graph)
        self.assertIsInstance(neoGraph, py2neo.Graph)
        self.assertEqual(neoGraph.size, len(graph.edges()))
        self.assertEqual(neoGraph.order, len(graph.nodes()))

        neoGraph.delete_all()


if __name__ == '__main__':
    unittest.main()