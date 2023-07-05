__author__ = "Cal Ochoa"
__email__ = "CalOchoa@gmail.com"

from datetime import datetime


class TimeCardIncrements(object):

    TIME_SEPARATOR = '-'
    DEFAULT_TIME_FORMAT = '%I%p'
    MINUTE_TIME_FORMAT = '%I:%M%p'
    DEFAULT_INCREMENT = 3600    # 3600 seconds = 1 hour

    def __init__(self, start_end_time_str):
        time_str_parts = start_end_time_str.split(self.TIME_SEPARATOR)
        if len(time_str_parts) != 2:
            raise Exception('start and end time must be separated by `{0}`'.format(self.TIME_SEPARATOR))
        self.start_time_str = self.__clean_time_str(time_str_parts[0])
        self.end_time_str = self.__clean_time_str(time_str_parts[1])
        self.start_time = self.convert_time_str(self.start_time_str)
        self.end_time = self.convert_time_str(self.end_time_str)
        self.time_diff = self.__calculate_time_diff(self.start_time, self.end_time)

    @staticmethod
    def __clean_time_str(time_str):
        """
        Clean the input time string by removing surrounding spaces and converting letters to upper case.
        :param time_str: time string
        :return: clean time string
        """
        return time_str.upper().strip() if time_str else None

    def convert_time_str(self, time_str):
        """
        Covert the input time string into a datetime object.  Get the correct time format by 
        checking for minutes (ie `:`) in the time string.
        :param time_str: time string
        :return: datetime object
        """
        time_format = self.MINUTE_TIME_FORMAT if ':' in time_str else self.DEFAULT_TIME_FORMAT
        return datetime.strptime(time_str, time_format)
    
    def __calculate_time_diff(self, start_time, end_time):
        """
        Calculate the time difference in hours between the start and end time.
        If the start time is greater than or equal to the end time, then we need to
        add 24 hours
        :param start_time: start time
        :param end_time: end time
        :return: time difference in hours
        """
        duration = (end_time - start_time).total_seconds() / self.DEFAULT_INCREMENT
        return duration if (self.start_time <= self.end_time) else duration + 24
    
    def get_start_end_time_str(self):
        """
        Get the start and end time as a string.
        :return: start and end time as a string.
        """
        return '{0}{1}{2}'.format(self.start_time_str, self.TIME_SEPARATOR, self.end_time_str)

    def display_contents(self):
        print('***** Time Card Increments *****')
        print('Start-End Time Str: {0}'.format(self.get_start_end_time_str()))
        print('Start Time: {0}'.format(self.start_time.time()))
        print('End Time: {0}'.format(self.end_time.time()))
        print('Time Difference: {0} hours\n'.format(self.time_diff))


def test_me(test_start_end_time_str):
    test_daily_time_card_inc = TimeCardIncrements(test_start_end_time_str)
    test_daily_time_card_inc.display_contents()


if __name__ == "__main__":
    print('Start Testing TimeCardIncrements...\n')
    '''
    test_me(' 6aM - 7:15Pm ')
    test_me('6aM - 7am ')
    test_me(' 3pm-5:45pm')
    test_me('12pm-1:30pm')
    test_me('12am-1am')
    test_me('2pm-2:30pm')
    test_me('11pm-12am')
    '''
    test_me('1:25pm-4:10pm')

    print('\nEnd Testing TimeCardIncrements\n')