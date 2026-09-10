"""Prevent a refresh from silently consuming an earlier successful response."""
import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from cordon_d.acquisition import capture_public


class Response(io.BytesIO):
    status = 200
    url = 'https://publisher.example/release'
    headers = {}


class Captures(unittest.TestCase):
    def test_same_url_changed_content_requires_a_fresh_capture(self):
        with TemporaryDirectory() as directory:
            first = Path(directory)/'first'
            with patch('urllib.request.urlopen', return_value=Response(b'{"id":1,"value":"old"}')) as request:
                a = capture_public(Response.url, first, parent='source index')
                with self.assertRaises(FileExistsError):
                    capture_public(Response.url, first, parent='source index')
                self.assertEqual(request.call_count, 1)
            with patch('urllib.request.urlopen', return_value=Response(b'{"id":1,"value":"corrected"}')):
                b = capture_public(Response.url, Path(directory)/'second', parent='source index')
            self.assertNotEqual(a['sha256'], b['sha256'])
            self.assertEqual(json.loads((first/'body').read_text())['value'], 'old')

    def test_truncated_body_remains_partial_even_with_http_success(self):
        with TemporaryDirectory() as directory:
            path = Path(directory)/'capture'
            response = Response(b'partial')
            response.headers = {'Content-Length':'100'}
            with patch('urllib.request.urlopen', return_value=response):
                result = capture_public(Response.url, path, parent='source index')
            self.assertFalse(result['complete_body'])
            self.assertEqual(result['status'], 200)
            self.assertTrue((path/'body.partial').exists())
            self.assertFalse((path/'body').exists())


if __name__ == '__main__':
    unittest.main()
