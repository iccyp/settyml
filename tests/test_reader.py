import unittest
from unittest import mock

from settyml.settyml import Reader
from tests.test_fixture import TestFixture


class TestReader(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls._fixture = TestFixture()

    def test_should_load_yaml_from_file(self):
        with mock.patch('')
            # act
            Reader._load_settings_yaml(self._fixture.sample_yaml)
            # assert

