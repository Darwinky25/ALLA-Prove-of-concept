"""
Semantic Search Demo for ALLA POC

This script demonstrates the semantic search capabilities of the ALLA POC system.
It loads the semantic graph and provides an interactive interface for exploring
word similarities and relationships.
"""

import os
import networkx as nx
from src.graph import SemanticGraph
from src.semantic_search import SemanticSearcher

def load_graph():
    """Load the semantic graph from the cache."""
    graph = SemanticGraph()
    if os.path.exists('output/semantic_graph.gml'):
        graph.graph = nx.read_gml('output/semantic_graph.gml')
        print(f"Loaded graph with {len(graph.graph.nodes())} nodes and {len(graph.graph.edges())} edges")
    else:
        print("Error: No cached graph found. Please run main.py first to build the semantic graph.")
        exit(1)
    return graph

def interactive_search(searcher):
    """Run an interactive search session."""
    print("\n=== ALLA POC Semantic Search ===")
    print("Enter a word to explore its semantic relationships")
    print("Commands:")
    print("  sim <word> - Find similar words")
    print("  path <word1> <word2> - Find paths between words")
    print("  neigh <word> - Show semantic neighborhood")
    print("  exit - Quit the program")
    
    while True:
        try:
            command = input("\n> ").strip().lower()
            if not command:
                continue
                
            if command == 'exit':
                break
                
            parts = command.split()
            cmd = parts[0]
            
            if cmd == 'sim' and len(parts) > 1:
                word = ' '.join(parts[1:])
                similar = searcher.find_similar_words(word, top_n=5)
                if similar:
                    print(f"\nWords most similar to '{word}':")
                    for w, score in similar:
                        print(f"- {w} (score: {score:.3f})")
                else:
                    print(f"No similar words found for '{word}'")
                    
            elif cmd == 'path' and len(parts) > 2:
                word1, word2 = ' '.join(parts[1:-1]), parts[-1]
                paths = searcher.find_connecting_paths(word1, word2, max_paths=3)
                if paths:
                    print(f"\nPaths connecting '{word1}' to '{word2}':")
                    for i, path in enumerate(paths, 1):
                        print(f"{i}. {' -> '.join(path)}")
                else:
                    print(f"No paths found between '{word1}' and '{word2}'")
                    
            elif cmd == 'neigh' and len(parts) > 1:
                word = ' '.join(parts[1:])
                neighborhood = searcher.get_semantic_neighborhood(word, radius=2)
                if neighborhood:
                    print(f"\nSemantic neighborhood of '{word}':")
                    for distance, words in sorted(neighborhood.items()):
                        print(f"  {distance} hop{'s' if distance > 1 else ''} away: {', '.join(words[:8])}{'...' if len(words) > 8 else ''}")
                else:
                    print(f"No neighborhood found for '{word}'")
                    
            else:
                print("Unknown command. Try 'sim <word>', 'path <word1> <word2>', 'neigh <word>', or 'exit'")
                
        except KeyboardInterrupt:
            print("\nUse 'exit' to quit")
        except Exception as e:
            print(f"Error: {str(e)}")

def main():
    # Load the semantic graph
    print("Loading semantic graph...")
    graph = load_graph()
    
    # Initialize semantic search
    searcher = SemanticSearcher(graph.graph)
    
    # Run interactive search
    interactive_search(searcher)
    
    print("\nThank you for using ALLA POC Semantic Search!")

if __name__ == "__main__":
    main()
