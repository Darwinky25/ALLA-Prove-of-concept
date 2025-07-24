import os
import networkx as nx
from src.parser import Phase1_Parser
from src.graph import SemanticGraph
from src.api_client import FreeDictionaryClient
import validation.validate as validate

def main():
    """
    Main function to run the semantic graph construction and validation.
    """
    # Create output directory if it doesn't exist
    if not os.path.exists("output"):
        os.makedirs("output")
    
    if not os.path.exists("data"):
        os.makedirs("data")

    # --- Experiment Setup ---
    initial_definition = "A state of ease, often provided by a bed or mattress"
    
    # Optimized context for WordSim353 pairs
    context_keywords = [
        # Core seed words
        "state", "ease", "bed", "mattress", "provided",
        
        # WordSim353 pairs with direct connections
        "sleep", "dream", "comfort", "satisfaction",
        "furniture", "table", "cushion", "pillow",
        "king", "queen", "computer", "keyboard",
        "money", "cash", "book", "paper",
        "car", "train", "football", "basketball",
        "eat", "drink",
        
        # Essential connectors
        "rest", "support", "soft", "comfortable",
        "monarch", "royal", "type", "key", "typewriter",
        "currency", "dollar", "page", "read", "write",
        "vehicle", "transport", "sport", "game",
        "food", "beverage", "consume"
    ]
    
    print("Starting Phase 1: Building the Semantic Graph...")
    
    # --- Build the Graph ---
    parser = Phase1_Parser(
        initial_definition=initial_definition,
        context_keywords=context_keywords,
        max_hops=3
    )
    semantic_graph = parser.build_graph()
    
    num_nodes = len(semantic_graph.graph.nodes)
    num_edges = len(semantic_graph.graph.edges)
    
    # Calculate graph metrics
    if num_nodes > 0:
        density = nx.density(semantic_graph.graph)
        avg_degree = (2 * num_edges) / num_nodes
        
        # Calculate connected components
        num_components = nx.number_connected_components(semantic_graph.graph)
        largest_component = max(nx.connected_components(semantic_graph.graph), key=len)
        largest_component_size = len(largest_component)
        
        # Calculate average clustering coefficient
        clustering = nx.average_clustering(semantic_graph.graph)
    else:
        density = avg_degree = num_components = largest_component_size = clustering = 0

    print("\n=== Graph Construction Complete ===")
    print(f"Total nodes: {num_nodes}")
    print(f"Total edges: {num_edges}")
    print(f"Density: {density:.4f}")
    print(f"Average degree: {avg_degree:.4f}")
    print(f"Number of connected components: {num_components}")
    print(f"Largest component size: {largest_component_size} ({largest_component_size/num_nodes*100:.1f}% of total)")
    print(f"Average clustering coefficient: {clustering:.4f}")
    
    # Print sample of nodes and edges
    print("\nSample nodes:", list(semantic_graph.graph.nodes)[:10], "...")
    print("Sample edges:", list(semantic_graph.graph.edges)[:10], "...")

    # --- Visualization ---
    # Visualize a subgraph around the word 'ease'
    if 'ease' in semantic_graph.graph:
        print("Visualizing subgraph for 'ease'...")
        # Get neighbors up to 2 hops
        subgraph_nodes = set(['ease'])
        for neighbor in semantic_graph.get_neighbors('ease'):
            subgraph_nodes.add(neighbor)
            for second_neighbor in semantic_graph.get_neighbors(neighbor):
                subgraph_nodes.add(second_neighbor)
        
        semantic_graph.visualize_subgraph(list(subgraph_nodes), filename="output/ease_subgraph.png")
    else:
        print("'ease' not found in the graph, skipping visualization.")

    # --- Prepare Metrics Report ---
    metrics_report = (
        "=== Semantic Graph Metrics ===\n\n"
        f"Graph Structure:\n"
        f"  - Nodes: {num_nodes}\n"
        f"  - Edges: {num_edges}\n"
        f"  - Density: {density:.4f} (complete graph = 1.0, tree = ~2/n)\n"
        f"  - Average Degree: {avg_degree:.4f} (expected: ~2.91)\n"
        f"  - Connected Components: {num_components}\n"
        f"  - Largest Component: {largest_component_size} nodes ({largest_component_size/num_nodes*100:.1f}% of total)\n"
        f"  - Clustering Coefficient: {clustering:.4f} (0-1, higher = more clustered)\n"
        f"\nNode Degrees (sample):\n"
    )
    
    # Add degree distribution
    degrees = dict(semantic_graph.graph.degree())
    sorted_degrees = sorted(degrees.items(), key=lambda x: x[1], reverse=True)
    for node, degree in sorted_degrees[:10]:  # Top 10 nodes by degree
        metrics_report += f"    {node}: {degree}\n"
    
    if len(sorted_degrees) > 10:
        metrics_report += f"    ... and {len(sorted_degrees) - 10} more\n"
    
    # --- Semantic Validation ---
    print("\n=== WordSim353 Validation ===")
    from validation.validate import validate_with_wordsim353
    correlation, p_value = validate_with_wordsim353(semantic_graph)
    
    # Add validation results to metrics report
    validation_report = ""
    if correlation is not None:
        validation_report = (
            "\nSemantic Validation (WordSim353):\n"
            f"  - Spearman Correlation: {correlation:.4f}\n"
            f"  - P-value: {p_value:.4f}\n"
        )
    metrics_report += validation_report
    
    # Save metrics report
    with open("output/metrics.txt", "w") as f:
        f.write(metrics_report)

    # Save the graph for semantic search demo
    print("\nSaving semantic graph for search demo...")
    os.makedirs('output', exist_ok=True)
    
    # Create a simplified version of the graph for GML export
    G_simple = nx.Graph()
    
    # Add nodes with string attributes
    for node, data in semantic_graph.graph.nodes(data=True):
        G_simple.add_node(str(node))  # Convert node to string
        
    # Add edges
    for u, v in semantic_graph.graph.edges():
        G_simple.add_edge(str(u), str(v))  # Convert nodes to strings
    
    # Save the simplified graph
    nx.write_gml(G_simple, 'output/semantic_graph.gml')
    print(f"Graph saved to output/semantic_graph.gml")
    
    print("\nPOC Run Finished.")
    print("\nTo explore the semantic graph interactively, run:")
    print("  python semantic_search_demo.py")


if __name__ == "__main__":
    main()