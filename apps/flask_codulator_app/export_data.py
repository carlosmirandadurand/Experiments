#%%
import sqlite3
import csv

#%%
# Connect to the SQLite database
conn = sqlite3.connect('instance/questions.db')

# Create a cursor object to execute SQL queries
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
table_names = cursor.fetchall()
print(table_names)


#%%
# Execute a query to fetch the data from the table
query = "SELECT * FROM Question"
cursor.execute(query)

# Fetch all the rows returned by the query
rows = cursor.fetchall()

#%%
# Define the CSV file path
csv_file_path = 'exported_question_data.csv'

# Write the fetched rows to a CSV file
with open(csv_file_path, 'w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file)
    # Write the header row
    csv_writer.writerow(['ID', 'Name', 'Email', 'Question'])
    # Write the data rows
    csv_writer.writerows(rows)

#%%
# Close the cursor and connection
cursor.close()
conn.close()


#%%
# End
