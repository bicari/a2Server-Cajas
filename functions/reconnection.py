from querys import sqlQuerys
from socketio import Client


def reconnection_server(config, caja: Client, path_dsn_odbc: str):
    if sqlQuerys(path_dsn_odbc).get_data_local(config[3]) > 0:
        no_factura = sqlQuerys(path_dsn_odbc).get_serie_document_number(config[3])
        no_factura_server = sqlQuerys(dsn='DSN=A2GKC;CatalogName={catalogname}'.format(catalogname=config[5])).get_serie_document_number(config[3])
        print(no_factura, no_factura_server)
        if config[3][:3] == '1NF' or config[3][:3] == 'ZNF' and no_factura > no_factura_server:
            caja.emit('update_ssistema_serie', data={'serie': config[3], 'ultima_factura': no_factura},namespace='/default')