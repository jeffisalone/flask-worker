import pymysql

class db:
    def __init__(self):
        self.host = '47.93.254.56'
        self.port=3306
        self.user='django_app'
        self.passwd='Lds112..A'
        self.db='django_app'

    def fetch_one(self,params):
        conn = pymysql.connect(host=self.host,port=self.port,user=self.user,passwd=self.passwd,db=self.db)
        cursor =conn.cursor()
        cursor.execute(params)
        self.data = cursor.fetchone()
        cursor.close()
        conn.close()

    def run(self,params):
        conn = pymysql.connect(host=self.host,port=self.port,user=self.user,passwd=self.passwd,db=self.db)
        cursor =conn.cursor()
        cursor.execute(params)
        conn.commit()
        cursor.close()
        conn.close()