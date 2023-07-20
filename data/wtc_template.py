__author__ = "Cal Ochoa"
__email__ = "CalOchoa@gmail.com"


class WeeklyTimeCardTemplate(object):

    DAYS_OF_WEEK = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

    def __init__(self):
        pass

    # TODO: add docstrings/comments for all these functions...
    def get_populated_template(self, weekly_time_card):
        template = self.__get_html_template()
        employee = weekly_time_card.employee
        daily_time_card_list = weekly_time_card.daily_time_card_list
        from_date = daily_time_card_list[0].get_wtc_date()
        to_date = daily_time_card_list[-1].get_wtc_date()
        return template.format(
            title=f'{employee.employee_name}\'s Time Card',
            style=self.__get_style(), 
            header_rows=self.__get_header_rows(
                employee.entity_name.upper(), from_date, to_date, employee.employee_name, 
                employee.position, employee.facility_name.upper()
            ),
            hours_rows=self.__get_hours_rows(),
            entry_rows=self.__get_entry_rows(weekly_time_card),
            footer_rows=self.__get_footer_rows(weekly_time_card)
        )

    @staticmethod
    def __get_html_template():
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>{title}</title>{style}
        </head>
        <body>
            <div id="header"></div>
            <table>{header_rows}{hours_rows}{entry_rows}{footer_rows}
            </table>
            <div id="footer"></div>
        </body>
        </html>
        '''

    @staticmethod
    def __get_header_rows(
        entity_name, from_date, to_date, employee_name, position, facility_name
    ):
        return '''
                <tr>
                    <th colspan="2" class="header-row">WEEKLY TIME CARD</th>
                    <th colspan="12" class="header-row">{entity_name}</th>
                </tr>
                <tr>
                    <td colspan="2" class="date-row"><b>From:</b> {from_date}</th>
                    <td colspan="4" class="date-row"><b>To:</b> {to_date}</th>
                    <th colspan="5"></th>
                </tr>
                <tr>
                    <td colspan="6" class="employee-name-row"><b>Employee Name:</b> {employee_name}</th>
                    <th colspan="5">Program</th>
                </tr>
                <tr>
                    <td colspan="6" class="position-row"><b>Position:</b> {position}</th>
                    <th colspan="5">{facility_name}</th>
                </tr>'''.format(
                    entity_name=entity_name, from_date=from_date, to_date=to_date,
                    employee_name=employee_name, position=position, facility_name=facility_name
                )

    @staticmethod
    def __get_hours_rows():
        return '''
                <tr>
                    <th rowspan="3"></th>
                    <th rowspan="3">DATES</th>
                    <th colspan="6">HOURS</th>
                    <th colspan="3"></th>
                </tr>
                <tr>
                    <th rowspan="2">In</th>
                    <th rowspan="2">Out</th>
                    <th rowspan="2">In</th>
                    <th rowspan="2">Out</th>
                    <th rowspan="2">In</th>
                    <th rowspan="2">Out</th>
                    <th colspan="3">SUBTOTAL HOURS</th>
                </tr>
                <tr>
                    <th class="input-text">Total</th>
                    <th class="input-text">Regular</th>
                    <th class="input-text">Overtime</th>
                </tr>'''

    def __get_entry_rows(self, weekly_time_card):
        has_weekly_overtime_pay = weekly_time_card.has_overtime_pay()
        entry_rows = ''
        current_total_regular_hours = 0
        for daily_time_card in weekly_time_card.daily_time_card_list:
            total_daily_hours = daily_time_card.total_daily_hours
            total_overtime_hours = daily_time_card.get_overtime_hours()
            total_regular_hours = daily_time_card.NORMAL_HOURS if total_overtime_hours else total_daily_hours
            if has_weekly_overtime_pay and (current_total_regular_hours + total_regular_hours) > weekly_time_card.NORMAL_HOURS:
                remaining_regular_hours = weekly_time_card.NORMAL_HOURS - current_total_regular_hours
                total_overtime_hours += (total_regular_hours - remaining_regular_hours)
                total_regular_hours = remaining_regular_hours
            else:
                current_total_regular_hours += total_regular_hours
            entry_rows += self.__get_day_row(
                daily_time_card, total_daily_hours, total_regular_hours, total_overtime_hours
            )
        return entry_rows

    def __get_day_row(self, daily_time_card, total_daily_hours, total_regular_hours, total_overtime_hours):
        day = daily_time_card.get_wtc_day()
        date = daily_time_card.get_wtc_date()
        in_out_hours_cols = ''
        for in_out_hours in daily_time_card.in_out_hours_list:
            in_out_hours_cols += '''
                <td class="input-text">{start_time}</td>
                <td class="input-text">{end_time}</td>'''.format(
                    start_time=in_out_hours.start_time_str,
                    end_time=in_out_hours.end_time_str
                )
        blank_in_out_hours = 3 - len(daily_time_card.in_out_hours_list)
        if blank_in_out_hours > 0:
            for idx in range(blank_in_out_hours):
                in_out_hours_cols += '''
                <td class="input-text"></td>
                <td class="input-text"></td>'''
        return '''
            <tr>
                <td class="column1">{day}</td>
                <td class="input-text">{date}</td>{in_out_hours_cols}
                <td>{total_daily_hours}</td>
                <td>{total_regular_hours}</td>
                <td>{total_overtime_hours}</td>
            </tr>
        '''.format(
            day=day, date=date, in_out_hours_cols=in_out_hours_cols, 
            total_daily_hours=self.__remove_decimal_if_whole(total_daily_hours), 
            total_regular_hours=self.__remove_decimal_if_whole(total_regular_hours) if total_regular_hours else '', 
            total_overtime_hours=self.__remove_decimal_if_whole(total_overtime_hours) if total_overtime_hours else ''
        )

    @staticmethod
    def __remove_decimal_if_whole(input_num):
        return int(input_num) if isinstance(input_num, float) and input_num.is_integer() else input_num

    def __get_footer_rows(self, weekly_time_card):
        return '''
            <tr>
                <td rowspan="2" colspan="8" class="column1">EMPLOYEE SIGNATURE:</td>
                <th colspan="3">TOTAL HOURS</th>
            </tr>
            <tr>
                <td>{weekly_total_hours}</td>
                <td>{weekly_regular_hours}</td>
                <td>{weekly_overtime_hours}</td>
            </tr>
            <tr>
                <td colspan="14" class="boiler-plate">
                    *Note: No Overtime Hours will be worked without the prior approval of Administrator 
                    and/or Owner/Licenses.  The times reported accurately reflect the hours I have worked.  
                    I certify under penalty of perjury the information above is true and correct to the 
                    best of my knowledge.
                </td>
            </tr>
            <tr>
                <td colspan="14" class="column1">
                    <br/>FACILITY MANAGER SIGNATURE:<br/><br/>
                </td>
            </tr>'''.format(
                weekly_total_hours=self.__get_display_hours(weekly_time_card.total_weekly_hours), 
                weekly_regular_hours=self.__get_display_hours(weekly_time_card.get_regular_hours()),
                weekly_overtime_hours=self.__get_display_hours(weekly_time_card.get_overtime_hours())
            )

    def __get_display_hours(self, hours):
        return self.__remove_decimal_if_whole(hours) if hours else ''

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
