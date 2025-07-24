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
    graphml_path = 'output/semantic_graph.graphml'
    if os.path.exists(graphml_path):
        try:
            # Load the graph from GraphML
            graph = nx.read_graphml(graphml_path)
            # Convert node attributes from string to appropriate types
            for node in graph.nodes():
                if 'weight' in graph.nodes[node]:
                    graph.nodes[node]['weight'] = float(graph.nodes[node]['weight'])
            print(f"Loaded graph with {len(graph.nodes())} nodes and {len(graph.edges())} edges")
            return graph
        except Exception as e:
            print(f"Error loading graph: {e}")
            print("Please run main.py first to rebuild the semantic graph.")
            exit(1)
    else:
        print(f"Error: No cached graph found at {graphml_path}")
        print("Please run main.py first to build the semantic graph.")
        exit(1)

def interactive_search(searcher):
    """Run an interactive search session."""
    print("\n=== ALLA POC Semantic Search ===")
    print("Enter a word to explore its semantic relationships")
    print("Commands:")
    print("  sim <word> - Find similar words")
    print("  path <word1> <word2> - Find paths between words")
    print("  neigh <word> - Show semantic neighborhood")
    print("  exit - Quit the program")
    print("  help - Show this help message")
    
    while True:
        try:
            # Get user input
            try:
                command = input("\n> ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                print("\nUse 'exit' to quit")
                continue
            
            # Handle empty input
            if not command:
                continue
                
            # Handle exit command
            if command == 'exit':
                print("Goodbye!")
                break
                
            # Handle help command
            if command == 'help':
                print("\nAvailable commands:")
                print("  sim <word> - Find similar words")
                print("  path <word1> <word2> - Find paths between words")
                print("  neigh <word> - Show semantic neighborhood")
                print("  exit - Quit the program")
                print("  help - Show this help message")
                continue
            
            # Parse command
            parts = command.split()
            if not parts:
                continue
                
            cmd = parts[0]
            
            # Handle similar words command
            if cmd == 'sim' and len(parts) > 1:
                word = ' '.join(parts[1:])
                try:
                    similar = searcher.find_similar_words(word, top_n=5)
                    if similar:
                        print(f"\nWords most similar to '{word}':")
                        for w, score in similar:
                            print(f"- {w} (score: {score:.3f})")
                    else:
                        print(f"No similar words found for '{word}'")
                except Exception as e:
                    print(f"Error finding similar words: {e}")
            
            # Handle path finding command
            elif cmd == 'path' and len(parts) > 2:
                word1, word2 = ' '.join(parts[1:-1]), parts[-1]
                try:
                    paths = searcher.find_connecting_paths(word1, word2, max_paths=3)
                    if paths:
                        print(f"\nPaths connecting '{word1}' to '{word2}':")
                        for i, path in enumerate(paths, 1):
                            print(f"{i}. {' -> '.join(path)}")
                    else:
                        print(f"No paths found between '{word1}' and '{word2}'")
                except Exception as e:
                    print(f"Error finding paths: {e}")
            
            # Handle neighborhood command
            elif cmd == 'neigh' and len(parts) > 1:
                word = ' '.join(parts[1:])
                try:
                    neighborhood = searcher.get_semantic_neighborhood(word, radius=2)
                    if neighborhood:
                        print(f"\nSemantic neighborhood of '{word}':")
                        for distance, words in sorted(neighborhood.items()):
                            truncated = words[:8]
                            print(f"  {distance} hop{'s' if distance > 1 else ''} away: {', '.join(truncated)}" + 
                                 ("..." if len(words) > 8 else ""))
                    else:
                        print(f"No neighborhood found for '{word}'")
                except Exception as e:
                    print(f"Error getting neighborhood: {e}")
            
            # Handle unknown commands
            else:
                print("Unknown command. Try 'sim <word>', 'path <word1> <word2>', 'neigh <word>', or 'exit'")
                print("Type 'help' to see available commands.")
                
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            print("Please try again or type 'exit' to quit.")

def main():
    # Load the semantic graph
    print("Loading semantic graph...")
    graph = load_graph()
    
    # Initialize semantic search with the loaded graph
    searcher = SemanticSearcher(graph)
    
    # Run interactive search
    interactive_search(searcher)
    
    print("\nThank you for using ALLA POC Semantic Search!")

if __name__ == "__main__":
    main()
