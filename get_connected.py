import pyodbc
server = 'epqtimeclock.database.windows.net'
database = 'EPQTimeClockdb'
username = 'Dap_1223'
password = 'Divyesh12'   
driver= '{ODBC Driver 17 for SQL Server}'
def get_connected():
    return pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password)
 
