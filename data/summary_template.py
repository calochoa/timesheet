__author__ = "Cal Ochoa"
__email__ = "CalOchoa@gmail.com"

from pay_period import PayPeriod


class SummaryTemplate(object):

    def __init__(self):
        pass

    def get_populated_template(
        self, employee_name_pay_period_dict, week_1_timesheets, week_2_timesheets
    ):
        template = self.__get_html_template()
        combined_summary_hours_table = self.__get_combined_summary_hours_table(
            employee_name_pay_period_dict
        )
        facility_summary_hours_table_list = self.__get_facility_summary_hours_table_list(
            week_1_timesheets, week_2_timesheets
        )
        return template.format(
            style = self.__get_style(), 
            combined_summary_hours_table = combined_summary_hours_table,
            facility_summary_hours_tables = '<br/>'.join(elt for elt in facility_summary_hours_table_list)
        )

    @staticmethod
    def __get_html_template():
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Summary Hours</title>{style}
        </head>
        <body>
            <div id="header"></div>
            {combined_summary_hours_table}<br/>{facility_summary_hours_tables}
            <div id="footer"></div>
        </body>
        </html>
        '''

    def __get_combined_summary_hours_table(self, employee_name_pay_period_dict):
        employee_summary_hours_list = []
        total_w1_reg_hours, total_w1_ot_hours, total_w2_reg_hours, total_w2_ot_hours, \
            total_total_reg_hours, total_total_ot_hours, total_total_hours = 0, 0, 0, 0, 0, 0, 0
        for employee_name, pay_period in employee_name_pay_period_dict.items():
            w1_reg_hours, w1_ot_hours, w2_reg_hours, w2_ot_hours, total_reg_hours, \
                total_ot_hours, total_hours = pay_period.get_summary_hours(
                    pay_period.weekly_time_card_1, pay_period.weekly_time_card_2
                )
            employee_summary_hours_list.append(
                self.__get_facility_employee_summary_hours(
                    employee_name, w1_reg_hours, w1_ot_hours, w2_reg_hours, w2_ot_hours, 
                    total_reg_hours, total_ot_hours, total_hours, pay_period.facility_name
                )
            )
            total_w1_reg_hours += w1_reg_hours
            total_w1_ot_hours += w1_ot_hours
            total_w2_reg_hours += w2_reg_hours
            total_w2_ot_hours += w2_ot_hours
            total_total_reg_hours += total_reg_hours
            total_total_ot_hours += total_ot_hours
            total_total_hours += total_hours
        total_row = self.__get_total_row(
            total_w1_reg_hours, total_w1_ot_hours, total_w2_reg_hours, total_w2_ot_hours, 
            total_total_reg_hours, total_total_ot_hours, total_total_hours
        )
        return '''
            <table>{table_header_rows}{employee_rows}{total_row}
            </table>'''.format(
                table_header_rows = self.__get_table_header_rows(
                    'Summary Hours', row_2_name = 'Name', col_1_name = 'Staff', col_2_name = 'Facility'
                ),
                employee_rows = ''.join(elt for elt in employee_summary_hours_list),
                total_row = total_row
            )

    def __get_facility_summary_hours_table_list(self, week_1_timesheets, week_2_timesheets):
        """
        Get the tables containining the facility summary hours for the given week 1 timesheets
        and week 2 timesheets.
        :param week_1_timesheet: list of week 1 Timesheet object
        :param week_2_timesheet: list of week 2 Timesheet object
        :return: tables
        """
        facility_summary_hours_table_list = []
        for week_1_timesheet in week_1_timesheets:
            for week_2_timesheet in week_2_timesheets:
                if week_1_timesheet.entity_facility_name == week_2_timesheet.entity_facility_name:
                    facility_summary_hours_table_list.append(
                        self.__get_facility_employee_summary_hours_table(
                            week_1_timesheet.entity_facility_name, week_1_timesheet, week_2_timesheet
                        )
                    )
        return facility_summary_hours_table_list

    def __get_facility_employee_summary_hours_table(
        self, facility_name, week_1_timesheet, week_2_timesheet
    ):
        """
        Get the table containing the employee summary hours for a given facility, week 1
        timesheet, and week 2 timesheet.
        :param facility_name: facility name
        :param week_1_timesheet: week 1 Timesheet object
        :param week_2_timesheet: week 2 Timesheet object
        :return: table
        """
        employee_summary_hours_list = []
        employee_name_set = set()
        total_w1_reg_hours, total_w1_ot_hours, total_w2_reg_hours, total_w2_ot_hours, \
            total_total_reg_hours, total_total_ot_hours, total_total_hours = 0, 0, 0, 0, 0, 0, 0
        # iterate over the employees from the week 1 timesheet
        for employee_name, wtc_1 in week_1_timesheet.employee_name_wtc_dict.items():
            employee_name_set.add(employee_name)
            wtc_2 = week_2_timesheet.employee_name_wtc_dict.get(employee_name)
            # get the week 1, week 2 (if exists), and total hours for the employee
            w1_reg_hours, w1_ot_hours, w2_reg_hours, w2_ot_hours, total_reg_hours, \
                total_ot_hours, total_hours = PayPeriod.get_summary_hours(wtc_1, wtc_2)
            col_2_value = '{0} & {1}'.format(self.__get_id(wtc_1), self.__get_id(wtc_2))
            employee_summary_hours_list.append(
                self.__get_facility_employee_summary_hours(
                    employee_name, w1_reg_hours, w1_ot_hours, w2_reg_hours, w2_ot_hours, 
                    total_reg_hours, total_ot_hours, total_hours, col_2_value
                )
            )
            total_w1_reg_hours += w1_reg_hours
            total_w1_ot_hours += w1_ot_hours
            total_w2_reg_hours += w2_reg_hours
            total_w2_ot_hours += w2_ot_hours
            total_total_reg_hours += total_reg_hours
            total_total_ot_hours += total_ot_hours
            total_total_hours += total_hours

        # iterate over the employees from the week 2 timesheet
        for employee_name, wtc_2 in week_2_timesheet.employee_name_wtc_dict.items():
            # check if the employee is only in week 2
            if employee_name not in employee_name_set:
                # get the week 1 (does not exist), week 2, and total hours for the employee
                w1_reg_hours, w1_ot_hours, w2_reg_hours, w2_ot_hours, total_reg_hours, \
                    total_ot_hours, total_hours = pay_period.get_summary_hours(None, wtc_2)
                col_2_value = '{0} & {1}'.format(self.__get_id(wtc_1), self.__get_id(wtc_2))
                employee_summary_hours_list.append(
                    self.__get_facility_employee_summary_hours(
                        employee_name, w1_reg_hours, w1_ot_hours, w2_reg_hours, w2_ot_hours, 
                        total_reg_hours, total_ot_hours, total_hours, col_2_value
                    )
                )
                total_w1_reg_hours += w1_reg_hours
                total_w1_ot_hours += w1_ot_hours
                total_w2_reg_hours += w2_reg_hours
                total_w2_ot_hours += w2_ot_hours
                total_total_reg_hours += total_reg_hours
                total_total_ot_hours += total_ot_hours
                total_total_hours += total_hours
        total_row = self.__get_total_row(
            total_w1_reg_hours, total_w1_ot_hours, total_w2_reg_hours, total_w2_ot_hours, 
            total_total_reg_hours, total_total_ot_hours, total_total_hours
        )
        return '''
            <table>{table_header_rows}{employee_rows}{total_row}
            </table>'''.format(
                table_header_rows = self.__get_table_header_rows(facility_name),
                employee_rows = ''.join(elt for elt in employee_summary_hours_list),
                total_row = total_row
            )

    @staticmethod
    def __get_table_header_rows(
        facility_name, row_2_name = 'Staff', col_1_name = 'Name', col_2_name = 'Week 1 & 2 IDs'
    ):
        return '''
                <tr>
                    <th colspan="10">{facility_name}</th>
                </tr>
                <tr>
                    <th colspan="2">{row_2_name}</th>
                    <th colspan="2">Week 1 Hours</th>
                    <th colspan="2">Week 2 Hours</th>
                    <th colspan="3">Total Hours</th>
                </tr>
                <tr>
                    <th class="top-row">{col_1_name}</th>
                    <th class="top-row">{col_2_name}</th>
                    <th class="top-row">Regular</th>
                    <th class="top-row">Overtime</th>
                    <th class="top-row">Regular</th>
                    <th class="top-row">Overtime</th>
                    <th class="top-row">Regular</th>
                    <th class="top-row">Overtime</th>
                    <th class="top-row">Total</th>
                </tr>'''.format(
                    facility_name = facility_name, row_2_name = row_2_name, col_1_name = col_1_name, 
                    col_2_name = col_2_name
                )

    def __get_facility_employee_summary_hours(
        self, employee_name, w1_reg_hours, w1_ot_hours, w2_reg_hours, w2_ot_hours, 
        total_reg_hours, total_ot_hours, total_hours, col_2_value
    ):
        return '''
                <tr>
                    <td class="employee-name-row">{employee_name}</td>
                    <td class="col-two-value">{col_2_value}</td>
                    <td class="input-text">{w1_reg_hours}</td>
                    <td class="input-text">{w1_ot_hours}</td>
                    <td class="input-text">{w2_reg_hours}</td>
                    <td class="input-text">{w2_ot_hours}</td>
                    <td class="input-text">{total_reg_hours}</td>
                    <td class="input-text">{total_ot_hours}</td>
                    <td class="input-text">{total_hours}</td>
                </tr>'''.format(
                    col_2_value = col_2_value,
                    employee_name = employee_name, 
                    w1_reg_hours = self.__remove_decimal_if_whole(w1_reg_hours),
                    w1_ot_hours = self.__remove_decimal_if_whole(w1_ot_hours),
                    w2_reg_hours = self.__remove_decimal_if_whole(w2_reg_hours),
                    w2_ot_hours = self.__remove_decimal_if_whole(w2_ot_hours),
                    total_reg_hours = self.__remove_decimal_if_whole(total_reg_hours),
                    total_ot_hours = self.__remove_decimal_if_whole(total_ot_hours),
                    total_hours = self.__remove_decimal_if_whole(total_hours)
                )

    def __get_id(self, wtc):
        """
        Get the employee id for the given WeeklyTimeCard object.
        :param wtc: WeeklyTimeCard object
        :return: employee id
        """
        return wtc.employee.employee_id if wtc else ''

    def __get_reg_hours(self, wtc):
        """
        Get the regular hours for the given WeeklyTimeCard object.  Remove the decimal if
        the hours are a whole number.
        :param wtc: WeeklyTimeCard object
        :return: regular hours
        """
        return self.__remove_decimal_if_whole(wtc.get_regular_hours()) if wtc else 0

    def __get_ot_hours(self, wtc):
        """
        Get the overtime hours for the given WeeklyTimeCard object.  Remove the decimal if
        the hours are a whole number.
        :param wtc: WeeklyTimeCard object
        :return: regular hours
        """
        return self.__remove_decimal_if_whole(wtc.get_overtime_hours()) if wtc else 0

    @staticmethod
    def __remove_decimal_if_whole(input_num):
        """
        Remove the decimal if the input number is a whole number.
        :param input_num: input number
        :return: number
        """
        return int(input_num) if isinstance(input_num, float) and input_num.is_integer() else input_num

    def __get_total_row(
        self, w1_reg_hours, w1_ot_hours, w2_reg_hours, w2_ot_hours, total_reg_hours, 
        total_ot_hours, total_hours
    ):
        return '''
                <tr>
                    <td colspan="2" class="employee-name-row">TOTAL</td>
                    <td class="input-text">{w1_reg_hours}</td>
                    <td class="input-text">{w1_ot_hours}</td>
                    <td class="input-text">{w2_reg_hours}</td>
                    <td class="input-text">{w2_ot_hours}</td>
                    <td class="input-text">{total_reg_hours}</td>
                    <td class="input-text">{total_ot_hours}</td>
                    <td class="input-text">{total_hours}</td>
                </tr>'''.format(
                    w1_reg_hours = self.__remove_decimal_if_whole(w1_reg_hours),
                    w1_ot_hours = self.__remove_decimal_if_whole(w1_ot_hours),
                    w2_reg_hours = self.__remove_decimal_if_whole(w2_reg_hours),
                    w2_ot_hours = self.__remove_decimal_if_whole(w2_ot_hours),
                    total_reg_hours = self.__remove_decimal_if_whole(total_reg_hours),
                    total_ot_hours = self.__remove_decimal_if_whole(total_ot_hours),
                    total_hours = self.__remove_decimal_if_whole(total_hours)
                )

    @staticmethod
    def __get_style():
        return '''
            <style>
                @media print {
                    @page {
                        size: letter;
                        margin: 20mm;
                    }
                }

                body {
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                    font-size: 12px;
                    width: 760px;
                    margin: 0 auto;
                }

                #header, #footer {
                    text-align: center;
                    margin-bottom: 20px;
                }

                table {
                    border-collapse: collapse;
                    width: 100%;
                }

                th, td {
                    border: 1px solid black;
                    padding-top: 8px;
                    padding-bottom: 8px;
                    text-align: center;
                }
                
                .header-row {
                    font-size: 16px;
                    text-align: left;
                    padding-left: 10px;
                }
                
                .date-row {
                    text-align: left;
                    padding-left: 10px;
                }

                .col-two-value {
                    font-size: 11px;
                }

                .employee-name-row {
                    text-align: left;
                    padding-left: 10px;
                }

                .position-row {
                    text-align: left;
                    padding-left: 10px;
                }

                .column1 {
                    text-align: left;
                    padding-left: 10px;
                    font-weight: bold;
                }

                .input-text {
                    font-size: 11px;
                    width: 60px;
                }

                .boiler-plate {
                    padding: 10px;
                    text-align: left;
                    font-size: 10px;
                }

                #footer {
                    margin-top: 20px;
                }
            </style>'''
