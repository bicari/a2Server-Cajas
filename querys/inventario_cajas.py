import asyncio
import pyodbc
import pathlib
from datetime import datetime

async def query_max_auto(serie, name:str):
    with pyodbc.connect("DSN=A2GKC") as connection:
        try:
            cursor = connection.cursor()
            row=cursor.execute(f"""SELECT MAX(FTI_AUTOINCREMENT), FTI_SERIE
                                FROM SOPERACIONINV 
                                WHERE FTI_STATUS = 1  AND FTI_TIPO = 11 AND FTI_SERIE IN {serie} 
                                AND FTI_FECHAEMISION = '{str(datetime.date(datetime.now()))}' 
                                GROUP BY FTI_SERIE""").fetchall()
            #auto = await lastAuto(serie)
        except Exception as e:
             print(e)   
             return []
        return row


async def query_detalle_operacion(serie, auto):
    with pyodbc.connect("DSN=A2GKC") as connection:
        try:
            cursor = connection.cursor()
            row = cursor.execute(f"""SELECT 
                                        FDI_CANTIDAD, FDI_CODIGO 
                                    FROM SDETALLEVENTA
                                    WHERE FDI_OPERACION_AUTOINCREMENT = {auto}  """)
        except Exception as e:
            print(e)
        finally:
            cursor.close()        
