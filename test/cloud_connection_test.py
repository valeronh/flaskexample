import sys

sys.path.insert(1, "../src/datasource/")
from cloud_connection import CloudConnection

if __name__ == "__main__":
    att = CloudConnection()
    att.run_test()
