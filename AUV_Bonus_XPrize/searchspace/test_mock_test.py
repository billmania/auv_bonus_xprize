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
def test_monkeypatch(monkeypatch):
    def new_set_func(self, new_value):
        self.instance_variable = new_value * 2

    from searchspace.my_test_class import MyTestClass
    tc = MyTestClass()

    # replace a class method
    monkeypatch.setattr(MyTestClass, 'set_func', new_set_func)

    tc.set_func(4)
    assert tc.instance_variable == (4 * 2)

    # assign a value to an instance variable
    monkeypatch.setattr(tc, 'instance_variable', 15)
    assert tc.instance_variable == 15

    # assign a value to a class variable
    monkeypatch.setattr(MyTestClass, 'class_variable', 14)
    assert MyTestClass.class_variable == 14


def test_mocker(mocker):
    from searchspace.my_test_class import MyTestClass
    tc = MyTestClass()

    assert tc.get_func() == 5
    # set a return value
    mocker.patch.object(tc, 'get_func', return_value=6)
    assert tc.get_func() == 6
