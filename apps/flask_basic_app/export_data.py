#%%
import os
import csv
import sqlite3

# Process parameters
output_subdirectory  = 'instance'
input_database = f'{output_subdirectory}/flask_basic_app.db'


#%%
# Connect to the SQLite database and check what tables are available

conn = sqlite3.connect(input_database)
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
table_names = cursor.fetchall()
table_names = [t[0] for t in table_names]
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

for t in table_names:
    output_csv_file_name = f'{output_subdirectory}/exported_data_{t}.csv'
    print(f"Export Results for Table {t} --> {output_csv_file_name}")

    query = f"SELECT * FROM {t} WHERE 1=2"
    cursor.execute(query)
    rows = cursor.fetchall()
    column_names = [column[0] for column in cursor.description if column[0] not in ['password']]

    query = f"SELECT { ', '.join(column_names) } FROM {t}"
    cursor.execute(query)
    rows = cursor.fetchall()

    with open(output_csv_file_name, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(column_names)
        csv_writer.writerows(rows)


#%%
# Close the cursor and connection
cursor.close()
conn.close()


#%%
# End
