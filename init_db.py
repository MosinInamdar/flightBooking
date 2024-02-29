import sqlite3

# Establish connection to the database
connection = sqlite3.connect('flightBooking.db')

# Open and execute the SQL script
with open('schema.sql') as f:
    connection.executescript(f.read())

# Commit the transaction
connection.commit()

# Close the connection
connection.close()
