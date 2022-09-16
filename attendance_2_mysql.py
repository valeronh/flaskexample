import mysql.connector
import csv

class Attendance2Mysql:
    mydb = None
    mycursor = None

    def __init__(self):
        self.mydb = self.open_connection()
        self.mycursor = self.mydb.cursor()
        

    def open_connection(self):
        mydb=mysql.connector.connect(
            host="localhost",
            user="valerys",
            password="V@le1988",
            database="valerydb"
        )
        return mydb

    def select_owner(self):
        print("Contents of the table: ")
        self.mycursor.execute("SELECT * from owner")
        print(self.mycursor.fetchall())

    def reset_owner(self):
        try:
            self.mycursor.execute("DELETE FROM owner")
            self.mydb.commit()
            self.mydb.flush()
        except:
            self.mydb.rollback()

    def insert_owner(self, name, average):
        sql = "INSERT INTO owner (name, average) VALUES (%s, %s)"
        val = (name, average)
        self.mycursor.execute(sql, val)
        self.mydb.commit()

    def read_csv(self, csvfile):
        with open(csvfile, newline='') as file:
            filereader = csv.reader(file, delimiter=',')
            for row in filereader:
                self.insert_owner(row[1], row[15])

    def run_test(self):
        self.select_owner()
        self.reset_owner()
        self.read_csv('attendance.csv')
        self.select_owner()
        self.mydb.close()

