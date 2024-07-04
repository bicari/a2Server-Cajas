import asyncio
import pyodbc
import pathlib
import os
import time
import glob
import zipfile
from datetime import datetime

class sqlQuerys:
    def __init__(self, dsn= None):
        self.dsn = pyodbc.connect(dsn)
        
        #self.string = self.search_database_files() 


    def connection(self):
        return self.dsn    

    def search_sales(self, serie, auto) -> int | bool:
        try:
            max_auto = self.connection().execute(f"""SELECT MAX(FTI_AUTOINCREMENT)
                                FROM SOPERACIONINV 
                                WHERE FTI_STATUS = 1  AND FTI_TIPO = 11 AND FTI_SERIE = '{serie.upper()}' 
                                AND FTI_FECHAEMISION = '{str(datetime.date(datetime.now()))}' """).fetchone()
            if max_auto[0] > int(auto):
                print(str(datetime.date(datetime.now())))
                items_to_udpdate = self.connection().execute(f"""SELECT 
                                                                    FDI_CODIGO AS CODIGO,
                                                                    SUM(CASE WHEN FDI_TIPOOPERACION = 11 THEN FDI_CANTIDAD * (-1)
                                                                        WHEN FDI_TIPOOPERACION = 12 THEN FDI_CANTIDAD 
                                                                        END) AS CANTIDAD
                                                                FROM SDETALLEVENTA
                                                                WHERE FDI_OPERACION_AUTOINCREMENT = {max_auto[0]} AND FDI_TIPOOPERACION IN (11,12) 
                                                                AND FDI_FECHAOPERACION = '{str(datetime.date(datetime.now()))}'
                                                                GROUP BY CODIGO
                                                         
                                        """).fetchall()  
            print(items_to_udpdate, 'por aqui', max_auto) 
            return max_auto, items_to_udpdate
        except Exception as e:
            print(e)
            return False

    async def update_tablas_locales(self, auto_so, auto_sd):
        try:
            print(auto_so, auto_sd)
            self.connection().execute(f"""UPDATE SOPERACIONINV SET FTI_AUTOINCREMENT = FTI_AUTOINCREMENT + {auto_so}""")
            self.connection().execute(f"""UPDATE SDETALLEVENTA SET FDI_AUTOINCREMENT = FDI_AUTOINCREMENT + {auto_sd}""")
            self.connection().execute(f"""UPDATE SDETALLEVENTA SET FDI_OPERACION_AUTOINCREMENT = FTI_AUTOINCREMENT
                                          FROM SDETALLEVENTA 
                                          INNER JOIN SOPERACIONINV ON FTI_DOCUMENTO = FDI_DOCUMENTO
                                          WHERE FDI_DOCUMENTO = FTI_DOCUMENTO""")
            self.connection().commit()
            
            self.connection().close()
        except Exception as e:    
            print(e)

    async def max_Auto(self) -> tuple | Exception:
        try:
            max_auto = self.connection().execute("SELECT MAX(FTI_AUTOINCREMENT) FROM SOPERACIONINV").fetchone()[0]
            max_auto_detalle = self.connection().execute("SELECT MAX(FDI_AUTOINCREMENT) FROM SDETALLEVENTA").fetchone()[0]
            self.connection().close()
            return (max_auto , max_auto_detalle)
        except Exception as e:
            return e
        

    def filter_client(self, id:str):
        clients = self.connection().execute(f"SELECT FC_CODIGO FROM SCLIENTES WHERE FC_CODIGO = '{id}'").fetchall()
        for client in clients:
            if client.FC_CODIGO == id:
                fini = time.time()
                self.dsn.close() 
                return client
            
    async def insert_client(self, *args)-> bool | pyodbc.Error:
        pass

    