__author__ = "Cal Ochoa"
__email__ = "CalOchoa@gmail.com"

import pandas as pd
import zipfile
import os
import copy

from timesheet import Timesheet
from weekly_time_card import WeeklyTimeCard
from daily_time_card import DailyTimeCard
from pay_period import PayPeriod
from wtc_template import WeeklyTimeCardTemplate
from summary_template import SummaryTemplate


class TimeCardGenerator(object):
    """
    Generate time cards (as html files) for each employee based on the weekly schedules
    displayed in the excel spreadsheet.
    """

    WEEK_1 = 'week 1'
    WEEK_2 = 'week 2'

    def __init__(self, excel_spreadsheet_filename):
        sheet_names = self.__get_sheet_names(excel_spreadsheet_filename)
        self.week_1_timesheets = self.__get_weekly_timesheets(excel_spreadsheet_filename, sheet_names, self.WEEK_1)
        self.week_2_timesheets = self.__get_weekly_timesheets(excel_spreadsheet_filename, sheet_names, self.WEEK_2)
        self.week_1_time_cards = self.__get_weekly_time_cards(self.week_1_timesheets)
        self.week_2_time_cards = self.__get_weekly_time_cards(self.week_2_timesheets)
        self.employee_name_pay_period_dict = self.__get_employee_name_pay_period_dict(
            self.week_1_time_cards, self.week_2_time_cards
        )
        self.wtc_template = WeeklyTimeCardTemplate()
        self.summary_template = SummaryTemplate()

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
            employee_name_set = set()
            # iterate over 1st timesheet and add all values while combining duplicate employees from 2nd timesheet
            for employee_name, original_wtc in employee_name_wtc_dict_1.items():
                employee_name_set.add(employee_name)
                wtc = copy.deepcopy(original_wtc)
                wtc_2 = employee_name_wtc_dict_2.get(employee_name)
                if wtc_2 and wtc.weekly_date_str == wtc_2.weekly_date_str:
                    wtc.employee.facility_name += ' & {0}'.format(wtc_2.employee.facility_name)
                    wtc.total_weekly_hours += wtc_2.total_weekly_hours
                    self.__adjust_summary_hours_multiple_facilities(original_wtc, wtc_2)
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
                    #del employee_name_wtc_dict_2[employee_name]
                else:
                    weekly_time_cards.append(wtc)
            # iterate over 2nd timesheet and add all values while ignoring duplicate employees from 1st timesheet
            for employee_name, original_wtc in employee_name_wtc_dict_2.items():
                if employee_name not in employee_name_set:
                    weekly_time_cards.append(copy.deepcopy(original_wtc))
        else:
            weekly_time_cards = timesheet_1.id_wtc_dict.values()
        return weekly_time_cards

    def __adjust_summary_hours_multiple_facilities(self, wtc_1, wtc_2):
        """
        Correctly caclulate the summary hours for an employee who works in multiple facilities.
        Ensure that each facility is showing the correct overtime hours as both facilities
        need to be accounted for.
        :param wtc_1: WeeklyTimeCard object 1
        :param wtc_2: WeeklyTimeCard object 2
        """
        current_weekly_hours = 0
        for idx, dtc_1 in enumerate(wtc_1.daily_time_card_list):
            current_daily_hours = 0
            dtc_2 = wtc_2.daily_time_card_list[idx]
            total_daily_hours = dtc_1.total_daily_hours + dtc_2.total_daily_hours
            # check if we will exceed normal weekly or daily hours
            if self.__has_weekly_ot_hours(current_weekly_hours, total_daily_hours) \
                    or self.__has_daily_ot_hours(current_daily_hours, total_daily_hours):
                # accumulate overtime hours in the correct WeeklyTimeCard
                index1 = 0
                index2 = 0
                list1 = dtc_1.in_out_hours_list
                list2 = dtc_2.in_out_hours_list
                # iterate over both lists until there are no more hours
                while index1 < len(list1) or index2 < len(list2):
                    # check if both lists have hours
                    if index1 < len(list1) and index2 < len(list2):
                        if list1[index1].start_time < list2[index2].start_time:
                            current_weekly_hours, current_daily_hours = self.__add_extra_ot_hours(
                                wtc_1, current_weekly_hours, current_daily_hours, list1[index1].time_diff
                            )
                            index1 += 1
                        else:
                            current_weekly_hours, current_daily_hours = self.__add_extra_ot_hours(
                                wtc_2, current_weekly_hours, current_daily_hours, list2[index2].time_diff
                            )
                            index2 += 1
                    # check if list 1 has hours
                    elif index1 < len(list1):
                        current_weekly_hours, current_daily_hours = self.__add_extra_ot_hours(
                            wtc_1, current_weekly_hours, current_daily_hours, list1[index1].time_diff
                        )
                        index1 += 1
                    # check if list 2 has hours
                    else:
                        current_weekly_hours, current_daily_hours = self.__add_extra_ot_hours(
                            wtc_2, current_weekly_hours, current_daily_hours, list2[index2].time_diff
                        )
                        index2 += 1
            else:
                current_weekly_hours += total_daily_hours

    def __has_weekly_ot_hours(self, hours_1, hours_2):
        """
        Check if the combined input hours exceeds the normal weekly hours, and therefore,
        would qualify for having overtime hours.
        :param hours1: hours 1
        :param hours2: hours 2
        :return: boolean status
        """
        return self.__has_ot_hours(hours_1, hours_2, WeeklyTimeCard.NORMAL_HOURS)

    def __has_daily_ot_hours(self, hours_1, hours_2):
        """
        Check if the combined input hours exceeds the normal daily hours, and therefore,
        would qualify for having overtime hours.
        :param hours1: hours 1
        :param hours2: hours 2
        :return: boolean status
        """
        return self.__has_ot_hours(hours_1, hours_2, DailyTimeCard.NORMAL_HOURS)

    @staticmethod
    def __has_ot_hours(hours_1, hours_2, normal_hours):
        """
        Check if the combined input hours exceeds the normal hours, and therefore,
        would qualify for having overtime hours.
        :param hours1: hours 1
        :param hours2: hours 2
        :param normal_hours: normal hours
        :return: boolean status
        """
        return hours_1 + hours_2 > normal_hours

    def __add_extra_ot_hours(self, weekly_time_card, current_weekly_hours, current_daily_hours, shift_hours):
        """
        Add the extra overtime hours (if any) to the WeeklyTimeCard object, given the current
        weekly hours, current daily hours, and shift hours. Afterwards, return the newly updated
        current weekly hours and current daily hours after including the shift hours.
        :param weekly_time_card: WeeklyTimeCard object
        :param current_weekly_hours: current weekly hours
        :param current_daily_hours: current daily hours
        :param shift_hours: shift hours
        :return: current weekly hours, current daily hours
        """
        extra_ot_hours = self.__get_extra_ot_hours(current_weekly_hours, current_daily_hours, shift_hours)
        if extra_ot_hours:
            weekly_time_card.add_extra_ot_hours(extra_ot_hours)
        current_weekly_hours += shift_hours
        current_daily_hours += shift_hours
        return current_weekly_hours, current_daily_hours
    
    def __get_extra_ot_hours(self, current_weekly_hours, current_daily_hours, shift_hours):
        """
        Get the extra overtime hours based on the current weekly hours, current daily hours,
        and input shift hours.
        :param current_weekly_hours: current weekly hours
        :param current_daily_hours: current daily hours
        :param shift_hours: shift hours
        :return: extra overtime hours
        """
        weekly_ot_hours = self.__get_weekly_ot_hours(current_weekly_hours, shift_hours)
        daily_ot_hours = self.__get_daily_ot_hours(current_daily_hours, shift_hours)
        # use maximum between weekly and daily overtime hours to avoid overlap
        return max(weekly_ot_hours, daily_ot_hours)

    def __get_weekly_ot_hours(self, current_weekly_hours, shift_hours):
        """
        Get the overtime hours from the combined input hours.  More specifically, get the hours
        that exceed the normal weekly hours, after you combine the input hours.
        :param current_weekly_hours: current weekly hours
        :param shift_hours: shift hours
        :return: overtime hours
        """
        return self.__get_ot_hours(current_weekly_hours, shift_hours, WeeklyTimeCard.NORMAL_HOURS)

    def __get_daily_ot_hours(self, current_daily_hours, shift_hours):
        """
        Get the overtime hours from the combined input hours.  More specifically, get the hours
        that exceed the normal daily hours, after you combine the input hours.
        :param current_daily_hours: current daily hours
        :param shift_hours: shift hours
        :return: overtime hours
        """
        return self.__get_ot_hours(current_daily_hours, shift_hours, DailyTimeCard.NORMAL_HOURS)

    @staticmethod
    def __get_ot_hours(current_hours, shift_hours, normal_hours):
        """
        Get the overtime hours from the combined input hours.  More specifically, get the hours
        that exceed the normal hours, after you combine the input hours.
        :param current_hours: current hours
        :param shift_hours: shift hours
        :param normal_hours: normal hours
        :return: overtime hours
        """
        ot_hours = 0
        if current_hours > normal_hours:
            ot_hours = shift_hours
        else:
            ot_hours = max(current_hours + shift_hours - normal_hours, ot_hours)
        return ot_hours

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
        # create summary hours first because it will made and adjustments to the daily time cards
        output_dir = 'output/summary + time cards/'
        self.__create_dir_if_not_exists(output_dir)
        html_content = self.summary_template.get_populated_template(
            self.employee_name_pay_period_dict, self.week_1_timesheets, self.week_2_timesheets
        )
        self.__write_html_file(output_dir + 'summary_hours.html', html_content)

        tc_output_dir = output_dir + 'time cards'
        self.__populate_tc_html_template(self.week_1_time_cards, '{0}/{1}/'.format(tc_output_dir, self.WEEK_1))
        self.__populate_tc_html_template(self.week_2_time_cards, '{0}/{1}/'.format(tc_output_dir, self.WEEK_2))
        self.create_zip_from_directory(output_dir, 'output/summary+time_cards.zip')

    def __populate_tc_html_template(self, week_x_time_cards, output_dir):
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

    def __get_employee_name_pay_period_dict(self, week_1_time_cards, week_2_time_cards):
        """
        Get the dictionary of employee name to PayPeriod object using the
        week 1 time cards and week 2 time cards.
        :param week_1_time_cards: list of week 1 WeeklyTimeCard objects
        :param week_2_time_cards: list of week 2 WeeklyTimeCard objects
        :return: dictionary
        """
        employee_name_pay_period_dict = {}
        # populate the pay periods with the week 1 time cards
        for wtc_1 in week_1_time_cards:
            employee_name = wtc_1.employee.employee_name
            pay_period = PayPeriod(employee_name, wtc_1.employee.facility_name)
            employee_name_pay_period_dict[employee_name] = pay_period
            pay_period.weekly_time_card_1 = wtc_1
        # populate the pay periods with the week 2 time cards
        for wtc_2 in week_2_time_cards:
            employee_name = wtc_2.employee.employee_name
            pay_period = employee_name_pay_period_dict.get(employee_name)
            if not pay_period:
                pay_period = PayPeriod(employee_name, wtc_2.employee.facility_name)
                employee_name_pay_period_dict[employee_name] = pay_period
            pay_period.weekly_time_card_2 = wtc_2
        return employee_name_pay_period_dict


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
 