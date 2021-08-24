import pymysql


def get_connection():
    conn = pymysql.connect(
        host='127.0.0.1',
        port=3306,
        user='root',
        password='1234',
        db='youthdb',
        charset='utf8'
                           )
    return conn
