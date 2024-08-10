import sqlite3
import csv
import os

def connect_db(db_name):
    """Establish a connection to the SQLite database and return the connection object."""
    return sqlite3.connect(db_name)

def update_table(conn, table_name, column_name, new_value, condition):
    """Update values in a specific table based on a condition."""
    try:
        cursor = conn.cursor()
        sql = f"UPDATE {table_name} SET {column_name} = ? WHERE {condition}"
        cursor.execute(sql, (new_value,))
        conn.commit()
        print(f"Table '{table_name}' updated.")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        cursor.close()

def delete_table(conn, table_name):
    """Delete a table from the database."""
    try:
        cursor = conn.cursor()
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
        conn.commit()
        print(f"Table '{table_name}' deleted.")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        cursor.close()

def show_tables(conn):
    """Show the names of available tables in the database."""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        if tables:
            print("Tables available:")
            for table in tables:
                print(table[0])
        else:
            print("No tables found.")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        cursor.close()

def create_table(conn, table_name, columns):
    """Create a new table with user-defined columns."""
    try:
        cursor = conn.cursor()
        columns_definition = ', '.join(columns)
        sql = f"CREATE TABLE {table_name} ({columns_definition})"
        cursor.execute(sql)
        conn.commit()
        print(f"Table '{table_name}' created.")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        cursor.close()

def insert_from_csv(conn, table_name, csv_file_path):
    """Insert data from a CSV file into the specified table."""
    if not os.path.isfile(csv_file_path):
        print(f"CSV file '{csv_file_path}' does not exist.")
        return
    
    try:
        with open(csv_file_path, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            headers = next(csv_reader)
            placeholders = ', '.join(['?'] * len(headers))
            sql = f"INSERT INTO {table_name} ({', '.join(headers)}) VALUES ({placeholders})"
            
            cursor = conn.cursor()
            for row in csv_reader:
                cursor.execute(sql, row)
            conn.commit()
            print(f"Data from '{csv_file_path}' inserted into table '{table_name}'.")
    except (sqlite3.Error, FileNotFoundError) as e:
        print(f"An error occurred: {e}")
    finally:
        cursor.close()

def get_user_input_for_table():
    """Get table name and column definitions from the user."""
    table_name = input("Enter the table name: ")
    print("Enter columns in the format 'column_name column_type'. Type 'done' when finished:")
    
    columns = []
    while True:
        column_input = input("Column definition: ")
        if column_input.lower() == 'done':
            break
        columns.append(column_input)
    
    return table_name, columns

def get_column_info(db_path, table_name):
    """
    Retrieve column names and their data types from a specified table in an SQLite database.

    Parameters:
    - db_path (str): Path to the SQLite database file.
    - table_name (str): Name of the table to query.

    Returns:
    - list of tuples: Each tuple contains (column_name, data_type).
    """
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns_info = cursor.fetchall()
            result = [(row[1], row[2]) for row in columns_info]
            return result

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return []

def show_first_n_records(db_path, table_name, n=5):
    """
    Show the first N records from a specified table in the SQLite database.

    Parameters:
    - db_path (str): Path to the SQLite database file.
    - table_name (str): Name of the table to query.
    - n (int): Number of records to show. Default is 5.

    Returns:
    - None
    """
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {table_name} LIMIT ?", (n,))
            records = cursor.fetchall()
            
            if records:
                print(f"First {n} records from table '{table_name}':")
                for record in records:
                    print(record)
            else:
                print(f"No records found in table '{table_name}'.")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

def main_menu():
    """Display the main menu and handle user choices."""
    db_name = 'data.db'
    conn = connect_db(db_name)

    while True:
        print("\nMenu:")
        print("1. Show available tables")
        print("2. Create a new table")
        print("3. Insert data from CSV file")
        print("4. Update table values")
        print("5. Delete a table")
        print("6. Show columns with data types")
        print("7. Show first 5 records of a table")
        print("8. Show dimensions of a table")
        print("9. Exit")

        choice = input("Choose an option (1-9): ")

        if choice == '1':
            show_tables(conn)
        elif choice == '2':
            table_name, columns = get_user_input_for_table()
            create_table(conn, table_name, columns)
        elif choice == '3':
            table_name = input("Enter the table name to insert data into: ")
            csv_file_path = input("Enter the path to the CSV file: ")
            insert_from_csv(conn, table_name, csv_file_path)
        elif choice == '4':
            table_name = input("Enter the table name to update: ")
            column_name = input("Enter the column name to update: ")
            new_value = input("Enter the new value: ")
            condition = input("Enter the condition (e.g., 'id = 1'): ")
            update_table(conn, table_name, column_name, new_value, condition)
        elif choice == '5':
            table_name = input("Enter the table name to delete: ")
            delete_table(conn, table_name)
        elif choice == '6':
            table_name = input("Enter the table name: ")
            column_info = get_column_info(db_name, table_name)
            print("Column Names and Data Types:")
            for column, data_type in column_info:
                print(f"{column}: {data_type}")
        elif choice == '7':
            table_name = input("Enter the table name: ")
            show_first_n_records(db_name, table_name, n=5)
        elif choice == '8':
            table_name = input("Enter the table name: ")
            rows, columns = get_table_info(db_name, table_name)
            if rows is not None and columns is not None:
                print(f"Number of rows: {rows}")
                print(f"Number of columns: {columns}")
            else:
                print("Could not retrieve table information.")
        elif choice == '9':
            print("Exiting...")
            conn.close()
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 9.")

if __name__ == "__main__":
    main_menu()
