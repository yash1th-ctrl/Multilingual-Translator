"""
Comprehensive test suite for the Multilingual Translator application.
Tests all major functionality including text translation, audio processing, and API endpoints.
"""

import unittest
import json
import tempfile
import os
import sys
from unittest.mock import patch, MagicMock
import io

# Add the parent directory to the path to import the app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, translate_text_with_gemini, detect_language_with_gemini, text_to_speech

class TestTranslatorApp(unittest.TestCase):
    """Test cases for the main Flask application"""

    def setUp(self):
        """Set up test client and test data"""
        self.app = app.test_client()
        self.app.testing = True

        # Test data
        self.test_text = "Hello, how are you?"
        self.test_translation = "Hola, ¿cómo estás?"
        self.target_lang = "es"

    def test_index_route(self):
        """Test the main index route"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'TranslatePro Enterprise', response.data)
        self.assertIn(b'Multilingual Translator', response.data)

    def test_text_translation_endpoint(self):
        """Test text translation via POST request"""
        data = {
            'text': self.test_text,
            'target_lang': self.target_lang,
            'mode': 'translation'
        }

        response = self.app.post('/translate', data=data)
        self.assertEqual(response.status_code, 200)

        json_data = json.loads(response.data)
        self.assertIn('original_text', json_data)
        self.assertIn('translated_text', json_data)
        self.assertIn('target_language', json_data)
        self.assertEqual(json_data['original_text'], self.test_text)
        self.assertEqual(json_data['target_language'], self.target_lang)

    def test_language_detection_endpoint(self):
        """Test language detection API"""
        data = {'text': self.test_text}

        response = self.app.post('/detect-language',
                               data=json.dumps(data),
                               content_type='application/json')
        self.assertEqual(response.status_code, 200)

        json_data = json.loads(response.data)
        self.assertIn('detected_language_code', json_data)
        self.assertIn('detected_language_name', json_data)

    def test_chat_endpoint(self):
        """Test AI chat functionality"""
        data = {
            'message': 'How do I translate "hello" to Spanish?',
            'context': ''
        }

        response = self.app.post('/chat',
                               data=json.dumps(data),
                               content_type='application/json')
        self.assertEqual(response.status_code, 200)

        json_data = json.loads(response.data)
        self.assertIn('response', json_data)
        self.assertIn('powered_by', json_data)

    def test_explain_endpoint(self):
        """Test translation explanation functionality"""
        data = {
            'original': self.test_text,
            'translated': self.test_translation,
            'source_lang': 'en',
            'target_lang': self.target_lang
        }

        response = self.app.post('/explain',
                               data=json.dumps(data),
                               content_type='application/json')
        self.assertEqual(response.status_code, 200)

        json_data = json.loads(response.data)
        self.assertIn('explanation', json_data)

    def test_audio_validation_endpoint(self):
        """Test audio file validation"""
        # Create a mock audio file
        audio_data = b'fake audio data'

        data = {
            'audio': (io.BytesIO(audio_data), 'test.wav')
        }

        response = self.app.post('/validate-audio', data=data)
        # This might fail due to invalid audio format, but should not crash
        self.assertIn(response.status_code, [200, 400])

    def test_missing_text_error(self):
        """Test error handling for missing text"""
        data = {'target_lang': self.target_lang}

        response = self.app.post('/translate', data=data)
        self.assertEqual(response.status_code, 400)

        json_data = json.loads(response.data)
        self.assertIn('error', json_data)

    def test_invalid_language_detection(self):
        """Test language detection with empty text"""
        data = {'text': ''}

        response = self.app.post('/detect-language',
                               data=json.dumps(data),
                               content_type='application/json')
        self.assertEqual(response.status_code, 400)


class TestTranslationFunctions(unittest.TestCase):
    """Test cases for translation utility functions"""

    def setUp(self):
        """Set up test data"""
        self.test_text = "Hello world"
        self.target_lang = "es"

    @patch('app.GEMINI_AVAILABLE', True)
    @patch('app.gemini_model')
    def test_gemini_translation(self, mock_model):
        """Test Gemini AI translation function"""
        # Mock Gemini response
        mock_response = MagicMock()
        mock_response.text = "Hola mundo"
        mock_model.generate_content.return_value = mock_response

        result = translate_text_with_gemini(self.test_text, self.target_lang)
        self.assertEqual(result, "Hola mundo")
        mock_model.generate_content.assert_called_once()

    @patch('app.GEMINI_AVAILABLE', True)
    @patch('app.gemini_model')
    def test_language_detection(self, mock_model):
        """Test language detection function"""
        # Mock Gemini response
        mock_response = MagicMock()
        mock_response.text = "English"
        mock_model.generate_content.return_value = mock_response

        result = detect_language_with_gemini(self.test_text)
        self.assertEqual(result, "en")
        mock_model.generate_content.assert_called_once()

    @patch('app.gTTS')
    def test_text_to_speech(self, mock_gtts):
        """Test text-to-speech functionality"""
        # Mock gTTS
        mock_tts_instance = MagicMock()
        mock_gtts.return_value = mock_tts_instance

        result = text_to_speech(self.test_text, "en")

        # Should return a filename
        self.assertIsNotNone(result)
        self.assertTrue(result.endswith('.mp3'))
        mock_gtts.assert_called_once_with(text=self.test_text, lang="en")
        mock_tts_instance.save.assert_called_once()


class TestAudioProcessing(unittest.TestCase):
    """Test cases for audio processing functionality"""

    def setUp(self):
        """Set up test client"""
        self.app = app.test_client()
        self.app.testing = True

    def test_audio_translate_no_file(self):
        """Test audio translation with no file"""
        response = self.app.post('/audio-translate')
        self.assertEqual(response.status_code, 400)

        json_data = json.loads(response.data)
        self.assertIn('error', json_data)

    def test_voice_record_no_data(self):
        """Test voice recording with no data"""
        response = self.app.post('/voice-record',
                               data=json.dumps({}),
                               content_type='application/json')
        self.assertEqual(response.status_code, 400)

        json_data = json.loads(response.data)
        self.assertIn('error', json_data)


class TestErrorHandling(unittest.TestCase):
    """Test cases for error handling and edge cases"""

    def setUp(self):
        """Set up test client"""
        self.app = app.test_client()
        self.app.testing = True

    def test_invalid_route(self):
        """Test accessing invalid route"""
        response = self.app.get('/invalid-route')
        self.assertEqual(response.status_code, 404)

    def test_invalid_method(self):
        """Test using invalid HTTP method"""
        response = self.app.get('/translate')
        self.assertEqual(response.status_code, 405)

    def test_malformed_json(self):
        """Test sending malformed JSON"""
        response = self.app.post('/chat',
                               data='invalid json',
                               content_type='application/json')
        self.assertEqual(response.status_code, 400)


if __name__ == '__main__':
    # Create test suite
    test_suite = unittest.TestSuite()

    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestTranslatorApp))
    test_suite.addTest(unittest.makeSuite(TestTranslationFunctions))
    test_suite.addTest(unittest.makeSuite(TestAudioProcessing))
    test_suite.addTest(unittest.makeSuite(TestErrorHandling))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # Print summary
    print(f"\n{'='*50}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print(f"{'='*50}")