__author__ = "Cal Ochoa"
__email__ = "CalOchoa@gmail.com"

import pandas as pd
import zipfile
import os

from timesheet import Timesheet
from wtc_template import WeeklyTimeCardTemplate


class TimeCardGenerator(object):
    """
    Generate time cards (as html files) for each employee based on the weekly schedules
    displayed in the excel spreadsheet.
    """

    WEEK_1 = 'week 1'
    WEEK_2 = 'week 2'

    def __init__(self, excel_spreadsheet_filename):
        sheet_names = self.__get_sheet_names(excel_spreadsheet_filename)
        week_1_timesheets = self.__get_weekly_timesheets(excel_spreadsheet_filename, sheet_names, self.WEEK_1)
        week_2_timesheets = self.__get_weekly_timesheets(excel_spreadsheet_filename, sheet_names, self.WEEK_2)
        self.week_1_time_cards = self.__get_weekly_time_cards(week_1_timesheets)
        self.week_2_time_cards = self.__get_weekly_time_cards(week_2_timesheets)
        self.wtc_template = WeeklyTimeCardTemplate()

    @staticmethod
    def __get_sheet_names(excel_spreadsheet_filename):
        """
        Get the sheet names for the given excel file.
        :param excel_spreadsheet_filename: excel file
        :return: list of sheet names
        """
        sheet_names = []
        try:
            xls = pd.ExcelFile(excel_spreadsheet_filename)
            sheet_names = xls.sheet_names
        except Exception as e:
            print(f"Error reading the Excel file: {e}")
        return sheet_names

    @staticmethod
    def __get_weekly_timesheets(excel_spreadsheet_filename, sheet_names, week_x_name):
        """
        Get the weekly Timesheet objects for the given excel file and weekly sheet names that start
        with the `week_x_name`.
        :param excel_spreadsheet_filename: excel file
        :param sheet_names: list of sheet names
        :return: list of Timesheet objects
        """
        week_x_sheet_names = [sheet for sheet in sheet_names if sheet.lower().startswith(week_x_name)]
        return [Timesheet(excel_spreadsheet_filename, sheet_name=sheet) for sheet in week_x_sheet_names]

    def __get_weekly_time_cards(self, weekly_timesheets):
        """
        Get the weekly time cards for the given weekly timesheets.  Currently, there should only be 
        at most 2 timesheets (ie 2 facilities) for a given week.  If there are 2 timesheets, then
        we want to check if a person worked at both facilities and combine there hours into a single
        time card.
        :param weekly_timesheets: list of Timesheet objects
        :return: list of WeeklyTimeCard objects
        """
        weekly_time_cards = []
        timesheet_1 = weekly_timesheets[0]
        if len(weekly_timesheets) == 2:
            timesheet_2 = weekly_timesheets[1]
            employee_name_wtc_dict_1 = timesheet_1.employee_name_wtc_dict 
            employee_name_wtc_dict_2 = timesheet_2.employee_name_wtc_dict 
            # iterate over 1st timesheet and add all values while combining duplicate employees from 2nd timesheet
            for employee_name, wtc in employee_name_wtc_dict_1.items():
                wtc_2 = employee_name_wtc_dict_2.get(employee_name)
                if wtc_2 and wtc.weekly_date_str == wtc_2.weekly_date_str:
                    wtc.employee.facility_name += ' & {0}'.format(wtc_2.employee.facility_name)
                    wtc.total_weekly_hours += wtc_2.total_weekly_hours
                    for idx, daily_time_card_1 in enumerate(wtc.daily_time_card_list):
                        daily_time_card_2 = wtc_2.daily_time_card_list[idx]
                        daily_time_card_1.total_daily_hours += daily_time_card_2.total_daily_hours
                        if daily_time_card_2.in_out_hours_list:
                            if daily_time_card_1.in_out_hours_list:
                                daily_time_card_1.in_out_hours_list = self.__combine_in_out_hour_lists(
                                    daily_time_card_1.in_out_hours_list, daily_time_card_2.in_out_hours_list
                                )
                            else:
                                daily_time_card_1.in_out_hours_list = daily_time_card_2.in_out_hours_list
                    weekly_time_cards.append(wtc)
                    del employee_name_wtc_dict_2[employee_name]
                else:
                    weekly_time_cards.append(wtc)
            # iterate over 2nd timesheet and add all values while ignoring duplicate employees from 1st timesheet
            for wtc in employee_name_wtc_dict_2.values():
                weekly_time_cards.append(wtc)
        else:
            weekly_time_cards = timesheet_1.id_wtc_dict.values()
        return weekly_time_cards

    @staticmethod
    def __combine_in_out_hour_lists(list1, list2):
        """
        Combine the list of in out hours for the given inputs.
        :param list1: list 1
        :param list2: list 2
        :return: combined list
        """
        combined_list = []
        index1 = 0
        index2 = 0
        while index1 < len(list1) and index2 < len(list2):
            if list1[index1].start_time < list2[index2].start_time:
                combined_list.append(list1[index1])
                index1 += 1
            else:
                combined_list.append(list2[index2])
                index2 += 1
        # Append remaining elements from list1 (if any)
        combined_list.extend(list1[index1:])
        # Append remaining elements from list2 (if any)
        combined_list.extend(list2[index2:])
        return combined_list

    def create_html_time_cards(self):
        """
        Create the all the time cards as an html file and store them in a separate folder
        based on week.  Also, create a zip file of the final output.
        """
        output_dir = 'output/time cards'
        self.__populate_html_template(self.week_1_time_cards, '{0}/{1}/'.format(output_dir, self.WEEK_1))
        self.__populate_html_template(self.week_2_time_cards, '{0}/{1}/'.format(output_dir, self.WEEK_2))
        self.create_zip_from_directory(output_dir, 'output/my_time_cards.zip')

    def __populate_html_template(self, week_x_time_cards, output_dir):
        """
        Create each time cards as an html file and store them in the given output directory. 
        More specifically, populate the html template with the data from each WeeklyTimeCard object.
        :param week_x_time_cards: list of WeeklyTimeCard objects
        :param week_x_name: output directory name
        """
        self.__create_dir_if_not_exists(output_dir)
        for weekly_time_card in week_x_time_cards:
            file_path = '{0}{1}'.format(output_dir, self.__get_file_name(weekly_time_card))
            html_content = self.wtc_template.get_populated_template(weekly_time_card)
            self.__write_html_file(file_path, html_content)

    @staticmethod
    def __create_dir_if_not_exists(directory_path):
        """
        Create the directory if does not already exist.
        :param directory_path: directory path
        """
        try:
            if not os.path.exists(directory_path):
                os.makedirs(directory_path)
                print(f"Directory '{directory_path}' created successfully.")
            else:
                print(f"Directory '{directory_path}' already exists.")
        except Exception as e:
            print(f"Error creating directory: {e}")

    @staticmethod
    def __get_file_name(weekly_time_card):
        """
        Get the file name for the given WeeklyTimeCard object by using the employee's name
        and replacing spaces with underscores.  If the name ends with a period, then remove it.
        :param weekly_time_card: WeeklyTimeCard object
        :return: file name
        """
        file_name = weekly_time_card.employee.employee_name.replace(' ', '_')
        if file_name.endswith('.'):
            file_name = file_name[:-1]
        return '{0}.html'.format(file_name)

    @staticmethod
    def __write_html_file(file_path, content):
        """
        Write the html content to a file.
        :param file_path: file path
        :param content: html content
        """
        with open(file_path, 'w') as file:
            file.write(content)
        print(f"HTML file '{file_path}' has been created.")

    @staticmethod
    def create_zip_from_directory(directory_path, zip_file_path):
        """
        Create a zip file from the given directory path.
        :param directory_path: directory path
        :param zip_file_path: zip file path to create
        """
        with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(directory_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, directory_path)
                    zipf.write(file_path, relative_path)
        print(f"Zip file '{zip_file_path}' has been created.")


if __name__ == "__main__":
    print('Start Testing TimeCardGenerator...\n')

    #test_excel_spreadsheet_filename = 'resources/Schedule Example.xlsx'

    #test_excel_spreadsheet_filename = 'resources/Grid Sample (Color Coded).xlsx'
    #test_sheet_name = ' POSTED + 1to1 1232022-1302022'
    #test_sheet_name = 'REAL ABORN SCHEDULE NO 1-1s jus'

    #test_excel_spreadsheet_filename = 'resources/Schedule Example #2.xlsx'
    test_excel_spreadsheet_filename = 'resources/Schedule Example #3.xlsx'
    test_tc_generator = TimeCardGenerator(test_excel_spreadsheet_filename)
    test_tc_generator.create_html_time_cards()

    print('\nEnd Testing TimeCardGenerator\n')
 