import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from providers import _extract_text_from_response


class ProviderResponseParsingTests(unittest.TestCase):
    def test_extract_text_from_openai_like_response(self):
        class Message:
            def __init__(self, content):
                self.content = content

        class Choice:
            def __init__(self, content):
                self.message = Message(content)

        class Response:
            def __init__(self, content):
                self.choices = [Choice(content)]

        self.assertEqual(_extract_text_from_response("openai", Response("Xin chào")), "Xin chào")

    def test_extract_text_from_gemini_like_response(self):
        class Part:
            def __init__(self, text):
                self.text = text

        class Content:
            def __init__(self, text):
                self.parts = [Part(text)]

        class Candidate:
            def __init__(self, text):
                self.content = Content(text)

        class Response:
            def __init__(self, text):
                self.candidates = [Candidate(text)]

        self.assertEqual(_extract_text_from_response("gemini", Response("Hello")), "Hello")


if __name__ == "__main__":
    unittest.main()
