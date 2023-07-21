#%%
import os
import csv
import sqlite3

# Process parameters
output_subdirectory  = 'downloads'
output_csv_file_name1 = f'{output_subdirectory}/exported_question_data.csv'
output_csv_file_name2 = f'{output_subdirectory}/exported_user_data.csv'



#%%
# Connect to the SQLite database and check what tables are available

conn = sqlite3.connect('instance/flask_basic_app.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
table_names = cursor.fetchall()
print(table_names)



#%%
# Ensure the output subdirectory exists

if not os.path.exists(output_subdirectory):
    os.makedirs(output_subdirectory)
    print("Subdirectory created:", output_subdirectory)
else:
    print("Subdirectory already exists:", output_subdirectory)


#%%
# Export the questions to a CSV file

query = "SELECT * FROM Question"
cursor.execute(query)
rows = cursor.fetchall()

with open(output_csv_file_name1, 'w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(['ID', 'Name', 'Email', 'Question'])
    csv_writer.writerows(rows)


#%%
# Export the users to a CSV file

query = "SELECT id, username, full_name, email FROM User"
cursor.execute(query)
rows = cursor.fetchall()

with open(output_csv_file_name2, 'w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(['ID', 'Username', 'Full Name', 'Email'])
    csv_writer.writerows(rows)



#%%
# Close the cursor and connection
cursor.close()
conn.close()


#%%
# End
