__author__ = "Cal Ochoa"
__email__ = "CalOchoa@gmail.com"

import pandas as pd

from weekly_time_card import WeeklyTimeCard
from employee import Employee


class Timesheet(object):
    
    WKLY_DATE_STR_PREFIX = 'for the week of'
    WKLY_DATE_ROW_IDX = 1

    DAYS = {'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'}

    def __init__(self, excel_spreadsheet_filename, sheet_name=None):
        self.df = self.__get_data_frame(excel_spreadsheet_filename, sheet_name)
        col1_list = self.__get_col_values(0)
        col2_list = self.__get_col_values(1)
        self.entity_facility_name = self.__get_entity_facility_name(col1_list)
        self.weekly_date_str = self.__get_weekly_date_str()
        self.id_wtc_dict = self.__get_id_wtc_dict(col1_list, col2_list)
        self.tci_index_list, self.tci_str_list = self.__get_tci_data_lists(col1_list)
        self.__populate_weekly_time_cards()

    @staticmethod
    def __get_data_frame(excel_spreadsheet_filename, sheet_name):
        """
        Get the data frame for the given excel spreadsheet file name and sheet name
        (if provided).
        :param excel_spreadsheet_filename: excel spreadsheet file name
        :param sheet_name: sheet name
        :return: data frame
        """
        data_frame = None
        if sheet_name:
            xls = pd.ExcelFile(excel_spreadsheet_filename)
            data_frame = pd.read_excel(xls, sheet_name, header=None)
        else:
            data_frame = pd.read_excel(excel_spreadsheet_filename, header=None)
        return data_frame

    def __get_col_values(self, col_idx, start_row=-1, end_row=-1):
        """
        Get the list of column values for given column index.
        If the start and end rows are provided, then use them as
        the lower and upper bound respectively.
        :param col_idx: column index
        :param start_row: starting row
        :param end_row: ending row
        :return: list of column values
        """
        col_values = []
        if start_row >=0 and end_row >= 0:
            col_values = self.df.iloc[start_row:end_row+1, col_idx].tolist()
        else:
            col_values = self.df.iloc[:, col_idx].tolist()
        return col_values

    def __get_row_values(self, row_idx):
        """
        Get the list of row values for given row index.
        :param row_idx: row index
        :return: list of row values
        """
        return self.df.iloc[row_idx].tolist()

    @staticmethod
    def __get_entity_facility_name(col_list):
        """
        Get the entity facility name from the given column list.
        :param col_list: column list
        :return: entity facility name
        """
        return col_list[0].strip() if col_list else 'No Entity Name Found'

    def __get_weekly_date_str(self):
        """
        Get the weekly date string from the list of row values from `WKLY_DATE_ROW_IDX`.
        :param row_list: list of row values
        :return: weekly date string
        """
        weekly_date_str = None
        for value in self.__get_row_values(self.WKLY_DATE_ROW_IDX):
            if not pd.isna(value) and isinstance(value, str) \
                    and value.lower().startswith(self.WKLY_DATE_STR_PREFIX):
                weekly_date_str = value.lower().replace(self.WKLY_DATE_STR_PREFIX, '').strip()
        return weekly_date_str

    def __get_id_wtc_dict(self, col1_list, col2_list):
        """
        Get the dictionary of employee id to WeeklyTimeCard object for the given
        list of input columns.
        :param col1_list: list of column1 values
        :param col2_list: list of column2 values
        :return: dict
        """
        id_wtc_dict = {}
        found_employee = False
        for col1, col2 in zip(col1_list, col2_list):
            if found_employee:
                if self.__matches_text(col1, 'Total Hours'):
                    break
                if self.__is_valid_str(col2):
                    employee_id = col1.strip()
                    employee_name = col2.strip()
                    employee = Employee(employee_id, employee_name, self.entity_facility_name)
                    id_wtc_dict[employee_id] = WeeklyTimeCard(self.weekly_date_str, employee)
            if self.__matches_text(col1, 'Staff'):
                found_employee = True
        return id_wtc_dict

    def __matches_text(self, cell_value, input_text):
        """
        Check if the cell value has a valid string and matches the input text.
        :param cell_value: cell value
        :param input_text: input text to match
        :return: boolean status 
        """
        return self.__is_valid_str(cell_value) and cell_value.lower().strip() == input_text.lower()

    def __exists_in_set(self, cell_value, input_set):
        """
        Check if the cell value has a valid string and exists in the input set.
        :param cell_value: cell value
        :param input_text: input set
        :return: boolean status 
        """
        return self.__is_valid_str(cell_value) and cell_value.lower().strip() in input_set

    @staticmethod
    def __is_valid_str(cell_value):
        """
        Check if the cell value exists and is a string.
        :param cell_value: cell value
        :return: boolean status 
        """
        return cell_value and not pd.isna(cell_value) and isinstance(cell_value, str)

    def __get_tci_data_lists(self, col_list):
        """
        Get the lists of TimeCardIncrements indices and strings.
        :param col_list: list of column values
        :return: list of indices, list of strings
        """
        tci_index_list = []
        tci_str_list = []
        found_tci = False
        for idx, col in enumerate(col_list):
            if found_tci:
                if pd.isna(col):
                    break
                tci_index_list.append(idx)
                tci_str_list.append(col.strip())
            if self.__matches_text(col, 'Hours'):
                found_tci = True
        return tci_index_list, tci_str_list

    def __populate_weekly_time_cards(self):
        """
        Populate the WeeklyTimeCard for each employee.  
        1. Get the list of days to list of column indices (ie day index matrix)
        2. Iterate over each list of column indices for the given day
        3. Iterate over each column index
        4. Iterate over each row associated with a time increment
        5. Find entries where employees are working
        6. Add the time increments to their daily time card
        """
        for day_idx, day_col_idx_list in enumerate(self.__get_day_idx_matrix()):
            for day_col_idx in day_col_idx_list:
                col_values = self.__get_col_values(
                    day_col_idx, start_row=self.tci_index_list[0], end_row=self.tci_index_list[-1]
                )
                for tci_str, col_val in zip(self.tci_str_list, col_values):
                    if self.__is_valid_str(col_val):
                        employee_id = col_val.strip()
                        weekly_time_card = self.id_wtc_dict.get(employee_id)
                        if weekly_time_card:
                            weekly_time_card.add_time_inc(day_idx, tci_str)
                        else:
                            print('Employee ID: `{}` not found'.format(employee_id))

    def __get_day_idx_matrix(self):
        """
        Get a matrix of days to indices.  Start a new list once we see a day.
        Accumulate as long as we see `nan` or a new day, and stop otherwise.
        :return: day index matrix
        """
        days_row_idx = self.tci_index_list[0] - 1
        days_list = self.__get_row_values(days_row_idx)
        day_idx_matrix = []
        day_idx_list = []
        for col_idx, col_value in enumerate(days_list):
            if self.__exists_in_set(days_list[col_idx], self.DAYS):
                day_idx_list = []
                day_idx_matrix.append(day_idx_list)
                day_idx_list.append(col_idx)
            elif not self.__is_valid_str(days_list[col_idx]):
                day_idx_list.append(col_idx)
            elif day_idx_matrix:
                break
        return day_idx_matrix

    def display_contents(self):
        print('***** Timesheet *****')
        print('Entity Facility Name: {0}'.format(self.entity_facility_name))
        print('Weekly Date Str: {0}'.format(self.weekly_date_str))


if __name__ == "__main__":
    print('Start Testing Timesheet...\n')

    test_timesheet = Timesheet('resources/Schedule Example.xlsx')
    test_timesheet.display_contents()
    for employee_id in test_timesheet.id_wtc_dict.keys():
        wtc = test_timesheet.id_wtc_dict.get(employee_id)
        print('{0} ({1}): {2}'.format(wtc.employee.employee_name, employee_id, wtc.total_weekly_hours))

    print('\nEnd Testing Timesheet\n')
 