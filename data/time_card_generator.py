__author__ = "Cal Ochoa"
__email__ = "CalOchoa@gmail.com"

from timesheet import Timesheet


class TimeCardGenerator(object):

    def __init__(self, excel_spreadsheet_filename, sheet_name):
        self.timesheet = Timesheet(excel_spreadsheet_filename, sheet_name=sheet_name)


def __test_me(excel_spreadsheet_filename, sheet_name):
    test_tc_generator = TimeCardGenerator(excel_spreadsheet_filename, sheet_name)
    for employee_id in test_tc_generator.timesheet.id_wtc_dict.keys():
        wtc = test_tc_generator.timesheet.id_wtc_dict.get(employee_id)
        print('{0} ({1}): {2}'.format(wtc.employee.employee_name, employee_id, wtc.total_weekly_hours))


if __name__ == "__main__":
    print('Start Testing TimeCardGenerator...\n')

    #test_excel_spreadsheet_filename = 'resources/Schedule Example.xlsx'
    #test_sheet_name = 'WEEK 1_HARTNELL Schedule Templa'
    #test_sheet_name = 'WEEK 1_COLLEGE Schedule Templat'
    #test_sheet_name = 'WEEK 2_HARTNELL Schedule Templa'
    #test_sheet_name = 'WEEK 2_COLLEGE Schedule Templat'
    test_sheet_name = None

    test_excel_spreadsheet_filename = 'resources/Grid Sample (Color Coded).xlsx'
    test_sheet_name = ' POSTED + 1to1 1232022-1302022'
    #test_sheet_name = 'REAL ABORN SCHEDULE NO 1-1s jus'
    __test_me(test_excel_spreadsheet_filename, test_sheet_name)

    print('\nEnd Testing TimeCardGenerator\n')
 