from pprint import pprint
from app_pms.classes.test import TestSetUp
from base.views import base_models


class TestBaseModelList(TestSetUp):
    def test_model_listing(self):
        base_models({})


