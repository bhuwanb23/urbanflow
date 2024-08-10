import csv
import heapq
from collections import defaultdict

class Graph:
    def __init__(self):
        self.graph = defaultdict(list)
        self.edge_weights = {}  # Store edge weights for restoration
    
    def add_edge(self, u, v, weight):
        self.graph[u].append((v, weight))
        self.graph[v].append((u, weight))  # For undirected graph
        self.edge_weights[(u, v)] = weight
        self.edge_weights[(v, u)] = weight  # For undirected graph
    
    def dijkstra(self, start, end):
        distances = {vertex: float('infinity') for vertex in self.graph}
        distances[start] = 0
        priority_queue = [(0, start)]
        shortest_paths = {vertex: [] for vertex in self.graph}
        shortest_paths[start] = [start]
        
        while priority_queue:
            current_distance, current_vertex = heapq.heappop(priority_queue)
            
            if current_distance > distances[current_vertex]:
                continue
            
            for neighbor, weight in self.graph[current_vertex]:
                distance = current_distance + weight
                
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    heapq.heappush(priority_queue, (distance, neighbor))
                    shortest_paths[neighbor] = shortest_paths[current_vertex] + [neighbor]
                    
        return distances, shortest_paths
    
    def yen_k_shortest_paths(self, start, end, k):
        A = []  # List to store the k shortest paths
        B = []  # List to store candidate paths
        
        # Step 1: Find the shortest path using Dijkstra's algorithm
        distances, shortest_paths = self.dijkstra(start, end)
        if distances[end] == float('infinity'):
            return A  # No path found
        
        # Add the first shortest path to A
        A.append(shortest_paths[end])
        
        # Step 2: Loop to find the k-1 shortest paths
        for i in range(k - 1):
            for j in range(len(A[i]) - 1):
                spur_node = A[i][j]
                root_path = A[i][:j + 1]
                
                removed_edges = []
                for path in A:
                    if len(path) > j and root_path == path[:j + 1]:
                        u, v = path[j], path[j + 1]
                        # Remove edge u-v
                        weight = self.edge_weights.pop((u, v), None)
                        if weight is not None:
                            self.graph[u] = [(node, w) for node, w in self.graph[u] if node != v]
                            self.graph[v] = [(node, w) for node, w in self.graph[v] if node != u]
                            removed_edges.append((u, v, weight))
                
                spur_distances, spur_paths = self.dijkstra(spur_node, end)
                for path in spur_paths[end]:
                    if path not in A:
                        total_path = root_path + spur_paths[end][1:]
                        if total_path not in B:
                            B.append(total_path)
                
                # Restore the removed edges
                for u, v, weight in removed_edges:
                    self.add_edge(u, v, weight)
        
            B.sort(key=lambda p: sum(self.edge_weights.get((p[i], p[i+1]), 0) for i in range(len(p) - 1)))
            if not B:
                break
            
            A.append(B.pop(0))
        
        return A

def load_graph_from_csv(file_path):
    graph = Graph()
    
    with open(file_path, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            city1 = row['City 1']
            city2 = row['City 2']
            predicted_time_value = float(row['Predicted_Travel_Time'])  # Convert to float
            graph.add_edge(city1, city2, predicted_time_value)
    
    return graph

def print_path_details(path, edge_weights):
    total_time = 0
    path_details = []
    for i in range(len(path) - 1):
        u, v = path[i], path[i + 1]
        weight = edge_weights.get((u, v), 0)
        total_time += weight
        path_details.append(f"{u} -> {v}: {weight} mins")
    path_details.append(f"Total time: {total_time} mins")
    return path_details

if __name__ == "__main__":
    file_path = r'data\traffic.csv'  # Use raw string to handle backslashes
    g = load_graph_from_csv(file_path)
    
    start_node = 'Kovur'  # Replace with your actual start node
    end_node = 'K.K. Nagar'  # Replace with your actual end node
    k = 3  # Number of shortest paths to find
    
    shortest_paths = g.yen_k_shortest_paths(start_node, end_node, k)
    
    print(f"The {k} shortest paths from {start_node} to {end_node} are:")
    for idx, path in enumerate(shortest_paths, start=1):
        print(f"Path {idx}: {' -> '.join(path)}")
        details = print_path_details(path, g.edge_weights)
        for detail in details:
            print(detail)
 