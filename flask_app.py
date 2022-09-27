from flask import Flask, render_template
import sys
import json
sys.path.insert(1, "src/datasource/")
from cloud_connection import CloudConnection
from attendance_2_mysql import Attendance2Mysql
sys.path.insert(1, "src/")
from attendance import Attendance


app = Flask(__name__)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/flow')
def flow():
    return render_template('flow.html')

@app.route('/attendance')
def attendance():
    sftp_connection = CloudConnection()
    sftp_connection.init()
    sftp_connection.download_cloud_files()
    attendance = Attendance()
    attendance.main("csv_files/")
    attendance2mysql = Attendance2Mysql()
    attendance2mysql.init("attendance.csv")
    attendance2mysql.run_main()
    return render_template('attendance.html', tables=attendance2mysql.select_owner())

if __name__ == "__main__":
    app.run(host='0.0.0.0')
