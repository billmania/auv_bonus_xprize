#
# Designed and written by:
# Bill Mania
# bill@manialabs.us
#
# under contract to:
# Valley Christian Schools
# San Jose, CA
#
# to compete in the:
# NOAA Bonus XPrize
# January 2019
#
class TestClass(object):
    def __init__(self):
        print('My test class')

        self.instance_variable = 5

    def class_func(self):
        print('Original TestClass func')
        print('var: {0}'.format(self.instance_variable))
        self.instance_variable += 1

def new_func(self, spare='BEFORE'):
    print('Brand new func {0}, {1}'.format(self.instance_variable, spare))

tc = TestClass()
tc.class_func()
TestClass.class_func = new_func

tc.class_func()
tc.class_func(spare='AFTER')
