__author__ = "Cal Ochoa"
__email__ = "CalOchoa@gmail.com"

import pandas as pd

from weekly_time_card import WeeklyTimeCard
from employee import Employee


class Timesheet(object):
    
    WKLY_DATE_STR_PREFIX = 'for the week of'
    WKLY_DATE_ROW_IDX = 1

    def __init__(self, excel_spreadsheet_filename):
        self.df = pd.read_excel(excel_spreadsheet_filename, header=None)
        col1_list = self.__get_col_values(0)
        col2_list = self.__get_col_values(1)
        self.entity_name = self.__get_entity_name(col1_list)
        self.weekly_date_str = self.__get_weekly_date_str()
        self.id_wtc_dict = self.__get_id_wtc_dict(col1_list, col2_list)
        self.tci_index_list, self.tci_str_list = self.__get_tci_data_lists(col1_list)
        self.__populate_weekly_time_cards()

    def __populate_weekly_time_cards(self):
        # TODO: populate WeeklyTimeCard for each employee
        days_row_idx = self.tci_index_list[0] - 1
        days_list = self.__get_row_values(days_row_idx)
        found_day = False
        count = 0
        for col_idx, col_value in enumerate(days_list):
            if found_day:
                if self.__is_matching_text(col_value, 'Hours'):
                    break
                count += 1
                # TODO: iterate over all the columns, but need to keep track of the correct day
                # self.__get_col_values(col_idx)
                    # TODO: only iterate over the correct rows
                    # see: self.tci_index_list, self.tci_str_list
            if self.__is_matching_text(col_value, 'Monday'):
                found_day = True
        print('count: {0}'.format(count))
        #self.__get_col_values(2)

    def __get_col_values(self, col_idx):
        """
        Get the list of column values for given column index.
        :param col_idx: column index
        :return: list of column values
        """
        return self.df.iloc[:, col_idx].tolist()

    def __get_row_values(self, row_idx):
        """
        Get the list of row values for given row index.
        :param row_idx: row index
        :return: list of row values
        """
        return self.df.iloc[row_idx].tolist()

    @staticmethod
    def __get_entity_name(col_list):
        """
        Get the entity name from the given column list.
        :param col_list: column list
        :return: entity name
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
                if self.__is_matching_text(col1, 'Total Hours'):
                    break
                employee_id = col1.strip()
                employee_name = col2.strip()
                employee = Employee(employee_id, employee_name, self.entity_name)
                id_wtc_dict[employee_id] = WeeklyTimeCard(self.weekly_date_str, employee)
            if self.__is_matching_text(col1, 'Staff'):
                found_employee = True
        return id_wtc_dict
    
    @staticmethod
    def __is_matching_text(cell_value, input_text):
        """
        Check if the cell value exists, is a string, and matches the input text.
        :param cell_value: cell value
        :param input_text: input text to match
        :return: boolean status 
        """
        return cell_value and not pd.isna(cell_value) and isinstance(cell_value, str) \
            and cell_value.lower().strip() == input_text.lower()

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
            if self.__is_matching_text(col, 'Hours'):
                found_tci = True
        return tci_index_list, tci_str_list

    def display_contents(self):
        print('***** Timesheet *****')
        print('Entity Name: {0}'.format(self.entity_name))
        print('Weekly Date Str: {0}'.format(self.weekly_date_str))




if __name__ == "__main__":
    print('Start Testing Timesheet...\n')

    test_timesheet = Timesheet('resources/Schedule Example.xlsx')
    test_timesheet.display_contents()

    print('\nEnd Testing Timesheet\n')
 