import os


class TestFixture:

    FIXTURES = os.path.join(os.path.abspath(
            os.path.dirname(__file__)), 'fixtures')

    def __init__(self):
        self.sample_yaml = os.path.join(self.FIXTURES, 'test_settings.yaml')