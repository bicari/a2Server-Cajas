import zipfile
import os


async def search_database_files()  -> bool :
        try:
            LIST_TABLES = ['a2InvCostosPrecios', 'a2PtosConfig', 'Sautorizados','Sbancos', 'Sbeneficiario','Scargosfijos', 'Scategoria', 'SCierresCaja', 'Sclientes','SClientesDetalle','SclientesEventuales','SCodeBar','Scompuesto','Sconceptos','Sconvenios','Scuentasxcobrar','Sdepositos', 'SDetalleCompra', 'SDetalleInv','SDetallePartes','SDetalleVenta',
'SFixed','SFormasPago','SFormasPagoFlag','SHistoricoCliente','SIGTF','SInstitucion','SinvDep','Sinventario','Sinvlote','SInvOferta','Smoneda','SOperacionInv','Spagosfijos',
'Sprovinvent','SRetencioncliente','Sseriales','SSistema','Starjetas','Stransbanco','STransCuentas','SUsersFlag','Susuarios','Svendedores','Szonas','Sclasificacion'] #Lista de tablas a sincronizar al iniciar app
            file_compress = zipfile.ZipFile('data.zip', 'w')
            result = next(os.walk('C:\\a2CA2020\\Empre001\\Data'))[2] #Lista de archivos del directorio data del sistema
            for file in result:
                if file[:-4] in LIST_TABLES and file.endswith(('.idx', '.dat', '.blb')):
                    file_compress.write(filename='{path}{file_name}'.format(path='C:\\a2CA2020\\Empre001\\Data\\', file_name=file), arcname=file, compress_type=zipfile.ZIP_DEFLATED)
                
            file_compress.close()
            return True
        except Exception as e:
             return False

async def search_local_tables(path_files) -> bool:
     try:
          LIST_TABLES_LOCAL = ['SDetalleVenta', 'SOperacionInv']
          file_compress =  zipfile.ZipFile('zip\\data_local.zip', 'w')
          files =  next(os.walk(path_files))[2]
          for file in files:
               if file[:-4] in LIST_TABLES_LOCAL and file.endswith(('.idx', '.dat', '.blb')):
                    file_compress.write(filename='{path}{file_name}'.format(path=path_files +'\\' , file_name=file), arcname=file, compress_type=zipfile.ZIP_DEFLATED)
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