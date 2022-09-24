import pandas as pd
import jellyfish
import os
import sys

class Attendance:
    # csv columns headers columns:
    ROOM_NAME = "Meeting Name"
    ROOM_START = "Meeting Start Time"
    ROOM_FINISH = "Meeting End Time"
    NAMES = "Name"
    EMAILS = "Attendee Email"
    JOIN_TIME = "Join Time"
    JOIN_TIME_NUM = 5
    LEAVE_TIME = "Leave Time"
    LEAVE_TIME_NUM = 6
    OVERALL_TIME = "Attendance Duration"
    PLATFORM = "Connection Type"


    def get_files(self, dirpath):
        """
        calculates a list containing all participants files
        :param dirpath: string of a directory containing the participants files
        :return: list of all participants files
        """
        attend_files = []
        for file in os.listdir(dirpath):
            filepath = os.path.join(dirpath, file)
            if os.path.isfile(filepath) and "participant-" in file:
                attend_files.append(filepath)

        if len(attend_files) == 0:
            print("This directory has no participant's meetings files!")
            print("please provide a one containing those csv files")
            exit(1)
        return attend_files


    def get_data(self, csvfile):
        """
        analyzes the data from a csv file and returning it as a pd.DataFrame
        :param csvfile: string of a path to a csv file
        :return: pd.DataFrame sorted by the join times and the maximal overall login time in the file
        """
        df = pd.read_csv(csvfile, encoding="utf-16LE", sep="\t")
        df = df.replace('\"', '', regex=True)
        df = df.replace('=', '', regex=True)
        # calculate maximal overall login time in the file:
        df.sort_values(by=[self.LEAVE_TIME], ascending=False, inplace=True)  # descending order by leave time
        latest = str(df.iloc[0, self.LEAVE_TIME_NUM]).rsplit(" ")[1]     # take first row after sort
        latest_hour = int(latest.rsplit(":")[0])
        latest_min = int(latest.rsplit(":")[1])
        df.sort_values(by=[self.JOIN_TIME], ascending=True, inplace=True)    # ascending order by join time
        earliest = str(df.iloc[0, self.JOIN_TIME_NUM]).rsplit(" ")[1]  # take first row after sort
        earliest_hour = int(earliest.rsplit(":")[0])
        earliest_min = int(earliest.rsplit(":")[1])
        max_overall = (latest_hour - earliest_hour) * 60 + (latest_min-earliest_min)
        return df, max_overall


    def init(self, dirpath):
        """
        initiates all parameters that are needed for the script: the dictionary of the participants, list of csv files
        and the initiative pd.DataFrame
        :return: pd.DataFrame, list of csv files and the dictionary of the participants
        """
        time_dict = {}
        csv_lst = self.get_files(dirpath)
        init_data, m = self.get_data(csv_lst[0])
        self.dict_init(init_data, time_dict)
        df = pd.DataFrame(index=time_dict.keys())
        return df, csv_lst, time_dict


    def check_spell(self, df_email, time_dict):
        """
        the function checks if an email is misspelled by up to several errors
        if so, then the function returns the correct one, else, the function returns false
        :param df_email: string of an email from the DataFrame
        :param time_dict: dictionary of participants
        :return: String or void
        """
        for mail in time_dict.keys():
            if jellyfish.damerau_levenshtein_distance(df_email, mail) < 3:
                return mail
        return


    def check_hebrew(self, s):
        """
        checks if a string contains any hebrew letter, if so returns true, else returns false
        :param s: string
        :return: bool
        """
        for c in s:
            if ord('\u05d0') <= ord(c) <= ord('\u05ea'):    # if the character is in range of the unicode of hebrew letters
                return True
        return False


    def dict_init(self, df, time_dict):
        """
        initiates the participant's dictionary for every file
        :param df: pd.DataFrame
        :param time_dict: dictionary of the participants
        """
        # initializing all keys:
        for username in time_dict.keys():
            time_dict[username]['time'] = []
            time_dict[username]['overall'] = 0

        for i, row in df.iterrows():
            file_email = str(row[self.EMAILS])
            username = file_email.rsplit('@')[0]
            if "bynet" in file_email or "8200" in file_email or "nan" in file_email:  # skipping the non-students
                continue
            file_name = str(row[self.NAMES])
            if not self.check_spell(username, time_dict):  # if the mail is not already in the dictionary- add it
                time_dict[username] = {'time': [], 'overall': 0, 'name': file_name}
            else:   # if it is then update it
                username = self.check_spell(username, time_dict)   # correcting
                if not self.check_hebrew(file_name):   # if the name in the file is not in hebrew
                    # if there is a more accurate name let's update it
                    if len(time_dict[username]['name']) < len(file_name):
                        time_dict[username]['name'] = file_name
                    # if the dictionary's name is in hebrew, and we have an english name we should update it to be english
                    if self.check_hebrew(time_dict[username]['name']):
                        time_dict[username]['name'] = file_name


    def dict_update(self, email, time_dict, start, end, overall):
        """
        Formats the inputs: start and end times to a single string "start time - end time".
        calculates the overall login time.
        Updates the dictionary with the given values
        :param email: string
        :param time_dict: dictionary - {email : {time, overall}}
        :param start: string login time
        :param end: string logout time
        :param overall: string overall logged in time
        """
        time_dict[email]['time'].append(start.rsplit(' ')[1] + " - " + end.rsplit(' ')[1])
        time_dict[email]['overall'] += int(overall.replace(' mins', ''))


    def dict_build(self, df, time_dict):
        """
        Building the dictionary based on the input
        :param df: DataFrame - input's data-frame
        :param time_dict:
        """
        self.dict_init(df, time_dict)
        for index, row in df.iterrows():
            file_email = str(row[self.EMAILS])
            username = file_email.rsplit('@')[0]
            if time_dict.get(username):  # if the email is spelled correctly then it is in the dictionary
                self.dict_update(username, time_dict, row[self.JOIN_TIME], row[self.LEAVE_TIME], row[self.OVERALL_TIME])
            elif "bynet" in file_email or "8200" in file_email or "nan" in file_email:  # skipping the non-students:
                continue
            else:
                # checking if is misspelled and correcting it:
                username = self.check_spell(username, time_dict)
                if username:  # if such email exists then consider it as a misspelled email
                    self.dict_update(username, time_dict, row[self.JOIN_TIME], row[self.LEAVE_TIME], row[self.OVERALL_TIME])
        self.special_cases(time_dict)
        return time_dict


    def special_cases(self, time_dict):
        """
        checks for special cases in the login time frames
        :param time_dict: dictionary - {email : {time, overall}}
        """
        for mail in time_dict.keys():
            times = time_dict[mail]['time']
            if len(times) < 2:
                continue
            special = False
            # checking for a special case in logging times:
            i = 0
            while i + 1 < len(times):  # while a next time frame exists
                start = times[i].rsplit(' - ')[0]  # take first login time
                end = times[i].rsplit(' - ')[1]  # take first logout time
                start1 = times[i + 1].rsplit(' - ')[0]  # take second login time
                end1 = times[i + 1].rsplit(' - ')[1]  # take second logout time
                if end >= end1:  # it means, that user was logged in from several devices
                    del (times[i + 1])
                    special = True
                elif start1 <= end <= end1:  # if the logged time frames overlap then take the longest frame
                    times[i] = start + " - " + end1
                    del (times[i + 1])
                    special = True
                else:
                    i += 1

            if special:  # if a special case occurred, calculate the correct overall logged time
                overall = 0
                for frame in times:
                    sh = int(frame.rsplit(":")[0])  # starting hour
                    sm = int(frame.rsplit(":")[1])  # starting minute
                    eh = int(frame.rsplit(":")[2].rsplit("- ")[1])  # ending hour
                    em = int(frame.rsplit(":")[3])  # ending minute

                    overall += (eh - sh) * 60 + (em - sm)
                time_dict[mail]['overall'] = overall


    def add_csv(self, file, time_dict, new_overall):
        """
        adding every csv as a new column and analyzing it
        :param file: string of a csv file
        :param time_dict: dictionary
        :param new_overall: new pd.DataFrame for the overall login time
        :return: the new pd.DataFrame of the overall login time
        after adding the column. also returning the maximum login time in the file
        """
        df, max_time = self.get_data(file)
        # adding values to dictionary:
        self.dict_build(df, time_dict)
        # building the new rows dictionaries:
        overall_dict = {}
        for mail in time_dict.keys():
            overall = time_dict[mail]['overall']
            overall_dict[mail] = overall
        file_date = str(df.iloc[1, self.JOIN_TIME_NUM]).rsplit(" ")[0]

        if file_date in new_overall.columns:    # if a meeting has several files than add
            for i, row in new_overall.iterrows():
                overall_dict[i] += row[file_date]

        new_overall = self.add_col(new_overall, file_date, overall_dict)
        return new_overall, max_time


    def add_col(self, df, col_name, time_dict):
        """
        adding a column to a pd.DataFrame.
        :param df: pd.DataFrame
        :param col_name: string of the date of the file
        :param time_dict: dictionary of login time per user
        :return:
        """
        df = pd.DataFrame(df, index=time_dict.keys())   # updating the indexes to be up-to-date with all files
        df[col_name] = df.index.map(time_dict)
        return df


    def add_names(self, df, time_dict):
        """
        add the updated names to the second row of the DataFrame
        :param df: pd.DataFrame
        :param time_dict: dictionary of names
        :return:
        """
        names = {}
        for key in time_dict.keys():
            names[key] = time_dict[key]['name']

        names_col = df.index.map(names)
        df.insert(loc=0, column='names', value=names_col)
        return df


    def add_avg_time(self, df, sum_max):
        """
        adds an average time row to the end of the DataFrame
        :param df: pd.DataFrame
        :param sum_max: sum of maximum time of every row
        :return: pd.DataFrame
        """
        sum_row = pd.DataFrame(df.sum(axis=1, numeric_only=True))
        avg = {}
        i = 0
        for idx in df.index:
            avg[idx] = str((sum_row.iloc[i, 0] / sum_max) * 100) + " %"
            i += 1
        df['average'] = df.index.map(avg)
        return df


    def main(self, path):
        if not os.path.isdir(path):
            print("This path is not a directory")
            exit(1)

        new_df, csv_files, init_dict = self.init(path)
        sum_maxes = 0
        for csv in csv_files:
            new_df, max_row = self.add_csv(csv, init_dict, new_df)
            sum_maxes += max_row

        new_df.sort_index(axis=1, inplace=True)
        new_df = self.add_avg_time(new_df, sum_maxes)
        new_df = self.add_names(new_df, init_dict)
        new_df.to_csv('attendance.csv')
