import zipfile
import os


async def search_database_files()  -> bool :
        try:
            LIST_TABLES = ['SOperacionInv', 'SdetalleVenta'] #Lista de tablas a sincronizar al iniciar app
            file_compress = zipfile.ZipFile('data.zip', 'w')
            result = next(os.walk('C:\\a2CA2020\\Empre001\Data'))[2] #Lista de archivos del directorio data del sistema
            for file in result:
                if file[:-4] in LIST_TABLES and file.endswith(('.idx', '.dat', '.blb')):
                    file_compress.write(filename='{path}{file_name}'.format(path='C:\\a2CA2020\\Empre001\Data\\', file_name=file), arcname=file, compress_type=zipfile.ZIP_DEFLATED)
                
            file_compress.close()
            return True
        except Exception as e:
             return False
