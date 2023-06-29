__author__ = "Cal Ochoa"
__email__ = "CalOchoa@gmail.com"


class Employee(object):

    def __init__(self, employee_id, employee_name, entity_name, position='staff'):
        self.employee_id = employee_id
        self.employee_name = employee_name
        self.entity_name = entity_name
        self.position = position

    def display_contents(self):
        print('***** Employee *****')
        print('Employee ID: {0}'.format(self.employee_id))
        print('Employee Name: {0}'.format(self.employee_name))
        print('Entity Name: {0}'.format(self.entity_name))
        print('Position: {0}\n'.format(self.position))

    def __str__(self):
        return 'Employee[ID: {0}, Name: {1}, Entity: {2}, Position: {3}]'.format(
            self.employee_id, self.employee_name, self.entity_name, self.position
        )

    def __repr__(self):
        return 'Employee[ID: {0}, Name: {1}, Entity: {2}, Position: {3}]'.format(
            self.employee_id, self.employee_name, self.entity_name, self.position
        )


if __name__ == "__main__":
    print('Start Testing Employee...\n')

    test_employee = Employee('A', 'Cal', 'Cal Workouts')
    test_employee.display_contents()

    print('\nEnd Testing Employee\n')
 