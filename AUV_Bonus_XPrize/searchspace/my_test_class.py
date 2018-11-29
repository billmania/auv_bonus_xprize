class MyTestClass(object):

    class_variable = int(5)

    def __init__(self):
        self.instance_variable = int(5)

    def set_func(self, new_value):
        self.instance_variable = new_value

    def get_func(self):
        return int(self.instance_variable)
