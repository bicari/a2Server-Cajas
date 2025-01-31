import configparser

#import os

async def lastAuto():
    global_var = configparser.ConfigParser()
    global_var.read('server.ini')
    auto =  global_var.items('LASTAUTO')
    return auto

def saveServerLastUpdate(date: str):
    server = configparser.ConfigParser()
    server.read('server.ini')
    server['CONFIG']['LAST_COMPACT']= date
    with open('server.ini', 'w') as file:
        server.write(file)

def getKeys():
    get_keys = configparser.ConfigParser()
    get_keys.read('server.ini')
    
    return get_keys.options('LASTAUTO')

async def updateAuto(data, id_caja, section):
    try:
        var = configparser.ConfigParser()
        var.read('server.ini')
        var.set(section, id_caja, data)

        with open('server.ini', 'w') as configfile:
            var.write(configfile)
    except Exception as e:
        print(e)        

def getServerConfig():
    server = configparser.ConfigParser()
    server.read('server.ini')
    ip = server.get('CONFIG', 'IP')
    port = server.get('CONFIG', 'PORT')
    path_data = server.get('CONFIG', 'PATH_DATA')
    last_compact_date = server.get('CONFIG', 'LAST_COMPACT')
    ip_server_files = server.get('CONFIG', 'SERVER_FILES')
    port_server_files = server.get('CONFIG', 'PORT_SERVER_FILES')
    path_server_files = server.get('CONFIG', 'PATH_SERVER_FILES')

    return ip, port, path_data, last_compact_date, ip_server_files, port_server_files, path_server_files

def getConfigClient():
    client = configparser.ConfigParser()
    client.read('client.ini')
    ip = client.get('CONFIG', 'SERVERIP')
    port = client.get('CONFIG', 'PORT')
    rutalocal = client.get('CONFIG', 'RUTALOCAL')
    serie = client.get('CONFIG', 'SERIEACTUAL')
    series = client.get('CONFIG', 'SERIES')
    a2data = client.get('CONFIG', 'RUTA_A2')
    ruta_a2_cash= client.get('CONFIG', 'RUTA_A2_CASH')
    sync = client.get('CONFIG', 'SYNC')
    ip_server_files = client.get('CONFIG', 'SERVERFILES')
    port_server_files = client.get('CONFIG', 'PORTFILES')
    connection_mode = client.get('CONFIG', 'CONNECTION_MODE')
    lastAuto_sclientes = client.get('CONFIG', 'LASTAUTO') 
    return ip, port, rutalocal, serie.upper(), series.upper().split(','),  a2data, ruta_a2_cash, sync, ip_server_files, port_server_files, connection_mode, lastAuto_sclientes

def saveInitConfig(server_ip, port, serie, ruta_local, ruta_a2, ruta_a2_cash, portfiles, ipfiles, connection_mode):
    try:
        file = configparser.ConfigParser(strict=True)
        file.read('client.ini')
        file['CONFIG']['SERVERIP'] = server_ip
        file['CONFIG']['PORT'] = port
        file['CONFIG']['SERIEACTUAL'] = serie
        file['CONFIG']['RUTALOCAL'] = ruta_local
        file['CONFIG']['RUTA_A2'] = ruta_a2
        file['CONFIG']['RUTA_A2_CASH'] = ruta_a2_cash
        file['CONFIG']['PORTFILES']= portfiles
        file['CONFIG']['SERVERFILES']= ipfiles
        file['CONFIG']['CONNECTION_MODE'] = connection_mode
        with open('client.ini', 'w') as file_ini:
            file.write(file_ini)
        return True    
    except Exception as e:
        return e    

def saveAutoClients(auto):
    try:
        file = configparser.ConfigParser()
        file.read('client.ini')
        file['CONFIG']['LASTAUTO'] = auto
        with open('client.ini', 'w') as file_ini:
            file.write(file_ini)
        return True    
    except Exception as e:
        return str(e)   


def saveSyncData(last_sync):
    try:
        file = configparser.ConfigParser(strict=True)
        file.read('client.ini')
        file['CONFIG']['SYNC'] = last_sync
        with open('client.ini', 'w') as file_ini:
            file.write(file_ini)  
        return True            
    except Exception as e:
        return e


#updateAuto('25', 'CAJA01', 'LASTAUTO')    