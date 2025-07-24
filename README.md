# ALLA: AI Language Learning Architecture - Proof of Concept

This project demonstrates transparent and reproducible semantic graph construction from text definitions using data from the Free Dictionary API. It showcases how semantic understanding can be internally represented as a logical and stable graph structure.

## Core Objectives

1. **Transparency**: Demonstrate that the `SemanticGraph` is built recursively and can be traced from any relevant word in the initial definition.
2. **Internal Representation**: Show that a rich semantic network serves as evidence of understanding, without requiring external validation like QA.
3. **Empirical Validation**: Use quantitative metrics, visualizations, and the WordSim353 benchmark for reproducible validation.

## Project Structure

```
.
├── cache.json              # Cache for API responses to ensure reproducibility
├── data/
│   └── wordsim353.csv      # Benchmark dataset for semantic validation
├── main.py                 # Main script to run the entire experiment
├── output/
│   ├── ease_subgraph.png   # Visualization of the subgraph for "ease"
│   ├── semantic_graph.gml  # Serialized graph for the search demo
│   └── metrics.txt         # Quantitative metrics and validation results
├── README.md               # This documentation
├── requirements.txt        # Python dependencies
├── semantic_search_demo.py # Interactive semantic search interface
├── src/
│   ├── api_client.py       # Free Dictionary API client with caching
│   ├── graph.py            # SemanticNode and SemanticGraph class definitions
│   ├── parser.py           # Definition parsing and graph building logic
│   └── semantic_search.py  # Semantic search functionality
└── validation/
    └── validate.py         # Graph validation with WordSim353 dataset
```

## Quick Start

1. **Install Dependencies**:
   Ensure you have Python 3.8+ installed, then install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Main Script**:
   Execute the main script to build the semantic graph and run validations:
   ```bash
   python main.py
   ```

3. **Explore the Graph Interactively**:
   After building the graph, you can explore it interactively:
   ```bash
   python semantic_search_demo.py
   ```

## Key Features

- **Recursive Graph Construction**: Builds a semantic network by recursively exploring word definitions
- **Context-Aware Filtering**: Focuses on relevant terms using POS tagging and context keywords
- **Quantitative Validation**: Validates the semantic graph using WordSim353 benchmark
- **Interactive Exploration**: Explore the semantic graph through an interactive interface
- **Reproducible Results**: Caches API responses to ensure consistent results across runs

## Output and Results

After execution, you'll find the following outputs:

- `output/ease_subgraph.png`: Visualization of the semantic relationships around the word "ease"
- `output/semantic_graph.gml`: Serialized graph data for the search demo
- `output/metrics.txt`: Quantitative metrics including node/edge counts, density, and validation scores

## Understanding the Results

- **Graph Metrics**: The semantic graph typically contains hundreds of nodes and edges, with a low density characteristic of semantic networks
- **Validation Scores**: The Spearman correlation with WordSim353 provides a quantitative measure of the graph's semantic coherence
- **Visualization**: The subgraph visualization helps understand the local semantic neighborhood of key terms

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests for any improvements or bug fixes.

## License

This project is open source and available under the [MIT License](LICENSE).