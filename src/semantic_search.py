import networkx as nx
from typing import List, Dict, Tuple
from collections import defaultdict

class SemanticSearcher:
    """
    A class for performing semantic similarity searches on a semantic graph.
    """
    
    def __init__(self, graph):
        """
        Initialize with a semantic graph.
        
        Args:
            graph: A networkx Graph object containing semantic relationships
        """
        self.graph = graph
        self._build_inverted_index()
    
    def _build_inverted_index(self):
        """Build an inverted index for faster word lookups."""
        self.word_index = {}
        for i, node in enumerate(self.graph.nodes()):
            self.word_index[node] = i
    
    def find_similar_words(self, word: str, top_n: int = 5) -> List[Tuple[str, float]]:
        """
        Find the top N most similar words to the given word.
        
        Args:
            word: The word to find similar words for
            top_n: Number of similar words to return
            
        Returns:
            List of (similar_word, similarity_score) tuples, sorted by score
        """
        if word not in self.graph:
            return []
        
        # Calculate similarity to all other words
        similarities = []
        for other_word in self.graph.nodes():
            if other_word == word:
                continue
                
            try:
                # Get shortest path length (inverse of similarity)
                path_length = nx.shortest_path_length(self.graph, word, other_word)
                # Convert to similarity score (shorter path = more similar)
                similarity = 1.0 / (1.0 + path_length)
                similarities.append((other_word, similarity))
            except (nx.NetworkXNoPath, nx.NodeNotFound):
                continue
        
        # Sort by similarity (descending) and return top N
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_n]
    
    def find_connecting_paths(self, word1: str, word2: str, max_paths: int = 3) -> List[List[str]]:
        """
        Find paths connecting two words in the semantic graph.
        
        Args:
            word1: First word
            word2: Second word
            max_paths: Maximum number of paths to return
            
        Returns:
            List of paths, where each path is a list of words
        """
        if word1 not in self.graph or word2 not in self.graph:
            return []
            
        try:
            # Get up to max_paths shortest paths
            paths = list(nx.all_shortest_paths(self.graph, word1, word2))
            return paths[:max_paths]
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return []

    def get_semantic_neighborhood(self, word: str, radius: int = 2) -> Dict[str, List[str]]:
        """
        Get words in the semantic neighborhood of the given word.
        
        Args:
            word: The center word
            radius: How many hops out to include
            
        Returns:
            Dictionary mapping distances to lists of words at that distance
        """
        if word not in self.graph:
            return {}
            
        neighborhood = defaultdict(list)
        
        # Use BFS to find nodes at each distance
        visited = {word}
        queue = [(word, 0)]
        
        while queue:
            current_word, distance = queue.pop(0)
            if distance > 0:  # Don't include the word itself
                neighborhood[distance].append(current_word)
                
            if distance < radius:
                for neighbor in self.graph.neighbors(current_word):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append((neighbor, distance + 1))
        
        return dict(neighborhood)
