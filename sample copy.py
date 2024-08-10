import pandas as pd
import heapq

# Load data from CSV files
def load_data():
    traffic_data = pd.read_csv('data\traffic_data.csv')
    buses = pd.read_csv('data\buses.csv')
    routes = pd.read_csv('data\routes.csv')
    return traffic_data, buses, routes

# Construct the graph from traffic data
def construct_graph(traffic_data):
    graph = {}
    for _, row in traffic_data.iterrows():
        city1 = row['City 1']
        city2 = row['City 2']
        travel_time = row['Predicted_Travel_Time']
        
        if city1 not in graph:
            graph[city1] = {}
        if city2 not in graph:
            graph[city2] = {}
        
        graph[city1][city2] = travel_time
        graph[city2][city1] = travel_time  # Assuming undirected graph for bidirectional paths

    return graph

# Dijkstra's algorithm to find the shortest path
def dijkstra(graph, start, end):
    queue = [(0, start)]
    distances = {node: float('inf') for node in graph}
    distances[start] = 0
    previous_nodes = {node: None for node in graph}
    
    while queue:
        current_distance, current_node = heapq.heappop(queue)
        
        if current_node == end:
            break
        
        for neighbor, weight in graph[current_node].items():
            distance = current_distance + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous_nodes[neighbor] = current_node
                heapq.heappush(queue, (distance, neighbor))
    
    path = []
    while end:
        path.append(end)
        end = previous_nodes[end]
    path.reverse()
    
    return path, distances[path[-1]]

# Get transport availability and stops for a given path
def get_transport_availability(path, buses, routes):
    transport_info = []
    
    for i in range(len(path) - 1):
        start_city = path[i]
        end_city = path[i + 1]
        
        # Find relevant routes
        relevant_routes = routes[(routes['City 1'] == start_city) & (routes['City 2'] == end_city)]
        
        for _, route in relevant_routes.iterrows():
            route_id = route['ID']
            
            # Check available transport modes
            available_transports = []
            
            # Check Bus availability
            buses_on_route = buses[buses['ID'].isin(route['Bus Stop'].split(','))]
            for _, bus in buses_on_route.iterrows():
                num_stops = len(buses[buses['ID'] == bus['ID']])
                available_transports.append({
                    'Transport': 'Bus',
                    'Number': bus['Number'],
                    'Stops': num_stops,
                })
            
            transport_info.append({
                'RouteID': route_id,
                'StartCity': start_city,
                'EndCity': end_city,
                'AvailableTransports': available_transports,
            })
    
    return transport_info

def main():
    # Load data
    traffic_data, buses, routes = load_data()
    
    # Construct the graph from traffic data
    graph = construct_graph(traffic_data)
    
    # Define the start and end cities
    start_city = 'CityA'
    end_city = 'CityD'
    
    # Calculate shortest path
    path, _ = dijkstra(graph, start_city, end_city)
    print("Shortest Path:", path)
    
    # Get transport availability along the path
    transport_availability = get_transport_availability(path, buses, routes)
    
    for info in transport_availability:
        print(f"From {info['StartCity']} to {info['EndCity']}, Route ID: {info['RouteID']}")
        for transport in info['AvailableTransports']:
            print(f"  Transport Type: {transport['Transport']}, Number: {transport['Number']}, Stops: {transport['Stops']}")

if __name__ == "__main__":
    main()
