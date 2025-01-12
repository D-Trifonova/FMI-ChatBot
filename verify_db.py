import sqlite3

def check_data_in_db(db_file):
    try:
        # Connect to the database
        conn = sqlite3.connect(db_file)
        # Create a cursor
        cursor = conn.cursor()

        # Query the scraped_data table
        cursor.execute("SELECT * FROM scraped_data")
        rows = cursor.fetchall()

        # Print the data
        for row in rows:
            # Print ID, title, and URL
            print(f"ID: {row[0]}, Title: {row[1]}, URL: {row[3]}")
            # Print first 100 characters of content
            print(f"Content: {row[2][:100]}...")
            print("\n")

        conn.close()
    except sqlite3.Error as e:
        # Print error message
        print(f"An error occurred while accessing the database: {e}")

if __name__ == '__main__':
    check_data_in_db('chatbot_database.db')
