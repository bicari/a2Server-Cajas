import uvicorn
import os
import pathlib
import asyncio
from functions import search_database_files
from functions import getServerConfig, saveServerLastUpdate
import shutil
from datetime import datetime
config = getServerConfig()

async def init_app():
     try:
        await search_database_files(catalogname=config[2])  
        if os.path.exists('data_cajas.zip'):      
                copy_result = shutil.copy('data_cajas.zip', config[6])  
                saveServerLastUpdate(str(datetime.date(datetime.now())))
     except Exception as e:
        print(e)            
        
                   

if __name__ == '__main__':
    try:
        asyncio.run(init_app())
        uvicorn.run("server:app", host=config[0], port=int(config[1]), log_level='info')
    except KeyboardInterrupt as e:
          print(e)    
    if not os.path.exists(f"{pathlib.Path().absolute()}\\tmp"):
            os.mkdir(f"{pathlib.Path().absolute()}\\tmp")
    if not os.path.exists(f"{pathlib.Path().absolute()}\\zip"):
            os.mkdir(f"{pathlib.Path().absolute()}\\zip")
    if not os.path.exists(f"{pathlib.Path().absolute()}\\zip_backup"):
            os.mkdir(f"{pathlib.Path().absolute()}\\zip_backup")  