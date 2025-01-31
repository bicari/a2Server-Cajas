import pyodbc
from decimal import Decimal
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

    def get_lastAuto_clients(self):
        try:
            auto = self.connection().execute("SELECT MAX(BASE_AUTOINCREMENT) FROM SCLIENTES").fetchone()[0]
            return auto
        except Exception as e:
            return str(e)    

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


    def insert_new_clients(self,data: dict):
        try:
            new_clients = 0
            for client in data['data']:
                descripcion_detallada = client[4].replace("\r", "'+#13+'").replace("\n", "'+#10+'") if client[4] != None else ""
                direccion1 = client[9].replace("\r", "'+#13+'").replace("\n", "'+#10+'") if client[9] != None else ""
                direccion2 = client[10].replace("\r", "'+#13+'").replace("\n", "'+#10+'") if client[10] != None else ""
                direccion3 = client[11].replace("\r", "'+#13+'").replace("\n", "'+#10+'") if client[11] != None else ""
                query=f"""INSERT INTO SCLIENTES (FC_CODIGO, 
                        FC_DESCRIPCION, 
                        FC_STATUS, 
                        FC_CLASIFICACION, 
                        FC_DESCRIPCIONDETALLADA, 
                        FC_NIT, 
                        FC_RIF, 
                        FC_TIPO, 
                        FC_CONTACTO, 
                        FC_DIRECCION1, 
                        FC_DIRECCION2, 
                        FC_DIRECCION3, 
                        FC_TELEFONO, 
                        FC_TELEFAX, 
                        FC_EMAIL, 
                        FC_WEBSITE, 
                        FC_FORMAENVIO, 
                        FC_ZONA, 
                        FC_VENDEDOR, 
                        FC_COBRADOR, 
                        FC_LIMITECREDITO, 
                        FC_DIASCREDITO, 
                        FC_MORA, 
                        FC_FECHAINICIO, 
                        FC_MAXIMODESCUENTO, 
                        FC_SALDO, 
                        FC_PAGOSADELANTADOS, 
                        FC_SALDOMONEDA2, 
                        FC_PAGOSADELMONEDA2, 
                        FC_TOTALVENTA, 
                        FC_MAXIMOCREDITO, 
                        FC_PROMEDIOPAGOSDIAS, 
                        FC_TOTALIVARETENIDO, 
                        FC_DESCTOPRONTOPAGO, 
                        FC_FLAGCONTABILIDAD, 
                        FC_FLAGULTIMASOPERACIONES,  
                        FC_MONEDA, 
                        FC_EXENTO, 
                        FC_FRECUENCIA, 
                        FC_DIACORTE, 
                        FC_PRECIODEFECTO, 
                        FC_RECORDCONTADO, 
                        FC_FECHANACIMIENTO, 
                        FC_RETENCION, 
                        FC_FORMATOFACTURA, 
                        FC_FORMATOAPARTADO,  
                        FC_CODERETENCION, 
                        FC_ISOPAIS, 
                        FC_THKATIPOVENTA) 
                                      VALUES('{client[0]}', '{client[1]}', {"Null" if client[2]== None else client[2]}, {"Null" if client[3]==None else f"'{client[3]}'"}, 
                                      '{descripcion_detallada}', {"Null" if client[5] == None else f"'{client[5]}'"}, {"Null" if client[6] == None else f"'{client[6]}'"},
                                      {"Null" if client[7] == None else client[7]}, {"Null" if client[8] == None else f"'{client[8]}'"}, '{direccion1}', '{direccion2}', '{direccion3}',
                                      {"Null" if client[12]== None else f"'{client[12]}'"}, {"Null" if client[13]== None else f"'{client[13]}'"}, {"Null" if client[14]== None else f"'{client[14]}'"},
                                      {"Null" if client[15]== None else f"'{client[15]}'"}, {"Null" if client[16]== None else f"'{client[16]}'"}, {"Null" if client[17]== None else f"'{client[17]}'"},
                                      {"Null" if client[18]== None else f"'{client[18]}'"}, {"Null" if client[19]== None else f"'{client[19]}'"}, {"Null" if client[20]==None else client[20]}, {"Null" if client[21]==None else client[21]},
                                      {"Null" if client[22]== None else client[22]}, {"Null" if client[23]==None else f"'{client[23]}'"}, {"Null" if client[24]== None else client[24]}, {"Null" if client[25]== None else client[25]},
                                      {"Null" if client[26]== None else client[26]}, {"Null" if client[27]== None else client[27]}, {"Null" if client[28]== None else client[28]}, {"Null" if client[29]== None else client[29]},
                                      {"Null" if client[30]== None else client[30]}, {"Null" if client[31]== None else client[31]}, {"Null" if client[32]== None else client[32]}, {"Null" if client[33]== None else client[33]},
                                      {"Null" if client[34]== None else client[34]}, {"Null" if client[35]== None else client[35]}, {"Null" if client[36]== None else f"'{client[36]}'"}, {"Null" if client[37]== None else client[37]},
                                      {"Null" if client[38]== None else client[38]}, {"Null" if client[39]== None else client[39]}, {"Null" if client[40]== None else client[40]}, {"Null" if client[41]== None else client[41]},
                                      {"Null" if client[42]== None else f"'{client[42]}'"}, {"Null" if client[43]== None else client[43]}, {"Null" if client[44]== None else f"'{client[44]}'"}, {"Null" if client[45]== None else f"'{client[45]}'"},
                                      {"Null" if client[46]== None else f"'{client[46]}'"}, {"Null" if client[47]== None else f"'{client[47]}'"}, {"Null" if client[48]== None else f"'{client[48]}'"} 
                                      )"""
                #print(query)
                try:
                    rows = self.connection().execute(query).rowcount
                    new_clients += rows
                    self.connection().commit()
                except pyodbc.Error as e:
                    pass   
                
            return new_clients    
        except Exception as e:
            return str(e)    

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
            

    def search_new_clients_local(self, auto: int):
        clients = self.connection().execute(f"""SELECT FC_CODIGO, 
                        FC_DESCRIPCION, 
                        FC_STATUS, 
                        FC_CLASIFICACION, 
                        FC_DESCRIPCIONDETALLADA, 
                        FC_NIT, 
                        FC_RIF, 
                        FC_TIPO, 
                        FC_CONTACTO, 
                        FC_DIRECCION1, 
                        FC_DIRECCION2, 
                        FC_DIRECCION3, 
                        FC_TELEFONO, 
                        FC_TELEFAX, 
                        FC_EMAIL, 
                        FC_WEBSITE, 
                        FC_FORMAENVIO, 
                        FC_ZONA, 
                        FC_VENDEDOR, 
                        FC_COBRADOR, 
                        FC_LIMITECREDITO, 
                        FC_DIASCREDITO, 
                        FC_MORA, 
                        FC_FECHAINICIO, 
                        FC_MAXIMODESCUENTO, 
                        FC_SALDO, 
                        FC_PAGOSADELANTADOS, 
                        FC_SALDOMONEDA2, 
                        FC_PAGOSADELMONEDA2, 
                        FC_TOTALVENTA, 
                        FC_MAXIMOCREDITO, 
                        FC_PROMEDIOPAGOSDIAS, 
                        FC_TOTALIVARETENIDO, 
                        FC_DESCTOPRONTOPAGO, 
                        FC_FLAGCONTABILIDAD, 
                        FC_FLAGULTIMASOPERACIONES,  
                        FC_MONEDA, 
                        FC_EXENTO, 
                        FC_FRECUENCIA, 
                        FC_DIACORTE, 
                        FC_PRECIODEFECTO, 
                        FC_RECORDCONTADO, 
                        FC_FECHANACIMIENTO, 
                        FC_RETENCION, 
                        FC_FORMATOFACTURA, 
                        FC_FORMATOAPARTADO,  
                        FC_CODERETENCION, 
                        FC_ISOPAIS, 
                        FC_THKATIPOVENTA FROM SCLIENTES WHERE BASE_AUTOINCREMENT > {auto}""").fetchall()
        #print('Numeros de campos', (len(client) for client in clients))
        return {'data': [tuple(float(value) if isinstance(value, Decimal) else value for value in client) for client in clients]}
        #return [tuple(client) for client in clients]
            
    async def insert_client(self, *args)-> bool | pyodbc.Error:
        pass


    