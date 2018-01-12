import unittest
import logging
from logger import config_log
import maya

log = logging.getLogger(__name__)
config_log(log)

class BaseTest(unittest.TestCase):
    LOG_BLANK_LINES = 2

    @staticmethod
    def space():
        for i in range(BaseTest.LOG_BLANK_LINES):
            log.debug('')

    @classmethod
    def setUpClass(cls):
        BaseTest.space()
        log.debug(f'RUN {maya.now()}')
        BaseTest.space()

    def setUp(self):
        BaseTest.space()
        log.debug(f'/{"-"*20} {self._testMethodName} {"-"*20}\\')

    def tearDown(self):
        log.debug(f'\\{"_"*20} {self._testMethodName} {"_"*20}/')
