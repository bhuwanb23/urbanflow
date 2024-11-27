from flask import Flask, render_template, request
from datetime import datetime, timedelta
import pandas as pd
import csv
from collections import defaultdict
import heapq

app = Flask(__name__)

class Graph:
    def __init__(self):
        self.graph = defaultdict(list)
    
    def add_edge(self, u, v, weight):
        self.graph[u].append((v, weight))
        self.graph[v].append((u, weight))  # Undirected graph
    
    def dijkstra(self, start, end):
        distances = {node: float('infinity') for node in self.graph}
        distances[start] = 0
        pq = [(0, start)]
        previous = {node: None for node in self.graph}
        
        while pq:
            current_distance, current_vertex = heapq.heappop(pq)
            
            if current_vertex == end:
                path = []
                while current_vertex:
                    path.append(current_vertex)
                    current_vertex = previous[current_vertex]
                return current_distance, path[::-1]
            
            if current_distance > distances[current_vertex]:
                continue
                
            for neighbor, weight in self.graph[current_vertex]:
                distance = current_distance + weight
                
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    previous[neighbor] = current_vertex
                    heapq.heappush(pq, (distance, neighbor))
        
        return float('infinity'), []

def load_graph_from_csv(filename):
    g = Graph()
    travel_times = {}
    
    with open(filename, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            r1, r2, r3, r4, r5 = row['r1'], row['r2'], row['r3'], row['r4'], row['r5']
            
            # Add edges with travel time (assuming 30 minutes between consecutive stops)
            travel_time = 30
            g.add_edge(r1, r2, travel_time)
            travel_times[(r1, r2)] = travel_times[(r2, r1)] = travel_time
            
            g.add_edge(r2, r3, travel_time)
            travel_times[(r2, r3)] = travel_times[(r3, r2)] = travel_time
            
            g.add_edge(r3, r4, travel_time)
            travel_times[(r3, r4)] = travel_times[(r4, r3)] = travel_time
            
            g.add_edge(r4, r5, travel_time)
            travel_times[(r4, r5)] = travel_times[(r5, r4)] = travel_time
    
    return g, travel_times

def parse_time(time_str):
    try:
        return datetime.strptime(time_str, '%I:%M %p')
    except ValueError:
        try:
            return datetime.strptime(time_str, '%H:%M')
        except ValueError:
            return None

def format_time(dt):
    return dt.strftime('%I:%M %p')

def find_buses_for_path(path, bus_data, start_time, travel_times):
    available_buses = []
    detailed_output = []
    current_time = parse_time(start_time)
    total_travel_time = 0
    
    for i in range(len(path) - 1):
        from_stop = path[i]
        to_stop = path[i + 1]
        
        # Find buses for this segment
        segment_buses = []
        for _, row in bus_data.iterrows():
            route = [row['r1'], row['r2'], row['r3'], row['r4'], row['r5']]
            if from_stop in route and to_stop in route:
                if route.index(from_stop) < route.index(to_stop):
                    segment_buses.append({
                        'bus_id': row['ID'],
                        'start_time': row['Starting time'],
                        'frequency': row['Frequency']
                    })
        
        if segment_buses:
            # Regular bus route calculations
            min_wait_time = float('infinity')
            best_bus = None
            
            for bus in segment_buses:
                bus_time = parse_time(bus['start_time'])
                while bus_time < current_time:
                    bus_time = datetime.combine(current_time.date(), 
                                             (bus_time + timedelta(minutes=bus['frequency'])).time())
                
                wait_time = (bus_time - current_time).total_seconds() / 60
                if wait_time < min_wait_time:
                    min_wait_time = wait_time
                    best_bus = bus
            
            # Calculate times
            next_bus_time = current_time + timedelta(minutes=min_wait_time)
            travel_time = travel_times.get((from_stop, to_stop), 30)
            arrival_time = next_bus_time + timedelta(minutes=travel_time)
            
            # Add to output with bus number prominently displayed
            available_buses.append(f"Bus {best_bus['bus_id']} from {from_stop} at {format_time(next_bus_time)}")
            detailed_output.append(
                f"From {from_stop} to {to_stop}:\n"
                f"Bus {best_bus['bus_id']}\n"
                f"Current time: {format_time(current_time)}\n"
                f"Next bus at: {format_time(next_bus_time)}\n"
                f"Waiting time: {min_wait_time:.0f} mins\n"
                f"Travel time: {travel_time} mins\n"
                f"Arrival time at {to_stop}: {format_time(arrival_time)}\n"
                f"----"
            )
            
            current_time = arrival_time
            total_travel_time += min_wait_time + travel_time
            
        else:
            # Alternative transportation
            alt_travel_time = 20  # Maximum time among alternatives
            arrival_time = current_time + timedelta(minutes=alt_travel_time)
            
            detailed_output.append(
                f"From {from_stop} to {to_stop}:\n"
                f"Current time: {format_time(current_time)}\n"
                f"No direct bus available.\n"
                f"Expected arrival at {to_stop}: {format_time(arrival_time)}\n"
                f"----"
            )
            
            # Update current time using the maximum alternative transport time
            current_time = arrival_time
            total_travel_time += alt_travel_time

    return available_buses, detailed_output, total_travel_time
    
def get_valid_locations():
    df = pd.read_csv('data/output-2.csv')
    locations = set()
    for col in ['r1', 'r2', 'r3', 'r4', 'r5']:
        locations.update(df[col].unique())
    return sorted(list(locations))

@app.route('/')
def index():
    current_time = datetime.now().strftime("%H:%M")
    return render_template('index.html', 
                         default_time=current_time,
                         locations=get_valid_locations())

@app.route('/find_route', methods=['POST'])
def find_route():
    source = request.form['source']
    destination = request.form['destination']
    
    # Validate source and destination
    if source == destination:
        return render_template('route.html',
                             error="Source and destination locations cannot be the same. Please choose different locations.",
                             source=source,
                             destination=destination)
    
    # Convert 24-hour time format to 12-hour format
    time_24h = request.form.get('time', '00:00')
    try:
        time_obj = datetime.strptime(time_24h, '%H:%M')
        time_12h = time_obj.strftime("%I:%M %p")
        
        # Load the graph and bus data
        bus_data = pd.read_csv('data/output-2.csv')
        g, travel_times = load_graph_from_csv('data/output-2.csv')
        
        # Find shortest path
        _, shortest_path = g.dijkstra(source, destination)
        
        if not shortest_path:
            raise ValueError("No route found between the specified locations")
        
        # Find available buses and calculate total time
        available_buses, detailed_output, total_travel_time = find_buses_for_path(
            shortest_path, bus_data, time_12h, travel_times)
        
        # Prepare the output
        output = []
        output.append(f"Path: {' -> '.join(shortest_path)}")
        output.extend(detailed_output)
        output.append(f"Total time: {total_travel_time:.0f} mins")
        
        return render_template('route.html',
                             source=source,
                             destination=destination,
                             time=time_12h,
                             available_buses=available_buses,
                             detailed_output=detailed_output,
                             output=output,
                             error=None)
                             
    except Exception as e:
        return render_template('route.html',
                             error=f"An error occurred: {str(e)}")

if __name__ == '__main__':
    app.run(debug=True)