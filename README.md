# Multilingual Translator

A Flask-based web application that provides translation services for both text and audio input, supporting multiple Indian languages. The application uses Google's translation services and text-to-speech capabilities to provide a complete translation experience.

## Features

- Text translation between multiple languages
- Audio file translation (WAV format)
- Text-to-speech output in the target language
- Support for multiple Indian languages including:
  - Hindi
  - Tamil
  - Telugu
  - Marathi
  - Bengali
  - Gujarati
  - Kannada
  - Malayalam
  - Punjabi
  - English

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)
- Internet connection (required for Google services)

## Installation

1. Clone the repository or download the source code.

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the Flask application:
```bash
python app.py
```

2. Open your web browser and navigate to `http://localhost:5000`

3. Choose your input method:
   - Text Input: Enter text directly in the text area
   - Audio Input: Upload a WAV format audio file

4. Select the target language from the dropdown menu

5. Click "Translate" to get the translation and audio output

## Audio Input Requirements

- Supported format: WAV
- Maximum file size: 16MB
- Clear audio quality recommended for better transcription

## Notes

- The application uses Google's services for translation and speech recognition
- Internet connection is required for all translation and speech services
- Audio files are temporarily stored and automatically deleted after processing
- For best results with audio input, use clear speech in a quiet environment

## Troubleshooting

1. If you encounter any issues with audio transcription:
   - Ensure the audio file is in WAV format
   - Check if the audio is clear and without background noise
   - Verify your internet connection

2. If translation fails:
   - Check your internet connection
   - Verify that the input text is not empty
   - Ensure the target language is properly selected

## License

This project is open source and available under the MIT License. 