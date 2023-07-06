__author__ = "Cal Ochoa"
__email__ = "CalOchoa@gmail.com"


class WeeklyTimeCardTemplate(object):

    DAYS_OF_WEEK = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

    def __init__(self):
        pass

    def get_populated_template1(self, weekly_time_card):
        template = self.__get_html_template()
        employee = weekly_time_card.employee
        facility_name = 'facility_name'
        daily_time_card_list = weekly_time_card.daily_time_card_list
        from_date = daily_time_card_list[0].get_wtc_date()
        to_date = daily_time_card_list[-1].get_wtc_date()
        return template.format(
            title=f'{employee.employee_name}\'s Time Card',
            style=self.__get_style(), 
            header_rows=self.__get_header_rows(
                employee.entity_name.upper(), from_date, to_date, employee.employee_name, 
                employee.position, facility_name
            ),
            hours_rows=self.__get_hours_rows(),
            entry_rows=self.__get_entry_rows(daily_time_card_list),
            footer_rows=self.__get_footer_rows(weekly_time_card.total_weekly_hours)
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
                    <th colspan="8" class="header-row">{entity_name}</th>
                </tr>
                <tr>
                    <td colspan="2" class="date-row"><b>From:</b> {from_date}</th>
                    <td colspan="5" class="date-row"><b>To:</b> {to_date}</th>
                    <th colspan="3"></th>
                </tr>
                <tr>
                    <td colspan="7" class="employee-name-row"><b>Employee Name:</b> {employee_name}</th>
                    <th colspan="3">Program</th>
                </tr>
                <tr>
                    <td colspan="7" class="position-row"><b>Position:</b> {position}</th>
                    <th colspan="3">{facility_name}</th>
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
                    <th colspan="2"></th>
                </tr>
                <tr>
                    <th rowspan="2">In</th>
                    <th rowspan="2">Out</th>
                    <th rowspan="2">In</th>
                    <th rowspan="2">Out</th>
                    <th rowspan="2">In</th>
                    <th rowspan="2">Out</th>
                    <th colspan="2">SUBTOTAL HOURS</th>
                </tr>
                <tr>
                    <th>Regular</th>
                    <th>Office Use</th>
                </tr>'''

    def __get_entry_rows(self, daily_time_card_list):
        entry_rows = ''
        for daily_time_card in daily_time_card_list:
            entry_rows += self.__get_day_row(daily_time_card)
        return entry_rows

    @staticmethod
    def __get_day_row(daily_time_card):
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
                <td></td>
            </tr>
        '''.format(
            day=day, date=date, in_out_hours_cols=in_out_hours_cols, 
            total_daily_hours=daily_time_card.total_daily_hours
        )

    @staticmethod
    def __get_footer_rows(weekly_total_hours):
        return '''
            <tr>
                <td rowspan="2" colspan="8" class="column1">EMPLOYEE SIGNATURE:</td>
                <td>{weekly_total_hours}</td>
                <td></td>
            </tr>
            <tr>
                <td>TOTAL</td>
                <td>TOTAL</td>
            </tr>
            <tr>
                <td colspan="12" class="boiler-plate">
                    *Note: No Overtime Hours will be worked without the prior approval of Administrator 
                    and/or Owner/Licenses.  The times reported accurately reflect the hours I have worked.  
                    I certify under penalty of perjury the information above is true and correct to the 
                    best of my knowledge.
                </td>
            </tr>
            <tr>
                <td colspan="12" class="column1">
                    <br/>FACILITY MANAGER SIGNATURE:<br/><br/>
                </td>
            </tr>'''.format(weekly_total_hours=weekly_total_hours)

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

                .invisible {
                    font-size: 10px;
                    color: transparent;
                }

                #footer {
                    margin-top: 20px;
                }
            </style>'''
