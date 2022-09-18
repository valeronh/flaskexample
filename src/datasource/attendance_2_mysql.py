import mysql.connector
import csv
from dotenv import dotenv_values
import sys, os

class Attendance2Mysql:
    mydb = None
    mycursor = None
    config = None
    path = None
    argv = None

    def __init__(self, argv):
        self.config = dotenv_values("../.env")
        self.argv = argv
        self.validate()
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

    def validate(self):
        if len(self.argv)>2:
            sys.exit("Too many arguments, please provide only one argument which is path")
        if len(self.argv)>1:
            self.path = self.argv[1]
            if not os.path.isfile(self.path):
                sys.exit("No such file")    
        else:
            sys.exit("Path to csv file is mandatory")

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
        self.read_csv(self.path)
        self.select_owner()
        self.mydb.close()

