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

    def __init__(self, weekly_date_str, employee):
        start_daily_time_card = self.__validate_weekly_date_str(weekly_date_str)
        self.weekly_date_str = weekly_date_str
        self.employee = employee
        self.total_weekly_hours = 0
        self.daily_time_card_list = self.__init_daily_time_card_list(start_daily_time_card)

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
        start_dtc = DailyTimeCard(date_str_parts[0].strip(), date_format=self.DEFAULT_DATE_FORMAT)
        if start_dtc.daily_date.weekday() != 0:
            raise Exception('start date must be a Monday')
        end_dtc = DailyTimeCard(date_str_parts[1].strip(), date_format=self.DEFAULT_DATE_FORMAT)
        if end_dtc.daily_date.weekday() != 6:
            raise Exception('end date must be a Sunday')
        delta = end_dtc.daily_date - start_dtc.daily_date
        if delta.days != self.DAYS_IN_WEEK-1:
            raise Exception('weekly date string must span a single week')
        return start_dtc
        
    def __init_daily_time_card_list(self, start_daily_time_card):
        daily_time_card_list = [start_daily_time_card]
        for idx in range(1, self.DAYS_IN_WEEK):
            next_date = start_daily_time_card.daily_date + timedelta(days=idx)
            next_date_str = next_date.strftime(self.DEFAULT_DATE_FORMAT)
            daily_time_card_list.append(DailyTimeCard(next_date_str, date_format=self.DEFAULT_DATE_FORMAT))
        return daily_time_card_list
    
    # TODO: add function to add time increments for a specific day
    # 1. need to find the right day in the list first, daily_time_card
    # 2. need to call daily_time_card.add_in_out_hours(time_card_increments_str)

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
    
    # TODO: Under what other circumstances would there be even more overtime hours?
    def get_overtime_hours(self):
        """
        Get the amount of overtime hours for the weekly time card, if applicable.  
        Start by accumulating all the daily overtime hours.  Then, add any remaining hours
        that extend beyond the normal hours and that were not already accounted for in the 
        daily overttime hours.
        :return: overtime hours
        """
        overtime_hours = 0
        for daily_time_card in self.daily_time_card_list:
            overtime_hours += daily_time_card.get_overtime_hours()
        # TODO: verify the below logic...
        extra_hours = self.total_weekly_hours - self.NORMAL_HOURS - overtime_hours
        if extra_hours > 0:
            overtime_hours += extra_hours
        return overtime_hours
    
    def get_regular_hours(self):
        """
        Get the regular hours for weekly time cards by subtracting the total weekly hours
        by the overtime hours.
        :return: regular hours
        """
        return self.total_weekly_hours - self.get_overtime_hours()
    
    def display_contents(self):
        print('***** Weekly Time Card *****')
        print('Weekly Date Str: {0}'.format(self.weekly_date_str))
        print('Employee: {0}'.format(self.employee))
        print('Total Weekly Hours: {0}'.format(self.total_weekly_hours))
        print('Weekly Regular Hours: {0}'.format(self.get_regular_hours()))
        print('Weekly Overtime Hours: {0}'.format(self.get_overtime_hours()))
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
 