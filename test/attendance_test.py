import sys
sys.path.insert(1, "src/")
from attendance import Attendance

if __name__ == "__main__":
    attendance = Attendance()
    attendance.main("csv_files/")
