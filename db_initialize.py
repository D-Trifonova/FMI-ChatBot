import sqlite3
import json

# Create a connection to an SQLite database and return the connection object.
# Argument: db_file - Path to the database file.
def create_connection(db_file):
    # Initialize the connection object as None
    conn = None
    try:
        # Creates a connection to the database
        conn = sqlite3.connect(db_file)
    except sqlite3.Error as e:
        print(f"An error occurred while connecting to the database: {e}")  # Print error message
        
    # Return the connection object or None
    return conn

# Execute an SQL script from a given file.
# Arguments: conn - Connection object to the database; sql_file - Path to the SQL script file
def execute_sql_script(conn, sql_file):

    try:
        # Open the SQL file in read mode
        with open(sql_file, 'r') as f:
            # Read the contents of the SQL file and save it in a variable
            sql_script = f.read() 
        
        # Execute the SQL script on the database
        conn.executescript(sql_script)
        # Commit the changes to the database
        conn.commit()
    except sqlite3.Error as e:
        print(f"An error occurred while executing the SQL script: {e}")  # Print error message

# Read JSON file and return data
# Argument: json_file - Path to the JSON file
def read_json_file(json_file):
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data
    except Exception as e:
        print(f"An error occurred while reading the JSON file: {e}")
        return None

# Insert data into the scraped_data table
# Arguments: conn - Connection object to the database; data - Parsed JSON data
def insert_data_to_db(conn, data):
    try:
        cursor = conn.cursor()
        for item in data:
            cursor.execute("INSERT INTO scraped_data (page_title, page_content, page_url) VALUES (?, ?, ?)", 
                           (item['title'], item['content'], item['url']))
        conn.commit()
    except sqlite3.Error as e:
        print(f"An error occurred while inserting data into the database: {e}")

# Initialize the database by creating a connection, executing the SQL script, and inserting JSON data.
def init_db():

    # Create a connection to the database
    conn = create_connection('chatbot_database.db')
    # Check if the connection was successfully established
    if conn:
        # Execute the SQL script to create the tables
        execute_sql_script(conn, 'database_schema.sql')
        
        # Read and insert JSON data
        data = read_json_file('fmi_full_site.json')
        if data:
            insert_data_to_db(conn, data)
        
        # Close the connection to the database
        conn.close()

if __name__ == '__main__':
    # Execute the init_db function if the script is run directly
    init_db()
