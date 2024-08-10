import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

def read_csv(file_path):
    """Read CSV file and return DataFrame."""
    return pd.read_csv(file_path)

def create_graph(df):
    """Create a graph from the DataFrame."""
    G = nx.Graph()
    
    # Add edges to the graph
    for _, row in df.iterrows():
        city1 = row['City 1']
        city2 = row['City 2']
        distance = row['Distance']
        G.add_edge(city1, city2, weight=distance)
    
    return G

def draw_graph(G):
    """Draw the graph using matplotlib."""
    pos = nx.spring_layout(G)  # Position nodes using the Fruchterman-Reingold force-directed algorithm
    
    plt.figure(figsize=(12, 8))
    
    # Draw nodes
    nx.draw_networkx_nodes(G, pos, node_size=700, node_color='skyblue', alpha=0.7)
    
    # Draw edges with weights
    nx.draw_networkx_edges(G, pos, width=1.0, alpha=0.5, edge_color='gray')
    labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
    
    # Draw node labels
    nx.draw_networkx_labels(G, pos, font_size=12, font_family='sans-serif')
    
    plt.title('Graph Visualization')
    plt.show()

def main():
    file_path = 'data\chennai_cities.csv'  # Replace with your CSV file path
    df = read_csv(file_path)
    G = create_graph(df)
    draw_graph(G)

if __name__ == "__main__":
    main()
