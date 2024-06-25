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
        self.dsn = pyodbc.connect(f'DSN={dsn}')
        
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

    def filter_client(self, id:str):
        clients = self.connection().execute(f"SELECT FC_CODIGO FROM SCLIENTES WHERE FC_CODIGO = '{id}'").fetchall()
        for client in clients:
            if client.FC_CODIGO == id:
                fini = time.time()
                self.dsn.close() 
                return client
            
    async def insert_client(self, *args)-> bool | pyodbc.Error:
        pass

    