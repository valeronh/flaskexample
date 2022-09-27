import sys
sys.path.insert(1, "src/datasource/")
from attendance_2_mysql import Attendance2Mysql

if __name__ == "__main__":
    if len(sys.argv)>1:
        att = Attendance2Mysql()
        att.init(sys.argv[1])
        att.run_test()
    else:
        sys.exit("Path is mandatory")
