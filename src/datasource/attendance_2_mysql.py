import mysql.connector
import csv
from dotenv import dotenv_values
import sys, os

class Attendance2Mysql:
    mydb = None
    mycursor = None
    config = None
    path = None

    def init(self, path):
        self.config = dotenv_values(".env")
        self.path = path
        self.mydb = self.open_connection()
        self.mycursor = self.mydb.cursor(dictionary=True)
        self.create_owner_table()
        
    def open_connection(self):
        mydb=mysql.connector.connect(
            host=self.config["MYSQL_HOST"],
            user=self.config["MYSQL_USER"],
            password=self.config["MYSQL_PASSWORD"],
            database=self.config["MYSQL_DATABASE"]
        )
        return mydb

    def create_owner_table(self):
        self.mycursor.execute("CREATE TABLE IF NOT EXISTS owner(id INT NOT NULL AUTO_INCREMENT, name VARCHAR(30), average VARCHAR(20), PRIMARY KEY(id))")
        print("Table is created....")

    def select_owner(self):
        print("Contents of the table: ")
        self.mycursor.execute("SELECT * from owner")
        return self.mycursor.fetchall()

    def reset_owner(self):
        try:
            self.mycursor.execute("DROP TABLE  owner")
            print("Old table deleted...")
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
            next(filereader)
            for row in filereader:
                self.insert_owner(row[1], row[-1])

    def run_test(self):
        self.reset_owner()
        self.create_owner_table()
        self.select_owner()
        self.read_csv(self.path)
        self.select_owner()

