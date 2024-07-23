import sqlite3
import pymysql

# Connect to the source SQLite database
source_conn = sqlite3.connect(r'D:\study\5th sem  it\Internship II\Student_Web_Portal_3rd_Sem\db.sqlite3')
source_cursor = source_conn.cursor()

# Connect to the destination MySQL database
dest_conn = pymysql.connect(
    host='localhost',
    user='studentw',
    password='project_to_manage_students',
    db='studentweb'
)
dest_cursor = dest_conn.cursor()

# Function to copy table data
def copy_table_data(table_name):
    # Read data from source database
    source_cursor.execute(f"SELECT * FROM {table_name}")
    rows = source_cursor.fetchall()

    # Get column names
    column_names = [description[0] for description in source_cursor.description]

    # Create a placeholder string for inserting data
    placeholders = ', '.join(['%s' for _ in column_names])

    # Insert data into destination database
    insert_query = f"INSERT INTO {table_name} ({', '.join(column_names)}) VALUES ({placeholders})"
    dest_cursor.executemany(insert_query, rows)

    # Commit the changes
    dest_conn.commit()

# List of tables to copy
tables = [
    # 'user_user_user_permissions',

    'auth_group',
    'auth_group_permissions',
    'user_user_groups',
    ]

complete = [
        'user_user',
    'faculty_faculty_records',
    'main_sub_syllabus',
    'main_gtuexam',
    'Student_app_student',
    'Student_app_student_marks',
]

# Copy data for each table
for table in tables:
    copy_table_data(table)

# Close the connections
source_conn.close()
dest_conn.close()

print("Data copied successfully!")
