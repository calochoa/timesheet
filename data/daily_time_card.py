__author__ = "Cal Ochoa"
__email__ = "CalOchoa@gmail.com"

from datetime import datetime

from time_card_increments import TimeCardIncrements


class DailyTimeCard(object):

    NORMAL_HOURS = 8
    DEFAULT_DATE_FORMAT = '%m/%d/%y'
    NO_HOURS_WORKED_STR = 'OFF'

    def __init__(self, daily_date_str, date_format=DEFAULT_DATE_FORMAT):
        self.daily_date = datetime.strptime(daily_date_str, date_format).date()
        self.in_out_hours_list = []
        self.total_daily_hours = 0

    def add_in_out_hours(self, time_card_increments_str):
        """
        Add the input time card increments string to the in/out hours list, but only retain consecutive
        blocks of time.  Also, update the total daily hours each time.  Finally, return the hours added.
        :param time_card_increments_str: time card increments string
        :return: hours added
        """
        current_tci = TimeCardIncrements(time_card_increments_str)
        hours_added = current_tci.time_diff
        self.total_daily_hours += hours_added
        if self.in_out_hours_list:
            last_tci = self.in_out_hours_list[-1]
            if last_tci.end_time == current_tci.start_time:
                self.in_out_hours_list.pop()
                update_tci_str = '{0}{1}{2}'.format(
                    last_tci.start_time_str, TimeCardIncrements.TIME_SEPARATOR, current_tci.end_time_str
                )
                current_tci = TimeCardIncrements(update_tci_str)
        self.in_out_hours_list.append(current_tci)
        return hours_added

    def has_overtime_pay(self):
        """
        Check if there is overtime pay for this daily time card by comparing the total 
        daily hours to the normal hours.
        :return: boolean status
        """
        return self.total_daily_hours > self.NORMAL_HOURS
    
    def get_overtime_hours(self):
        """
        Get the amount of overtime hours for the daily time card, if applicable.
        :return: overtime hours
        """
        return self.total_daily_hours - self.NORMAL_HOURS if self.has_overtime_pay() else 0
    
    def get_daily_hours_worked_str(self):
        """
        Get the daily hours worked string for the daily time card.
        :return: daily hours worked string
        """
        daily_hours_worked_str = self.NO_HOURS_WORKED_STR
        if self.total_daily_hours:
            daily_hours_worked_str = '{0}'.format(self.__get_valid_hours(self.total_daily_hours))
            overtime_hours = self.get_overtime_hours()
            if overtime_hours:
                daily_hours_worked_str = '{0} + {1}'.format(self.NORMAL_HOURS, self.__get_valid_hours(overtime_hours))
        return daily_hours_worked_str
    
    @staticmethod
    def __get_valid_hours(hours):
        """
        If the hours is a float and a whole number, then return the hours as an int; otherwise
        return it as is.
        :param hours: hours
        :return: valid hours
        """
        return int(hours) if isinstance(hours, float) and hours.is_integer() else hours

    def get_wtc_date(self):
        """
        Get the date in the format for the weekly time card html file.
        :return: weekly time card date
        """
        return self.daily_date.strftime(self.DEFAULT_DATE_FORMAT)

    def get_wtc_day(self):
        """
        Get the day in the format for the weekly time card html file.
        :return: weekly time card day
        """
        return self.daily_date.strftime('%A')

    def display_contents(self):
        print('***** Daily Time Card *****')
        print('Daily Date: {0} ({1})'.format(self.daily_date, self.daily_date.strftime('%A')))
        print('Total Daily Hours: {0}'.format(self.total_daily_hours))
        print('Has Daily Overtime Pay: {0}'.format(self.has_overtime_pay()))
        print('Daily Overtime Hours: {0}'.format(self.get_overtime_hours()))
        print('In Out Hours: {0}'.format([in_out_hour.get_start_end_time_str() for in_out_hour in self.in_out_hours_list]))
        print('Daily Hours Worked: {0}\n'.format(self.get_daily_hours_worked_str()))


def test_me(test_daily_date_str, in_out_hours_list, date_format=DailyTimeCard.DEFAULT_DATE_FORMAT):
    test_daily_time_card = DailyTimeCard(test_daily_date_str, date_format=date_format)
    for in_out_hours_str in in_out_hours_list:
        test_daily_time_card.add_in_out_hours(in_out_hours_str)
    test_daily_time_card.display_contents()


if __name__ == "__main__":
    print('Start Testing DailyTimeCard...\n')

    test_in_out_hours_list = [
        '10am-11am', '11am-12pm', '12pm-1pm', '2pm-3pm', '3pm-4pm', '8pm-9pm', '9pm-10pm', '10pm-11pm',
        '2am-3am', '3am-4:30am'
    ]
    test_me('09/19/22', test_in_out_hours_list)
    test_me('09/22/22', ['3pm-7:30pm', '8pm-11:45pm'])
    test_me('09-24-22', ['6am-10:15am', '12pm-3:45pm', '1am-3am'], date_format='%m-%d-%y')
    test_me('092522', [], date_format='%m%d%y')

    print('\nEnd Testing DailyTimeCard\n')
 