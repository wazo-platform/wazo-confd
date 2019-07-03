from hamcrest import ( 
    assert_that,
    is_ 
)
import unittest

def validate_extension_range(extensionRange):
    return extensionRange.start < extensionRange.end

class TestContextNotifier(unittest.TestCase):

    def test_start_cant_be_higher_than_end(self):
        extensionRange = {'start': 10, 'end': 5}
        
        validation = validate_extension_range(extensionRange)

        assert_that(validation, is_(False))

    def test_start_can_be_equal_to_end(self):
        extensionRange = {'start': 0, 'end': 0}

        validation = validate_extension_range(extensionRange)

        assert_that(validation, is_(True))

    def test_start_can_be_lower_than_end(self):
        extensionRange = {'start': 5, 'end': 10}

        validation = validate_extension_range(extensionRange)

        assert_that(validation, is_(True))