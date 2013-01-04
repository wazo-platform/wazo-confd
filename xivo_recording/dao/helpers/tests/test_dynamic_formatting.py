'''
Created on Jan 4, 2013

@author: jean
'''
from datetime import datetime
from xivo_recording.dao.exceptions import InvalidInputException
from xivo_recording.dao.helpers.dynamic_formatting import table_to_string, \
    table_list_to_list_dict, str_to_datetime
from xivo_recording.recording_config import RecordingConfig
import unittest


class SampleClass:
    def __init__(self, privateFoo, privateBar, foo, bar, other):
        self._privateFoo = privateFoo
        self.__privateBar = privateBar
        self.foo = foo
        self.bar = bar
        self.other = other


class TestDynamicFormatting(unittest.TestCase):

    def setUp(self):
        RecordingConfig.CSV_SEPARATOR = ';; '
    
    def test_table_to_string(self):
        instance = SampleClass("un", None, "trois", 4, None)
        expected_result = "bar: 4" + RecordingConfig.CSV_SEPARATOR + "foo: trois" + \
                RecordingConfig.CSV_SEPARATOR + "other: None"
        actual_result = table_to_string(instance)
        assert expected_result == actual_result, "Instance not properly formatted: " + actual_result + \
                    ", expected: " + expected_result

    def test_table_list_to_list_dict(self):
        table_list=[SampleClass("un", None, "trois", 4, None), SampleClass("deux", "trois", None, 5, None)] 
        expected_list_dict = [{"bar":"4", "foo":"trois", "other":""},
                              {"bar":"5", "foo":"", "other":""}]
        
        actual_result = table_list_to_list_dict(table_list)
        assert expected_list_dict == actual_result, "Got incorrect dictionary: " + str(actual_result) + \
                    ", expected: " + str(expected_list_dict)
                    
                    
    def test_str_to_datetime(self):
        strDate = "2012-01-01"
        resultDate = str_to_datetime(strDate)
        assert resultDate == datetime.strptime(strDate, "%Y-%m-%d")
        
        strTime = "2012-01-01 00:00:00"
        resultTime = str_to_datetime(strTime)
        assert resultTime == datetime.strptime(strTime, "%Y-%m-%d %H:%M:%S")
        
        invalidDateStr = "2012-13-13"
        with self.assertRaises(InvalidInputException):
            str_to_datetime(invalidDateStr)
        
        tooShortStr = '2012'
        with self.assertRaises(InvalidInputException):
            str_to_datetime(tooShortStr)
 
        invalidTimeStr = '2012-01-01 00:00:99'
        with self.assertRaises(InvalidInputException):
            str_to_datetime(invalidTimeStr)

        invalidTimeStr = None
        with self.assertRaises(InvalidInputException):
            str_to_datetime(invalidTimeStr)
            
        invalidTimeStr = {}
        with self.assertRaises(InvalidInputException):
            str_to_datetime(invalidTimeStr)
            
        invalidTimeStr = 2012
        with self.assertRaises(InvalidInputException):
            str_to_datetime(invalidTimeStr)
            
