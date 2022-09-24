from flask import Flask
import sys
sys.path.insert(1, "src/datasource/")
from cloud_connection import CloudConnection
from attendance_2_mysql import Attendance2Mysql
sys.path.insert(1, "src/")
from attendance import Attendance


app = Flask(__name__)

@app.route('/')
def index():
    sftp_connection = CloudConnection()
    sftp_connection.init()
    sftp_connection.download_cloud_files()
    attendance = Attendance()
    attendance.main("csv_files/")
    attendance2mysql = Attendance2Mysql()
    app.logger.info("05")
    attendance2mysql.init("attendance.csv")
    app.logger.info("06")
    attendance2mysql.run_test()
    app.logger.info("07")
    return "Hello my WEB app using flask!!"

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
