__author__ = "Cal Ochoa"
__email__ = "CalOchoa@gmail.com"


class PayPeriod(object):

    def __init__(self, employee_name, facility_name):
        self.employee_name = employee_name
        self.facility_name = facility_name
        self.weekly_time_card_1 = None
        self.weekly_time_card_2 = None

    @classmethod
    def get_summary_hours(cls, wtc_1, wtc_2):
        """
        Get the summary hours for the weekly 1 time card and weekly 2 time card.  More specifically, 
        return the week 1 regular hours, week 1 overtime hours, week 2 regular hours, week 2 overtime hours, 
        total regular hours, total overtime hours, and total hours.
        :param wtc_1: week 1 WeeklyTimeCard object
        :param wtc_2: week 2 WeeklyTimeCard object
        :return: summary hours
        """
        w1_reg_hours = cls.__get_reg_hours(cls, wtc_1)
        w1_ot_hours = cls.__get_ot_hours(cls, wtc_1)
        w2_reg_hours = cls.__get_reg_hours(cls, wtc_2)
        w2_ot_hours = cls.__get_ot_hours(cls, wtc_2)
        total_reg_hours = w1_reg_hours + w2_reg_hours
        total_ot_hours = w1_ot_hours + w2_ot_hours
        total_hours = total_reg_hours + total_ot_hours
        return w1_reg_hours, w1_ot_hours, w2_reg_hours, w2_ot_hours, total_reg_hours, total_ot_hours, total_hours

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

    def display_contents(self):
        print('***** Pay Period *****')
        print('Employee Name: {0}'.format(self.employee_name))
        print('Facility Name: {0}'.format(self.facility_name))
        print('Has Weekly Time Card 1: {0}'.format(bool(self.weekly_time_card_1)))
        print('Has Weekly Time Card 2: {0}'.format(bool(self.weekly_time_card_2)))


if __name__ == "__main__":
    print('Start Testing Pay Period...\n')

    test_pay_period = PayPeriod('Cal', 'Cal Workouts')
    test_pay_period.weekly_time_card_1 = 'yay'
    test_pay_period.weekly_time_card_2 = None
    test_pay_period.display_contents()

    print('\nEnd Testing Pay Period\n')
 