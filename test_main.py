"""Test the function wrapped in the Flask application."""

import unittest

import flask
import webtest

import main
from lib import plucode

main._USERNAME = 'username'
main._PASSWORD = 'password'

TEST_URL = '/'
"""String URL under which the function is mapped."""

class FunctionTest(unittest.TestCase):
    def setUp(self):
        # Enable Flask debugging
        main.app.debug = True

        # Wrap the WSGI application in a TestApp
        self.app = webtest.TestApp(main.app)
        self.app.authorization = ('Basic', (main._USERNAME, main._PASSWORD))

    def test_bad_authentication(self):
        """Test bad HTTP basic authentication."""
        for value in [None, ('Basic', ('foo', 'bar')),
                      ('Basic', ('foo', main._PASSWORD)),
                      ('Basic', (main._USERNAME, 'bar'))]:
            self.app.authorization = value
            response = self.app.post(TEST_URL, status=401)
            self.assertEqual(response.status_int, 401)

    def test_bad_methods(self):
        """Test incorrect request methods."""
        response = self.app.get(TEST_URL, status=405)
        self.assertEqual(response.status_int, 405)

        response = self.app.put(TEST_URL, status=405)
        self.assertEqual(response.status_int, 405)

        response = self.app.delete(TEST_URL, status=405)
        self.assertEqual(response.status_int, 405)

    def assertResponse(self, response, expected=None):
        """Test response contains a JSON response."""
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.charset, 'utf-8')
        json_response = response.json
        self.assertIn('payload', json_response)
        self.assertIn('google', json_response['payload'])
        self.assertIn('expectUserResponse', json_response['payload']['google'])
        self.assertFalse(
            json_response['payload']['google']['expectUserResponse'])
        self.assertIn('richResponse', json_response['payload']['google'])
        self.assertEqual(
            json_response['payload']['google']['richResponse']['items'][0][
                'simpleResponse']['displayText'],
            json_response['payload']['google']['richResponse']['items'][0][
                'simpleResponse']['textToSpeech'])

        if isinstance(expected, str):
            self.assertEqual(
                json_response['payload']['google']['richResponse']['items'][0][
                'simpleResponse']['textToSpeech'],
                expected)
        elif isinstance(expected, list):
            self.assertIn(
                json_response['payload']['google']['richResponse']['items'][0][
                'simpleResponse']['textToSpeech'],
                expected)

    def test_not_JSON(self):
        """Test posting a non-JSON body."""
        response = self.app.post(TEST_URL, '')
        self.assertResponse(response, main._FALLBACKS)
        response = self.app.post_json(TEST_URL, [])
        self.assertResponse(response, main._FALLBACKS)
        response = self.app.post_json(TEST_URL, {'queryResult': []})
        self.assertResponse(response, main._FALLBACKS)
        response = self.app.post_json(
            TEST_URL, {'queryResult': {'parameters': []}})
        self.assertResponse(response, main._FALLBACKS)
        response = self.app.post_json(
            TEST_URL, {'queryResult': {'parameters': {'foo': 'bar'}}})
        self.assertResponse(response, main._FALLBACKS)
        response = self.app.post_json(
            TEST_URL, {'queryResult': {'parameters': {'description': ''}}})
        self.assertResponse(response, main._FALLBACKS)

    def test_number(self):
        """Test a request with a numeric PLU code."""
        for code in plucode._PLU_MAP:
            for value in [code, '9' + code]:
                data = {'queryResult': {'parameters': {'number': value}}}
                response = self.app.post_json(TEST_URL, data)
                self.assertResponse(response, plucode.get_description(value))

    def test_description(self):
        """Test a request with a description."""
        for code, description in plucode._PLU_MAP.items():
            data = {'queryResult': {'parameters': {
                'description': description
            }}}
            response = self.app.post_json(TEST_URL, data)
            if code == '4055':
                self.assertResponse(response, main._TOO_MANY)
            else:
                self.assertResponse(response)
                self.assertIn(code, response.json['payload']['google'][
                    'richResponse']['items'][0]['simpleResponse'][
                        'textToSpeech'])

    def test_not_found(self):
        """Test a request that is not found."""
        for value in ['foobar', 'foo bar', 'foo bar baz']:
            response = self.app.post_json(
                TEST_URL,
                {'queryResult': {'parameters': {'description': value}}})
            self.assertResponse(response, main._NOT_FOUND)

    def test_too_many(self):
        """Test a request with too many matches."""
        for value in ['apples', 'ORANGES', 'Grapes', 'pEARS',
                      'tangerines mandarins']:
            response = self.app.post_json(
                TEST_URL,
                {'queryResult': {'parameters': {'description': value}}})
            self.assertResponse(response, main._TOO_MANY)

if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(FunctionTest)
    unittest.TextTestRunner(verbosity=2).run(suite)
