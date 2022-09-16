import mysql.connector
import csv
from dotenv import dotenv_values

class Attendance2Mysql:
    mydb = None
    mycursor = None
    config = None

    def __init__(self):
        self.config = dotenv_values(".env")
        self.mydb = self.open_connection()
        self.mycursor = self.mydb.cursor()
        
    def open_connection(self):
        mydb=mysql.connector.connect(
            host=self.config["MYSQL_HOST"],
            user=self.config["MYSQL_USER"],
            password=self.config["MYSQL_PASSWORD"],
            database=self.config["MYSQL_DATABASE"]
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

