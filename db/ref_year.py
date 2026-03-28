import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.connection import get_connection




def get_ref_year(database):
    conn = None
    try:
        conn = get_connection(database)
        if not conn:
            return False
        cursor = conn.cursor()
        cursor.execute("SELECT D_Commentaire FROM dbo.P_DOSSIER")
        res = cursor.fetchall()

        return res
    except AttributeError:
        print('Error fetching the data')
        return None
    except Exception as e:
        print(f"Error:{e}")
        return None
    finally:
        if conn:
            conn.close()



    


    

