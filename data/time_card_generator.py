__author__ = "Cal Ochoa"
__email__ = "CalOchoa@gmail.com"

from timesheet import Timesheet
from wtc_template import WeeklyTimeCardTemplate


class TimeCardGenerator(object):

    def __init__(self, excel_spreadsheet_filename, sheet_name_1, sheet_name_2=None):
        timesheet_1 = Timesheet(excel_spreadsheet_filename, sheet_name=sheet_name_1)
        timesheet_2 = Timesheet(excel_spreadsheet_filename, sheet_name=sheet_name_2) if sheet_name_2 else None
        self.weekly_time_cards = self.__get_weekly_time_cards(timesheet_1, timesheet_2)
        self.wtc_template = WeeklyTimeCardTemplate()

    def __get_weekly_time_cards(self, timesheet_1, timesheet_2):
        weekly_time_cards = []
        if timesheet_2:
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

    def populate_html_template(self):
        for weekly_time_card in self.weekly_time_cards:
            file_path = 'output/{0}'.format(self.__get_file_name(weekly_time_card))
            html_content = self.wtc_template.get_populated_template1(weekly_time_card)
            self.write_html_file(file_path, html_content)

    @staticmethod
    def __get_file_name(weekly_time_card):
        file_name = weekly_time_card.employee.employee_name.replace(' ', '_')
        if file_name.endswith('.'):
            file_name = file_name[:-1]
        return '{0}.html'.format(file_name)

    def write_html_file(self, file_path, content):
        with open(file_path, 'w') as file:
            file.write(content)
        print(f"HTML file '{file_path}' has been created.")



def __test_me(excel_spreadsheet_filename, sheet_name_1, sheet_name_2=None):
    test_tc_generator = TimeCardGenerator(excel_spreadsheet_filename, sheet_name_1, sheet_name_2=sheet_name_2)
    test_tc_generator.populate_html_template()


if __name__ == "__main__":
    print('Start Testing TimeCardGenerator...\n')

    #test_excel_spreadsheet_filename = 'resources/Schedule Example.xlsx'
    #test_sheet_name = 'WEEK 1_HARTNELL Schedule Templa'
    #test_sheet_name = 'WEEK 1_COLLEGE Schedule Templat'
    #test_sheet_name = 'WEEK 2_HARTNELL Schedule Templa'
    #test_sheet_name = 'WEEK 2_COLLEGE Schedule Templat'
    #test_sheet_name = None

    #test_excel_spreadsheet_filename = 'resources/Grid Sample (Color Coded).xlsx'
    #test_sheet_name = ' POSTED + 1to1 1232022-1302022'
    #test_sheet_name = 'REAL ABORN SCHEDULE NO 1-1s jus'


    #test_excel_spreadsheet_filename = 'resources/Schedule Example #2.xlsx'
    test_excel_spreadsheet_filename = 'resources/Schedule Example #3.xlsx'
    #test_sheet_name_1 = 'WEEK 1_HARTNELL Schedule Templa'
    #test_sheet_name_2 = 'WEEK 1_COLLEGE Schedule Templat'
    test_sheet_name_1 = 'WEEK 2_HARTNELL Schedule Templa'
    test_sheet_name_2 = 'WEEK 2_COLLEGE Schedule Templat'
    __test_me(test_excel_spreadsheet_filename, test_sheet_name_1, test_sheet_name_2)

    print('\nEnd Testing TimeCardGenerator\n')
 