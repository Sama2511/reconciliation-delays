import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db.connection import get_connection



def fetch_dbs():
    conn= None
    try:
        conn = get_connection('master')
        if not conn:
            return None
        cursor = conn.cursor()
        cursor.execute('SELECT name FROM sys.databases')
        data = cursor.fetchall()
        dbs =[]
        for db in data:
            dbs.append(db[0])
        return dbs
    except AttributeError:
        print("Error fetching the databases")
        return None
    finally:
        if conn:
            conn.close()


