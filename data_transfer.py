import sqlite3

# Connect to the source database (database with data)
source_conn = sqlite3.connect(r'D:\study\5th sem  it\Internship II\Student_Web_Portal_3rd_Sem\maindb.sqlite3')
source_cursor = source_conn.cursor()

# Connect to the destination database (empty database)
dest_conn = sqlite3.connect(r'D:\study\5th sem  it\Internship II\Student_Web_Portal_3rd_Sem\db.sqlite3')
dest_cursor = dest_conn.cursor()

# Function to copy table data
def copy_table_data(table_name):
    # Read data from source database
    source_cursor.execute(f"SELECT * FROM {table_name}")
    rows = source_cursor.fetchall()

    # Get column names
    column_names = [description[0] for description in source_cursor.description]

    # Create a placeholder string for inserting data
    placeholders = ', '.join(['?' for _ in column_names])

    # Insert data into destination database
    insert_query = f"INSERT INTO {table_name} ({', '.join(column_names)}) VALUES ({placeholders})"
    dest_cursor.executemany(insert_query, rows)

    # Commit the changes
    dest_conn.commit()

# Copy data for main_gtuexam table
# copy_table_data('main_gtuexam')
# copy_table_data('main_sub_syllabus')
# copy_table_data('Student_app_student')
# copy_table_data('faculty_faculty_records')
# copy_table_data('Student_app_student_marks')
# copy_table_data('user_user')
# copy_table_data('user_user_groups')
# copy_table_data('user_user_permissions')
copy_table_data('auth_group')
copy_table_data('auth_group_permissions')

# Close the connections
source_conn.close()
dest_conn.close()

print("Data copied successfully!")
