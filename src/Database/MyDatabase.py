import psycopg2



class MyDatabase:
    def __init__(self , host ="localhost" , db = "mydb", user="postgres"  , password = "j95k89"):
        self.conn = psycopg2.connect(host=host, database=db, user=user, password=password)
        self.conn.autocommit = False
        self.cur = self.conn.cursor()

    def query(self, query):
        try:
            self.cur.execute(str(query))
            print("Transaction completed Successfully")
            self.conn.commit()
            return True
        except (Exception, psycopg2.DatabaseError) as error:
            print("Error in transcation Reverting all other operations of a transcation", error)
            self.conn.rollback()
            return False


    def close(self):
        self.cur.close()
        self.conn.close()
