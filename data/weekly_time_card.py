__author__ = "Cal Ochoa"
__email__ = "CalOchoa@gmail.com"

from datetime import datetime, timedelta

from daily_time_card import DailyTimeCard
from employee import Employee


class WeeklyTimeCard(object):

    DATE_SEPARATOR = '-'
    DAYS_IN_WEEK = 7
    DEFAULT_DATE_FORMAT = '%m%d%y'
    NORMAL_HOURS = 40

    DATE_FORMAT_OPTIONS = [DEFAULT_DATE_FORMAT, '%m/%d/%y', '%m/%d/%Y']

    def __init__(self, weekly_date_str, employee):
        self.date_format = self.DEFAULT_DATE_FORMAT
        start_daily_time_card = self.__validate_weekly_date_str(weekly_date_str)
        self.weekly_date_str = weekly_date_str
        self.employee = employee
        self.total_weekly_hours = 0
        self.daily_time_card_list = self.__init_daily_time_card_list(start_daily_time_card)
        self.overtime_hours = 0
        self.extra_ot_hours = None      # due to working at different facilities

    def __validate_weekly_date_str(self, weekly_date_str):
        """
        Validate the weekly date string and return the starting date.  Verify that there is a start
        and end date.  Verify the start date is a Monday, the end date is a Sunday, and that the 
        dates only span 1 week.
        :param weekly_date_str: weekly date string
        :return: start DailyTimeCard object
        """
        date_str_parts = weekly_date_str.split(self.DATE_SEPARATOR)
        if len(date_str_parts) != 2:
            raise Exception('start and end date must be separated by `{0}`'.format(self.DATE_SEPARATOR))
        start_dtc = self.__get_dtc(date_str_parts[0])
        if start_dtc.daily_date.weekday() != 0:
            raise Exception('start date must be a Monday')
        end_dtc = self.__get_dtc(date_str_parts[1])
        if end_dtc.daily_date.weekday() != 6:
            raise Exception('end date must be a Sunday')
        delta = end_dtc.daily_date - start_dtc.daily_date
        if delta.days != self.DAYS_IN_WEEK-1:
            raise Exception('weekly date string must span a single week')
        return start_dtc

    def __get_dtc(self, date_str):
        """
        Get the DailyTimeCard for the given date string.  Attempt to use
        different date format options, if necessary.
        :param date_str: date string
        :return: DailyTimeCard object
        """
        dtc = None
        for date_format in self.DATE_FORMAT_OPTIONS:
            try:
                dtc = DailyTimeCard(date_str.strip(), date_format=date_format)
                self.date_format = date_format
                break
            except Exception as e:
                pass
        return dtc
        
    def __init_daily_time_card_list(self, start_daily_time_card):
        daily_time_card_list = [start_daily_time_card]
        for idx in range(1, self.DAYS_IN_WEEK):
            next_date = start_daily_time_card.daily_date + timedelta(days=idx)
            next_date_str = next_date.strftime(self.date_format)
            daily_time_card_list.append(self.__get_dtc(next_date_str))
        return daily_time_card_list
    
    def add_time_inc(self, day_idx, time_card_increments_str):
        """
        Add the time increments for a specific day.
        :param day_idx: day index
        :param time_card_increments_str: time increments string
        """
        if day_idx >=0 and day_idx <7:
            daily_time_card = self.daily_time_card_list[day_idx]
            self.total_weekly_hours += daily_time_card.add_in_out_hours(time_card_increments_str)
        else:
            print('Day Index: `{0}` is out of bounds'.format(day_idx))

    def has_overtime_pay(self):
        """
        Check if there is overtime pay for this weekly time card by comparing the total 
        weekly hours to the normal hours.  Also, check if any of the DailyTimeCard has
        overtime pay.
        :return: boolean status
        """
        has_overtime_pay = False
        if self.total_weekly_hours > self.NORMAL_HOURS:
            has_overtime_pay = True
        else:
            for daily_time_card in self.daily_time_card_list:
                if daily_time_card.has_overtime_pay():
                    has_overtime_pay = True
                    break
        return has_overtime_pay
    
    def get_overtime_hours(self):
        """
        Get the amount of overtime hours for the weekly time card, if applicable.  
        :return: overtime hours
        """
        overtime_hours = 0
        # check if working at multiple facilities
        if self.extra_ot_hours:
            overtime_hours = self.extra_ot_hours
        else:
            # iterate over each day and accumulate the daily overtime hours
            # however, once we reach the weekly normal hours limit, add all the hours as overtime
            current_weekly_hours = 0
            weekly_overtime_enabled = False
            for daily_time_card in self.daily_time_card_list:
                total_daily_hours = daily_time_card.total_daily_hours
                if weekly_overtime_enabled:
                    if total_daily_hours:
                        daily_time_card.set_ot_hours = total_daily_hours
                        overtime_hours += total_daily_hours
                else:
                    potential_overtime_hours = (current_weekly_hours + total_daily_hours) - self.NORMAL_HOURS
                    daily_overtime_hours = daily_time_card.get_overtime_hours()
                    if potential_overtime_hours > 0:
                        weekly_overtime_enabled = True
                        overtime_hours_to_add = max(potential_overtime_hours, daily_overtime_hours)
                        daily_time_card.set_ot_hours = overtime_hours_to_add
                        overtime_hours += overtime_hours_to_add
                    elif daily_overtime_hours:
                        overtime_hours += daily_overtime_hours
                    current_weekly_hours += total_daily_hours
        return overtime_hours

    def get_regular_hours(self):
        """
        Get the regular hours for weekly time cards by subtracting the total weekly hours
        by the overtime hours.
        :return: regular hours
        """
        return self.total_weekly_hours - self.get_overtime_hours()

    def add_extra_ot_hours(self, hours):
        """
        Add the input hours to the extra overtime hours.
        :param hours: hours
        """
        if hours > 0:
            if self.extra_ot_hours is None:
                self.extra_ot_hours = hours
            else:
                self.extra_ot_hours += hours

    def display_contents(self):
        print('***** Weekly Time Card *****')
        print('Weekly Date Str: {0}'.format(self.weekly_date_str))
        print('Employee: {0}'.format(self.employee))
        print('Total Weekly Hours: {0}'.format(self.total_weekly_hours))
        print('Weekly Regular Hours: {0}'.format(self.get_regular_hours()))
        print('Weekly Overtime Hours: {0}'.format(self.get_overtime_hours()))
        print('Weekly Extra Overtime Hours: {0}'.format(self.extra_ot_hours))
        for daily_time_card in self.daily_time_card_list:
            daily_time_card.display_contents()
        print('\n')

    def __repr__(self):
        return ('WeeklyTimeCard[Date: {0}, Employee: {1}, Total Hrs: {2}, '
                'Regular Hrs: {3}, Overtime Hrs: {3}]'.format(
                    self.weekly_date_str, self.employee, self.total_weekly_hours, 
                    self.get_regular_hours(), self.get_overtime_hours()
                ))

if __name__ == "__main__":
    print('Start Testing WeeklyTimeCard...\n')

    test_employee = Employee('A', 'Cal Ochoa', 'Cal Workouts', position='CTO')
    test_wtc = WeeklyTimeCard(' 052923 - 060423 ', test_employee)
    #test_wtc.display_contents()

    test_wtc = WeeklyTimeCard('052923-060423', test_employee)
    test_wtc.display_contents()

    print('\nEnd Testing WeeklyTimeCard\n')
 