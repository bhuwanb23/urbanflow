import csv
import heapq
from collections import defaultdict
from datetime import datetime, timedelta
import pandas as pd

# Graph implementation using adjacency list
class Graph:
    def __init__(self):
        self.graph = defaultdict(list)
    
    def add_edge(self, u, v, weight):
        self.graph[u].append((v, weight))
        self.graph[v].append((u, weight))  # Undirected graph
    
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
                    
        return distances, shortest_paths[end]

# Function to load the graph from the CSV traffic data
def load_graph_from_csv(file_path):
    graph = Graph()
    travel_times = {}
    with open(file_path, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            city1 = row['City 1']
            city2 = row['City 2']
            predicted_time_value = float(row['Predicted_Travel_Time'])
            graph.add_edge(city1, city2, predicted_time_value)
            travel_times[(city1, city2)] = predicted_time_value
            travel_times[(city2, city1)] = predicted_time_value  # Since it's an undirected graph
    return graph, travel_times

# Function to find available buses along the shortest path
def find_buses_for_path(path, buses, search_time, travel_times):
    available_buses = []
    total_travel_time = 0.0

    current_time = datetime.strptime(search_time, "%I:%M %p")
    
    for i in range(len(path) - 1):
        start, end = path[i], path[i + 1]
        travel_time = travel_times[(start, end)]
        arrival_time = current_time + timedelta(minutes=travel_time)
        
        found_bus = False
        for _, bus in buses.iterrows():
            bus_stops = [bus['r1'], bus['r2'], bus['r3'], bus['r4'], bus['r5']]
            
            if start in bus_stops and end in bus_stops:
                start_index = bus_stops.index(start)
                end_index = bus_stops.index(end)
                
                if start_index < end_index:  # Ensuring correct direction
                    bus_start_time = datetime.strptime(bus['Starting time'], "%I:%M %p")
                    frequency = timedelta(minutes=bus['Frequency'])
                    
                    while bus_start_time <= current_time:
                        bus_start_time += frequency
                    
                    # Now, bus_start_time is the next available bus after current_time
                    if bus_start_time >= current_time:
                        waiting_time = (bus_start_time - current_time).total_seconds() / 60.0
                        total_travel_time += waiting_time + travel_time

                        # Detailed print statements
                        print(f"From {start} to {end}:")
                        print(f"  Current time: {current_time.strftime('%I:%M %p')}")
                        print(f"  Next bus ({bus['Number']}) at: {bus_start_time.strftime('%I:%M %p')}")
                        print(f"  Waiting time: {waiting_time:.2f} mins")
                        print(f"  Travel time: {travel_time:.2f} mins")
                        print(f"  Arrival time at {end}: {(bus_start_time + timedelta(minutes=travel_time)).strftime('%I:%M %p')}")
                        print(f"  -----------------------------")

                        available_buses.append(f"Bus {bus['Number']} from {start} to {end} at {bus_start_time.strftime('%I:%M %p')}")
                        
                        current_time = bus_start_time + timedelta(minutes=travel_time)
                        found_bus = True
                        break
        
        if not found_bus:
            available_buses.append(f"No bus available from {start} to {end}, consider micro-mobility options.")
            total_travel_time += travel_time
            current_time += timedelta(minutes=travel_time)  # Add micro-mobility time
    
    return available_buses, total_travel_time

# Main function to simulate the entire process
def main():
    # Load bus data
    bus_data_path = "data/output-2.csv"
    bus_data = pd.read_csv(bus_data_path)

    # Sample start and end nodes
    start_node = 'Defence Colony'
    end_node = 'Hauz Khas'
    
    # Search time
    search_time = "08:00 AM"
    
    # Load graph and find shortest path
    g, travel_times = load_graph_from_csv('data/output.csv')
    _, shortest_path = g.dijkstra(start_node, end_node)
    
    # Find available buses and calculate total time
    available_buses, total_travel_time = find_buses_for_path(shortest_path, bus_data, search_time, travel_times)
    
    # Display the result
    print(f"\nThe shortest paths from {start_node} to {end_node} are:")
    print(f"Path : {' -> '.join(shortest_path)}")
    for bus in available_buses:
        print(bus)
    print(f"Total time: {total_travel_time:.2f} mins")

# Run the main function
if __name__ == "__main__":
    main()
