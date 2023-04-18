from flaskext.mysql import MySQL

def init(server):
    mysql = MySQL()
    mysql.init_app(server)
    return mysql