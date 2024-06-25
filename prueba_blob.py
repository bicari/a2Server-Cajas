import pyodbc
import time

connect = pyodbc.connect("""DSN=A2GKC;DRIVER={C:\Program Files (x86)\DBISAM 4 ODBC-CS\libs\dbodbc\read-write\win64\dbodbc.dll};
                         ConnectionType=Local;RemoteIPAddress=127.0.0.1;RemotePort=12005;RemoteCompression=0;RemotePing=False;RemotePingInterval=60;RemoteEncryption=False;RemoteEncryptionPassword=elevatesoft;RemoteReadAhead=50;
                         CatalogName=C:\\a2CA2020\\Empre001\\Data;ReadOnly=False;LockRetryCount=15;LockWaitTime=100;ForceBufferFlush=False;StrictChangeDetection=False;PrivateDirectory=C:\\a2CA2020\\Empre001\\Data""")
cursor = connect.cursor()
cursor.execute(""" CREATE TABLE IF NOT EXISTS "C:/a2CA2020/Empre001/Data/BLOB_TEMP"
(
   "FTI_DOCUMENTO" VARCHAR(30),
   "FTI_FORMADEPAGO" BLOB,
PRIMARY KEY ("RecordID") COMPRESS FULL
LOCALE CODE 0
USER MAJOR VERSION 1
);



""")
#cursor.close()
time.sleep(3)
#connect2 = pyodbc.connect('DSN=A2GKC')
#cursor2 = connect.cursor()


try:
    cursor.execute("""INSERT INTO "C:/a2CA2020/Empre001/Data/BLOB_TEMP" (FTI_DOCUMENTO, FTI_FORMADEPAGO)
                  SELECT FTI_DOCUMENTO, FTI_FORMADEPAGO
                  FROM "C:/a2CA2020/Empre001/Data/SOPERACIONINV" 
                  WHERE FTI_AUTOINCREMENT = '' """)
    cursor.commit()
    
except Exception as e:
    print(e)
