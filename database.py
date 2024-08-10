import sqlite3
import pandas as pd

def load_csv_to_sqlite(csv_file, db_file):
    """Load CSV data into an SQLite database."""
    # Load CSV into DataFrame
    bus_data = pd.read_csv(csv_file)
    
    # Connect to SQLite database (or create one if it doesn't exist)
    conn = sqlite3.connect(db_file)
    
    # Create table schema based on CSV
    conn.execute('''
        CREATE TABLE IF NOT EXISTS buses (
            ID TEXT,
            Number INTEGER,
            r1 TEXT,
            r2 TEXT,
            r3 TEXT,
            r4 TEXT,
            r5 TEXT,
            StartingTime TEXT,
            Frequency INTEGER
        )
    ''')
    
    # Load data into table
    bus_data.to_sql('buses', conn, if_exists='replace', index=False)
    
    conn.commit()
    conn.close()

def find_buses(start_stop, end_stop, input_time):
    """Find buses running between start and end stops within a specified time."""
    # Connect to SQLite database
    conn = sqlite3.connect('data.db')
    
    # Check the table schema to verify column names
    schema_query = 'PRAGMA table_info(buses);'
    schema = conn.execute(schema_query).fetchall()
    print("Table Schema:", schema)  # Print schema for debugging

    # Construct query to find buses running through start and end stops
    query = f'''
    WITH SelectedPaths AS (
        SELECT DISTINCT r1 AS stop_name FROM buses
        UNION
        SELECT DISTINCT r2 AS stop_name FROM buses
        UNION
        SELECT DISTINCT r3 AS stop_name FROM buses
        UNION
        SELECT DISTINCT r4 AS stop_name FROM buses
        UNION
        SELECT DISTINCT r5 AS stop_name FROM buses
    ),
    UserInput AS (
        SELECT '{input_time}' AS input_time, '{start_stop}' AS start_stop, '{end_stop}' AS end_stop
    )
    SELECT b.ID, b.Number, b.r1, b.r2, b.r3, b.r4, b.r5, b.StartingTime, b.Frequency
    FROM buses b
    JOIN SelectedPaths sp ON (b.r1 = sp.stop_name OR b.r2 = sp.stop_name OR b.r3 = sp.stop_name OR b.r4 = sp.stop_name OR b.r5 = sp.stop_name)
    WHERE (
        (b.r1 = UserInput.start_stop OR b.r2 = UserInput.start_stop OR b.r3 = UserInput.start_stop OR b.r4 = UserInput.start_stop OR b.r5 = UserInput.start_stop)
        AND (b.r1 = UserInput.end_stop OR b.r2 = UserInput.end_stop OR b.r3 = UserInput.end_stop OR b.r4 = UserInput.end_stop OR b.r5 = UserInput.end_stop)
        AND b.StartingTime BETWEEN datetime(UserInput.input_time) AND datetime(UserInput.input_time, '+2 hour')
    )
    ORDER BY b.StartingTime;
    '''
    
    # Execute the query
    try:
        results = conn.execute(query).fetchall()
        # Print the results
        print(f"Buses running from {start_stop} to {end_stop} within the time window:")
        for row in results:
            print(f"ID: {row[0]}, Number: {row[1]}, Route: {row[2]} -> {row[3]} -> {row[4]} -> {row[5]} -> {row[6]}, Starting Time: {row[7]}, Frequency: {row[8]}")
    except sqlite3.OperationalError as e:
        print(f"Query failed: {e}")
    
    conn.close()

def main():
    csv_file = 'data/buses-data.csv'
    db_file = 'data.db'
    
    # Load CSV data into SQLite database
    load_csv_to_sqlite(csv_file, db_file)
    
    # User input
    start_stop = 'Kovur'
    end_stop = 'Defence Colony'
    input_time = '2024-08-10 08:00:00'
    
    # Find and display buses
    find_buses(start_stop, end_stop, input_time)

if __name__ == '__main__':
    main()
