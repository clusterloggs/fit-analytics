"""
Utility script to inspect the SQLite database contents
"""
import os
import pandas as pd
from sqlalchemy import create_engine, inspect
from config import DATABASE_FILE

def check_db():
    # 1. Verify file exists
    if not os.path.exists(DATABASE_FILE):
        print(f"❌ Database file not found at: {DATABASE_FILE}")
        print("   Please run 'python pipeline.py' first.")
        return

    print(f" Database found at: {DATABASE_FILE}")
    
    # 2. Connect to database
    # Windows paths need to be converted for SQLAlchemy URI
    db_path = str(DATABASE_FILE).replace('\\', '/')
    engine = create_engine(f"sqlite:///{db_path}")
    
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    if not tables:
        print("Database exists but contains no tables.")
        return

    print(f"Found {len(tables)} tables: {', '.join(tables)}")
    print("=" * 60)

    # 3. Print details for each table
    for table in tables:
        print(f"\nTable: {table}")
        print("-" * 60)
        
        try:
            # Read entire table to get count and sample
            df = pd.read_sql_table(table, engine)
            
            print(f"Columns: {list(df.columns)}")
            print(f"Total Records: {len(df)}")
            
            if not df.empty:
                print("\nMost recent 3 records:")
                # Sorting by date if available, otherwise just tail
                if 'date' in df.columns:
                    print(df.sort_values('date').tail(3).to_string(index=False))
                else:
                    print(df.tail(3).to_string(index=False))
            else:
                print("   (Table is empty)")
                
        except Exception as e:
            print(f"Error reading table {table}: {e}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    check_db()
