import pandas as pd

def export_to_excel(data, file_path):
    try:
        df = pd.DataFrame(data)
        df.to_excel(file_path, index=False)
        return True
    except AttributeError:
        print("Aucune donnée à exporter")
        return False
    except ValueError:
        print("Format de fichier invalide. Utilisez .xlsx")
        return False
    except PermissionError:
        print("Le fichier est ouvert dans Excel. Fermez-le et réessayez")
        return False
    except Exception as e:
        print(f"Erreur inattendue: {e}")
        return False
