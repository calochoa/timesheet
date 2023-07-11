__author__ = "Cal Ochoa"
__email__ = "CalOchoa@gmail.com"


class Employee(object):

    def __init__(self, employee_id, employee_name, entity_facility_name, position='DSP'):
        self.employee_id = employee_id
        self.employee_name = employee_name
        self.entity_name, self.facility_name = self.split_entity_facility_name(entity_facility_name)
        self.position = position

    # TODO: add comments
    def split_entity_facility_name(self, entity_facility_name):
        entity_name = entity_facility_name
        facility_name = 'facility_name'
        entity_facility_name_parts = entity_facility_name.split('dba')
        if len(entity_facility_name_parts) == 2:
            entity_name = entity_facility_name_parts[0].strip()
            facility_name = entity_facility_name_parts[1].strip()
        return entity_name, facility_name

    def display_contents(self):
        print('***** Employee *****')
        print('Employee ID: {0}'.format(self.employee_id))
        print('Employee Name: {0}'.format(self.employee_name))
        print('Entity Name: {0}'.format(self.entity_name))
        print('Facility Name: {0}'.format(self.facility_name))
        print('Position: {0}\n'.format(self.position))

    def __str__(self):
        return 'Employee[ID: {0}, Name: {1}, Entity: {2}, Facility: {3}, Position: {4}]'.format(
            self.employee_id, self.employee_name, self.entity_name, self.facility_name, self.position
        )

    def __repr__(self):
        return 'Employee[ID: {0}, Name: {1}, Entity: {2}, Facility: {3}, Position: {4}]'.format(
            self.employee_id, self.employee_name, self.entity_name, self.facility_name, self.position
        )


if __name__ == "__main__":
    print('Start Testing Employee...\n')

    test_employee = Employee('A', 'Cal', 'Cal Workouts dba Taconic')
    test_employee.display_contents()

    print('\nEnd Testing Employee\n')
 