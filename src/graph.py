import networkx as nx
import matplotlib.pyplot as plt

class SemanticNode:
    """
    Represents a node in the semantic graph.
    Each node corresponds to a word with its linguistic properties.
    """
    def __init__(self, word, pos=None, definition=None, usage_patterns=None):
        self.word = word
        self.pos = pos
        self.definition = definition
        self.usage_patterns = usage_patterns if usage_patterns is not None else []

    def __repr__(self):
        return f"SemanticNode({self.word}, POS: {self.pos})"

class SemanticGraph:
    """
    Represents the semantic network as a graph.
    """
    def __init__(self):
        self.graph = nx.Graph()

    def add_node(self, node):
        """Adds a SemanticNode to the graph."""
        self.graph.add_node(node.word, data=node)

    def add_edge(self, word1, word2, weight=1.0):
        """Adds an edge between two words."""
        if self.graph.has_node(word1) and self.graph.has_node(word2):
            self.graph.add_edge(word1, word2, weight=weight)
        else:
            raise ValueError("One or both nodes not found in the graph.")

    def get_node(self, word):
        """Retrieves a node by its word."""
        if self.graph.has_node(word):
            return self.graph.nodes[word]['data']
        return None

    def find_path(self, word1, word2):
        """Finds the shortest path between two words."""
        try:
            return nx.shortest_path(self.graph, source=word1, target=word2)
        except nx.NetworkXNoPath:
            return None

    def get_neighbors(self, word):
        """Gets the neighbors of a word."""
        if self.graph.has_node(word):
            return list(self.graph.neighbors(word))
        return []

    def visualize_subgraph(self, words, filename="output/subgraph.png"):
        """Visualizes a subgraph containing the specified words."""
        subgraph = self.graph.subgraph(words)
        plt.figure(figsize=(12, 12))
        pos = nx.spring_layout(subgraph, k=0.5, iterations=50)
        nx.draw(subgraph, pos, with_labels=True, node_color='lightblue', node_size=2000, edge_color='gray', font_size=12, font_weight='bold')
        plt.title("Semantic Subgraph")
        plt.savefig(filename)
        plt.close()
        print(f"Subgraph saved to {filename}")