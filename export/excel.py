import pandas as pd

def export_to_excel(data, file_path):
    try:
        df = pd.DataFrame(data)
        df.to_excel(file_path, index=False)
        return True
    except AttributeError:
        print("No data to export")
        return False
    except ValueError:
        print("Invalid file format. use .xlsx")
        return False
    except PermissionError:
        print("File is open in Excel. close it and try again")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False
