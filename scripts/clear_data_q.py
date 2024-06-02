import os
import django
from django.db import connections
from django.apps import apps

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project.settings')
django.setup()

def clear_q_database():
    connection = connections['q']
    cursor = connection.cursor()

    # Disable foreign key checks to avoid issues while deleting
    cursor.execute("PRAGMA foreign_keys = OFF;")
    
    # Get all table names in the 'q' database
    table_names = connection.introspection.table_names()
    
    # Delete all rows from each table
    for table_name in table_names:
        cursor.execute(f"DELETE FROM {table_name};")
    
    # Re-enable foreign key checks
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    connection.commit()
    cursor.close()

if __name__ == "__main__":
    clear_q_database()
    print("All rows have been deleted from all tables in the 'q' database.")
