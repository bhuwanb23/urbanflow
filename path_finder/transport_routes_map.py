import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# Load the CSV data into a DataFrame
df = pd.read_csv('data\chennai_cities.csv')

# Create a graph object
G = nx.Graph()

# Define colors for different transport modes
color_map = {
    'Train Station': 'green',
    'Micro Mobility': 'purple',
    'Ride Sharing': 'orange'
}

# Create a mapping from city names to node numbers
city_to_node = {}
node_counter = 1

# Add edges to the graph from the DataFrame
for _, row in df.iterrows():
    city1 = row['City 1']
    city2 = row['City 2']
    
    # Ensure unique numbers for each city
    if city1 not in city_to_node:
        city_to_node[city1] = node_counter
        node_counter += 1
    if city2 not in city_to_node:
        city_to_node[city2] = node_counter
        node_counter += 1
    
    node1 = city_to_node[city1]
    node2 = city_to_node[city2]
    
    # Determine the color of the edge based on the type of transport
    if row['Train Station']:
        color = color_map['Train Station']
    elif row['Micro Mobility']:
        color = color_map['Micro Mobility']
    elif row['Ride Sharing']:
        color = color_map['Ride Sharing']
    else:
        color = 'gray'  # Color for bus stops or unspecified modes
    
    distance = row['Distance']
    # Add edge with distance as the weight and transport mode as color
    G.add_edge(node1, node2, color=color)

# Set up the figure and axis
plt.figure(figsize=(12, 8))

# Get edge colors 
edges = G.edges()
colors = [G[u][v]['color'] for u, v in edges]

# Draw the network
pos = nx.spring_layout(G)  # positions for all nodes

# Draw nodes
nx.draw_networkx_nodes(G, pos, node_size=500, node_color='lightblue', alpha=0.7)

# Draw edges with different colors
nx.draw_networkx_edges(G, pos, edgelist=edges, width=2.0, alpha=0.7, edge_color=colors)

# Draw labels as node numbers
node_labels = {v: str(v) for v in G.nodes()}
nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=10, font_family='sans-serif')

# Draw edge labels (distances)
edge_labels = nx.get_edge_attributes(G, 'weight')
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')

# Add a legend for transport modes
handles = [plt.Line2D([0], [0], color=color_map[m], lw=2) for m in color_map]
handles.append(plt.Line2D([0], [0], color='gray', lw=2))
labels = [f'{m} Mode' for m in color_map] + ['Bus Stop (Universal)']
plt.legend(handles, labels, title="Transport Modes")

# Display the graph
plt.title('Transport Routes Network with Transport Modes (Node Numbers)')
plt.show()
