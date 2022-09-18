import os
import pysftp
from dotenv import dotenv_values

class CloudConnection:
    config = None
    
    def __init__(self):
        self.config = dotenv_values("../.env")
    
    def list(self):
        with pysftp.Connection(host=self.config["CLOUD_HOSTNAME"], username=self.config["CLOUD_USERNAME"], password=self.config["CLOUD_PASSWORD"]) as sftp:
            print ("Connection succesfully stablished ... ")
            sftp.cwd(self.config["CLOUD_PATH"])
            directory_structure = sftp.listdir_attr()
            folder_dict = {}
            for attr in directory_structure:
                 folder_dict[attr.filename] = attr
            return folder_dict

    def download_file(self, remoteFilePath, localFilePath):
        with pysftp.Connection(host=self.config["CLOUD_HOSTNAME"], username=self.config["CLOUD_USERNAME"], password=self.config["CLOUD_PASSWORD"]) as sftp:
            sftp.cwd(self.config["CLOUD_PATH"])
            print ("Connection succesfully stablished ... ")
            sftp.get(remoteFilePath, localFilePath)

    def download_cloud_files(self):
        list = self.list()
        try:
            os.mkdir("csv_files")
        except:
            print("warning directory exists")
        for key in list.keys():
            self.download_file(key, "csv_files/" + key)

    def run_test(self):
        self.download_cloud_files()
