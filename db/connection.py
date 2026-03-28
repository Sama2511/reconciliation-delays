import pyodbc
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.config import load_config

def get_connection(database):
    try:
        config = load_config()
        if config['auth_type'] == 'Windows Authentication':
            conn = pyodbc.connect(
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={config['server']};"
                f"DATABASE={database};"
                f"Trusted_Connection=yes;",
                timeout=5
            )
        else:
            conn = pyodbc.connect(
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={config['server']};"
                f"DATABASE={database};"
                f"UID={config['username']};"
                f"PWD={config['password']};",
                timeout=5
            )
        return conn
    except pyodbc.Error as e:
        print(f"Connection failed: {e}")
        return None
    except KeyError as e:
        print(f"Missing config key: {e} getconnection")
        return None

def test_connection_sql_auth(database,server,username,password):
    try:

        conn = pyodbc.connect(
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={server};"
                f"DATABASE={database};"
                f"UID={username};"
                f"PWD={password};",
                timeout=5
            )
        return conn
    except pyodbc.Error as e:
        print(f"Connection failed: {e}")
        return None
    except KeyError as e:
        print(f"Missing config key: {e}")
        return None
    
def test_connection_win_auth(database,server):
    try:
        conn = pyodbc.connect(
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={server};"
                f"DATABASE={database};"
                f"Trusted_Connection=yes;",
                timeout=5
            )
        return conn
    except pyodbc.Error as e:
        print(f"Connection failed: {e}")
        return None
    except KeyError as e:
        print(f"Missing config key: {e} testconnection")
        return None

   

