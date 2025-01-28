import pyodbc
import time
from datetime import datetime
from os import path


class sqlQuerys:
    def __init__(self, dsn= None):
        self.dsn = pyodbc.connect(dsn)

    def connection(self):
        return self.dsn    

    def update_sempresas_a2cash(self, path_data_local, path_local_formatos_config):#Funcion que actualiza la tabla sempresas con los directorios locales FILECONFIG, CONFIGR, USERSCONFIG 
        try:
            self.connection().execute(f"""UPDATE SEMPRESAS SET FE_STATUS = 0, FE_DIRDATOS ='{path_data_local}', FE_DIRSISTEMA='{path_local_formatos_config}\\FILECONFIG', 
                                      FE_DIRFORMAS='{path_local_formatos_config}\\USERSCONFIG', FE_DIRFORMATOS='{path_local_formatos_config}\\CONFIGR',
                                      FE_TIPOCONEXION = 0""")
            self.connection().commit()
            self.connection().close()
            return True
        except Exception as e:
            return str(e)

    def update_susuarios(self, path_data_local):
        try:
            self.connection().execute(f"""UPDATE SUSUARIOS SET Directorio_Datos ='{path_data_local}', Directorio_Sistema ='{path.dirname(path_data_local)}\\FILECONFIG',
                                      Directorio_Formas='{path.dirname(path_data_local)}\\USERSCONFIG', Directorio_Formatos = '{path.dirname(path_data_local)}\\CONFIGR',
                                      Directorio_Local = '{path.dirname(path_data_local)}\\TMP'    """)
            self.connection().commit()
            self.connection().close()
        except Exception as e:
            print(e)

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

    def update_ssistema_document_number(self, data: dict):
        try:
            self.connection().execute(f"""UPDATE SSISTEMA SET NO_FACTURA = {int(data['ultima_factura'])}  WHERE DUMMYKEY = '{data['serie']}' """ )
            
            self.connection().commit()
            self.connection().close()
            return True
        except Exception as e:
            return e


    def get_serie_document_number(self, serie):
        try:
            no_factura = self.connection().execute(f"""SELECT NO_FACTURA FROM SSISTEMA WHERE DUMMYKEY = '{serie}'  """).fetchone()[0]
            self.connection().close()
            return no_factura
        except Exception as e:
            print(e)    

    def get_correlativos(self):
        try:
            no_factura = self.connection().execute(f"""SELECT NO_FACTURA, DUMMYKEY FROM SSISTEMA  """).fetchall()
            self.connection().close()
            return no_factura
        except Exception as e:
            print(e)   

    def update_correlativos(self, serie: str, correlativo: int):
        try:
            no_factura = self.connection().execute(f"""UPDATE SSISTEMA SET NO_FACTURA = {correlativo} WHERE DUMMYKEY = '{serie}'  """).rowcount
            self.connection().commit()
            self.connection().close()
            return no_factura
        except Exception as e:
            print(e)          


    def update_tablas_locales(self, auto_so, auto_sd):
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
            return True
        except Exception as e:    
            return e
    def clear_tablas_locales(self):
        try:
            self.connection().execute("""EMPTY TABLE SOPERACIONINV """)
            self.connection().execute("""EMPTY TABLE SDETALLEVENTA """)
            return True
        except Exception as e:
            return False  
        
    def get_data_local(self, serie):
        try:
            rows = self.connection().execute(f"""SELECT FTI_DOCUMENTO FROM SOPERACIONINV WHERE FTI_SERIE = '{serie}' """).rowcount
            return rows
        except Exception as e:
            print(e)
            return 0       


    async def max_Auto(self) -> tuple | str:
        try:
            max_auto = self.connection().execute("SELECT MAX(FTI_AUTOINCREMENT) FROM SOPERACIONINV").fetchone()[0]
            max_auto_detalle = self.connection().execute("SELECT MAX(FDI_AUTOINCREMENT) FROM SDETALLEVENTA").fetchone()[0]
            self.connection().close()
            return (max_auto , max_auto_detalle)
        except Exception as e:
            return str(e)

    def create_tables_locales(self, tables: tuple):
        try:
            for table in tables:
                self.connection().execute(table)    
        except Exception as e:
            print(e)    

    async def insert_into_data_server(self):
        try:
            self.connection().execute("INSERT INTO SOPERACIONINV SELECT * FROM zip_backup\\SOPERACIONINV")
            self.connection().execute("INSERT INTO SDETALLEVENTA SELECT * FROM zip_backup\\SDETALLEVENTA")
            self.connection().commit()
            self.connection().close()
            return True
        except Exception as e:
            print(e)
            return str(e)
            

    def filter_client(self, id:str):
        clients = self.connection().execute(f"SELECT FC_CODIGO FROM SCLIENTES WHERE FC_CODIGO = '{id}'").fetchall()
        for client in clients:
            if client.FC_CODIGO == id:
                fini = time.time()
                self.dsn.close() 
                return client
            
    async def insert_client(self, *args)-> bool | pyodbc.Error:
        pass

    