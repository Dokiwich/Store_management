import os
from dotenv import load_dotenv
import mysql.connector

def update_schema():
    load_dotenv()
    
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "laptop_shop_pro")
    )
    cursor = conn.cursor()
    
    alter_queries = [
        "ALTER TABLE products ADD COLUMN sku VARCHAR(100) UNIQUE;",
        "ALTER TABLE products ADD COLUMN spec_max_ram VARCHAR(50);",
        "ALTER TABLE products ADD COLUMN spec_panel VARCHAR(50);",
        "ALTER TABLE products ADD COLUMN spec_brightness VARCHAR(50);",
        "ALTER TABLE products ADD COLUMN spec_battery VARCHAR(50);",
        "ALTER TABLE products ADD COLUMN spec_color VARCHAR(50);",
        "ALTER TABLE products ADD COLUMN warranty_time VARCHAR(50);",
        "ALTER TABLE products ADD COLUMN condition_status VARCHAR(50) DEFAULT 'New';",
        "ALTER TABLE products ADD COLUMN short_description TEXT;",
        "ALTER TABLE products ADD COLUMN highlights TEXT;",
        "ALTER TABLE products ADD COLUMN min_stock INT DEFAULT 5;",
    ]
    
    for query in alter_queries:
        try:
            print(f"Executing: {query}")
            cursor.execute(query)
        except mysql.connector.Error as err:
            if err.errno == 1060: # Duplicate column name
                print(f"Column already exists: {err.msg}")
            else:
                print(f"Error: {err}")
    
    conn.commit()
    cursor.close()
    conn.close()
    print("Database schema update finished.")

if __name__ == "__main__":
    update_schema()
