from pprint import pprint
from tos_import.classes.test import TestSetUp
from base.views import base_models


class TestBaseModelList(TestSetUp):
    def test_model_listing(self):
        base_models({})


