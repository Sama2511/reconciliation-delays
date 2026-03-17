import pyodbc
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.config import load_config

def get_connection(database):
    try:
        config = load_config()
        conn = pyodbc.connect(
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={config['server']};"
            f"DATABASE={database};"
            f"Trusted_Connection={config['trusted_connection']};"
        )
        return conn
    except pyodbc.Error as e:
        print(f"Connection failed: {e}")
        return None
    except KeyError as e:
        print(f"Missing config key: {e}")
        return None




   

# cursor = conn.cursor()

# cursor.execute('SELECT * FROM dbo.F_ECRITUREC')
# rows = cursor.fetchall()
# for row in rows:
#     print(row)

# cursor.close()
# conn.close()
