import mysql.connector
from mysql.connector import Error
import random
import string
from datetime import datetime, timedelta

# Function to create a connection to MySQL
def connect_mysql(host, user, password, database=None):
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

# Function to create the database and table
def create_database_and_table(connection):
    cursor = connection.cursor()

    # Create the database if it doesn't exist
    cursor.execute("CREATE DATABASE IF NOT EXISTS test_db")
    cursor.execute("USE test_db")

    # Create the table
    # create_table_query = """
    # CREATE TABLE IF NOT EXISTS transactions (
    #     user_id INT AUTO_INCREMENT PRIMARY KEY,
    #     transaction_id INT,
    #     username VARCHAR(50),
    #     amount DECIMAL(10, 2),
    #     date DATE
    # )
    # """
    create_table_query = """CREATE TABLE user_activity (
        id INT AUTO_INCREMENT PRIMARY KEY,         -- Unique identifier for each activity
        user_id INT NOT NULL,                      -- User ID to identify the user
        activity_type VARCHAR(100) NOT NULL,       -- Type of activity (e.g., login, purchase, comment)
        activity_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Time when the activity happened
        metadata JSON,                             -- Additional metadata (e.g., device info, location)
        is_successful BOOLEAN DEFAULT TRUE         -- Whether the activity was successful
    );
    """
    insert_table_query = """INSERT INTO user_activity (user_id, activity_type, metadata, is_successful)
    VALUES 
    (1, 'login', '{"device": "mobile", "location": "New York"}', TRUE),
    (2, 'purchase', '{"item": "Laptop", "price": 1200}', TRUE),
    (3, 'comment', '{"post_id": 45, "comment_text": "Great article!"}', TRUE),
    (4, 'login', '{"device": "desktop", "location": "San Francisco"}', TRUE),
    (5, 'purchase', '{"item": "Headphones", "price": 150}', TRUE),
    (6, 'comment', '{"post_id": 13, "comment_text": "Thanks for sharing!"}', TRUE),
    (7, 'login', '{"device": "mobile", "location": "Los Angeles"}', FALSE),
    (8, 'purchase', '{"item": "Smartphone", "price": 800}', TRUE),
    (9, 'comment', '{"post_id": 30, "comment_text": "Interesting read."}', TRUE),
    (10, 'login', '{"device": "tablet", "location": "Chicago"}', TRUE),
    (11, 'purchase', '{"item": "Keyboard", "price": 70}', TRUE),
    (12, 'comment', '{"post_id": 50, "comment_text": "Good insights."}', TRUE);
    """
    
    cursor.execute(create_table_query)
    cursor.execute(insert_table_query)
    connection.commit()

# Function to generate random values and insert into the table
def insert_random_values(connection, num_entries=12):
    cursor = connection.cursor()

    # Generating random values
    for _ in range(num_entries):
        transaction_id = random.randint(1000, 9999)
        username = ''.join(random.choices(string.ascii_letters, k=8))
        amount = round(random.uniform(10.00, 500.00), 2)
        random_days = random.randint(1, 365)
        date = (datetime.now() - timedelta(days=random_days)).date()

        insert_query = """
        INSERT INTO transactions (transaction_id, username, amount, date)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(insert_query, (transaction_id, username, amount, date))

    connection.commit()

def show_values(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM user_activity")
    
    # Fetch all the records
    records = cursor.fetchall()

    # Display the records
    print("Inserted Records:")
    for record in records:
        print(record)

# Main function
def main():
    # Connect to MySQL
    connection = connect_mysql(host, user, password, 'test_db')

    if connection:
        # Create database and table
        # create_database_and_table(connection)
        
        # Insert random values
        # insert_random_values(connection, 12)
        # print("Inserted 12 random values into the database.\n")

        show_values(connection)

        # Close the connection
        connection.close()
    else:
        print("Failed to connect to MySQL.")

if __name__ == "__main__":
    main()
