from attendance_2_mysql import Attendance2Mysql
import sys, os

if __name__ == "__main__":
    if len(sys.argv)>1:
        path = sys.argv[1]
        if len(sys.argv)>2:
            sys.exit("Too many arguments, please provide only one argument which is path")
    else:
        sys.exit("Path to file is mandatory")

    if not os.path.isfile(path):
        sys.exit("No such file")
    
    att = Attendance2Mysql(path)
    att.run_test()
