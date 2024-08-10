import pandas as pd
import networkx as nx
import heapq

def read_csv_to_adjacency_matrix(filename):
    """
    Reads a CSV file and extracts edge data to create an adjacency matrix.
    
    Args:
    filename (str): Path to the CSV file.

    Returns:
    DataFrame: Pandas DataFrame containing edges with 'City 1', 'City 2', and 'Distance'.
    """
    try:
        # Attempt to read the CSV file into a DataFrame
        df = pd.read_csv(filename)
    except OSError as e:
        # Print error if file cannot be read
        print(f"Error reading the file: {e}")
        return None
    
    # Extract relevant columns for creating edges
    edges = df[['City 1', 'City 2', 'Predicted_Travel_Time']].dropna()
    return edges

def create_graph_from_edges(edges):
    """
    Converts the edge data into a NetworkX graph.

    Args:
    edges (DataFrame): Pandas DataFrame containing edges with 'City 1', 'City 2', and 'Distance'.

    Returns:
    Graph: A NetworkX graph constructed from the edges.
    """
    G = nx.Graph()  # Create an empty graph
    for index, row in edges.iterrows():
        city1 = row['City 1']
        city2 = row['City 2']
        distance = row['Predicted_Travel_Time']
        # Add edge between city1 and city2 with given distance
        G.add_edge(city1, city2, weight=distance)
    return G

def dijkstra(graph, start_node, end_node):
    """
    Finds the shortest path from start_node to end_node using Dijkstra's algorithm.

    Args:
    graph (Graph): NetworkX graph containing nodes and edges.
    start_node (str): Starting node for the pathfinding.
    end_node (str): Destination node for the pathfinding.

    Returns:
    tuple: Contains the shortest path (list of nodes) and the total distance.
    """
    distances = {node: float('inf') for node in graph.nodes()}
    distances[start_node] = 0
    priority_queue = [(0, start_node)]  # Min-heap priority queue
    predecessors = {node: None for node in graph.nodes()}

    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)

        if current_node == end_node:
            break

        for neighbor in graph.neighbors(current_node):
            weight = graph[current_node][neighbor]['weight']
            distance = current_distance + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                predecessors[neighbor] = current_node
                heapq.heappush(priority_queue, (distance, neighbor))

    # Reconstruct the shortest path from end_node to start_node
    path = []
    while end_node is not None:
        path.append(end_node)
        end_node = predecessors[end_node]
    path.reverse()  # Reverse path to get correct order
    return path, distances[path[-1]]

def find_n_shortest_paths(graph, start_node, end_node, n):
    """
    Finds the n shortest paths from start_node to end_node using a modified Dijkstra's algorithm.

    Args:
    graph (Graph): NetworkX graph containing nodes and edges.
    start_node (str): Starting node for the pathfinding.
    end_node (str): Destination node for the pathfinding.
    n (int): Number of shortest paths to find.

    Returns:
    list: List of tuples where each tuple contains a path (list of nodes) and its distance.
    """
    shortest_paths = []
    distances = {node: float('inf') for node in graph.nodes()}
    distances[start_node] = 0
    priority_queue = [(0, start_node, [])]  # Min-heap priority queue with path

    while priority_queue and len(shortest_paths) < n:
        current_distance, current_node, path = heapq.heappop(priority_queue)
        path = path + [current_node]

        if current_node == end_node:
            shortest_paths.append((path, current_distance))
            continue

        for neighbor in graph.neighbors(current_node):
            weight = graph[current_node][neighbor]['weight']
            distance = current_distance + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                heapq.heappush(priority_queue, (distance, neighbor, path))

    return shortest_paths

def main():
    """
    Main function to read data, create the graph, and find the shortest paths.
    """
    filename = 'data/traffic.csv'  # Path to the CSV file
    edges = read_csv_to_adjacency_matrix(filename)
    
    if edges is None:
        return

    # Create a graph from the edge data
    G = create_graph_from_edges(edges)

    start_node = 'K.K. Nagar'  # Starting city for pathfinding
    end_node = 'Pudur'    # Destination city for pathfinding
    n = 3                 # Number of shortest paths to find

    print(f"Finding the {n} shortest paths from {start_node} to {end_node}...")

    # Find the n shortest paths
    shortest_paths = find_n_shortest_paths(G, start_node, end_node, n)
    
    for i, (path, cost) in enumerate(shortest_paths):
        # Print each path and its total distance
        print(f"Path {i + 1}: {' -> '.join(path)} with cost {cost}")

if __name__ == "__main__":
    main()
