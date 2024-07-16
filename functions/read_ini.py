import configparser
import asyncio
#import os

async def lastAuto():
    global_var = configparser.ConfigParser()
    global_var.read('server.ini')
    auto =  global_var.items('LASTAUTO')
    return auto

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

    return ip, port

def getConfigClient():
    client = configparser.ConfigParser()
    client.read('client.ini')
    ip = client.get('CONFIG', 'SERVERIP')
    port = client.get('CONFIG', 'PORT')
    rutalocal = client.get('CONFIG', 'RUTALOCAL')
    serie = client.get('CONFIG', 'SERIEACTUAL')
    series = client.get('CONFIG', 'SERIES')
    a2data = client.get('CONFIG', 'RUTA_A2')
    return ip, port, rutalocal, serie.upper(), series.upper().split(','),  a2data

def saveInitConfig(server_ip, port, serie, ruta_local, ruta_a2):
    try:
        file = configparser.ConfigParser(strict=True)
        file.read('client.ini')
        file['CONFIG']['SERVERIP'] = server_ip
        file['CONFIG']['PORT'] = port
        file['CONFIG']['SERIEACTUAL'] = serie
        file['CONFIG']['RUTALOCAL'] = ruta_local
        file['CONFIG']['RUTA_A2'] = ruta_a2
        with open('client.ini', 'w') as file_ini:
            file.write(file_ini)
        return True    
    except Exception as e:
        return e    



#updateAuto('25', 'CAJA01', 'LASTAUTO')    