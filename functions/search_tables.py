import zipfile
import os
import datetime


async def search_database_files(catalogname)  -> bool :
        try:
            LIST_TABLES = ['a2InvCostosPrecios', 'a2PtosConfig', 'Sautorizados','Sbancos', 'Sbeneficiario','Scargosfijos', 'Scategoria', 'SCierresCaja', 'Sclientes','SClientesDetalle','SclientesEventuales','SCodeBar','Scompuesto','Sconceptos','Sconvenios','Sdepositos',
'SFixed','SFormasPago','SFormasPagoFlag','SHistoricoCliente','SIGTF','SInstitucion','SinvDep','Sinventario','Sinvlote','SInvOferta','Smoneda','Spagosfijos',
'Sprovinvent','SRetencioncliente','Sseriales','SSistema','Starjetas','SUsersFlag','Susuarios','Svendedores','Szonas','Sclasificacion'] #Lista de tablas a sincronizar al iniciar app
            file_compress = zipfile.ZipFile('data_cajas.zip', 'w')#Nombre del archivo comprimido
            result = next(os.walk(catalogname))[2] #Lista de archivos del directorio data del sistema
            
            for file in result:
                if file[:-4] in LIST_TABLES and file.endswith(('.idx', '.dat', '.blb')):
                    file_compress.write(filename='{path}{file_name}'.format(path=f'{catalogname}\\', file_name=file), arcname=file, compress_type=zipfile.ZIP_DEFLATED)
                
            file_compress.close()
            return True
        except Exception as e:
             return False
        
        

def search_local_tables(path_files, sid) -> bool:
     try:
          LIST_TABLES_LOCAL = ['SDetalleVenta', 'SOperacionInv']
          file_compress =  zipfile.ZipFile(f'zip\\data_ventas_{datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-")}.zip', 'w')
          files =  next(os.walk(path_files))[2]
          for file in files:
               if file[:-4] in LIST_TABLES_LOCAL and file.endswith(('.idx', '.dat', '.blb')):
                    file_compress.write(filename='{path}{file_name}'.format(path=path_files +'\\' , file_name=file), arcname=file, compress_type=zipfile.ZIP_DEFLATED)
          return True  
     except Exception as e: 
          print(e)    
          return False

def decompress_file_sinc(name_file, path_decompress):
     try:
          file_decompress = zipfile.ZipFile(name_file, 'r')
          file_decompress.extractall(path=path_decompress)
          return True
     except Exception as e:
          return False    

async def decompress_file(name_file, path_decompress):
     try:
          file_decompress = zipfile.ZipFile(name_file, 'r')
          file_decompress.extractall(path=path_decompress)
          return True
     except Exception as e:
          return False    