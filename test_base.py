import unittest
import logging
from logger import config_log
import maya

log = logging.getLogger(__name__)
config_log(log)

class BaseTest(unittest.TestCase):
    LOG_BLANK_LINES = 5

    @staticmethod
    def space():
        for i in range(BaseTest.LOG_BLANK_LINES):
            log.info('')

    @classmethod
    def setUpClass(cls):
        BaseTest.space()
        log.info(f'RUN {maya.now()}')
        BaseTest.space()

    def setUp(self):
        BaseTest.space()
        log.info(f'{"BEGIN"*9}      {self._testMethodName}')

    def tearDown(self):
        log.info(f'{"END"*15}      {self._testMethodName}')
