
from db.connection import get_connection



def fetch_dbs():

    try:
        conn = get_connection('master')
        cursor = conn.cursor()
        cursor.execute('SELECT name FROM sys.databases')
        data = cursor.fetchall()
        dbs =[]
        for db in data:
            dbs.append(db[0])
        print(dbs)
        return dbs
    except AttributeError:
        print("Error fetching the databases")
        return None
    finally:
        conn.close()


