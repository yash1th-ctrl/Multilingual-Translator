import os
from flask import Flask, render_template, request, jsonify, send_file
from deep_translator import GoogleTranslator
from gtts import gTTS
import tempfile
from werkzeug.utils import secure_filename
import google.generativeai as genai

# Configure Gemini AI
GEMINI_API_KEY = "AIzaSyBYQMkvTPNB2ajlfAP44_1sSqIPP02FSDU"
genai.configure(api_key=GEMINI_API_KEY)

# Initialize Gemini model
try:
    gemini_model = genai.GenerativeModel('gemini-1.5-flash')
    GEMINI_AVAILABLE = True
    print("✅ Gemini AI initialized successfully!")
except Exception as e:
    print(f"❌ Gemini AI initialization failed: {e}")
    GEMINI_AVAILABLE = False

# Try to import speech recognition, but handle gracefully if it fails
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError as e:
    print(f"Speech recognition not available: {e}")
    SPEECH_RECOGNITION_AVAILABLE = False

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['AUDIO_FOLDER'] = 'audio_output'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create folders if they don't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['AUDIO_FOLDER'], exist_ok=True)

# Supported languages
SUPPORTED_LANGUAGES = {
    # Indian Languages
    'en': 'English',
    'hi': 'Hindi',
    'ta': 'Tamil',
    'te': 'Telugu',
    'mr': 'Marathi',
    'bn': 'Bengali',
    'gu': 'Gujarati',
    'kn': 'Kannada',
    'ml': 'Malayalam',
    'pa': 'Punjabi',
    'ur': 'Urdu',
    'or': 'Odia',
    'as': 'Assamese',

    # International Languages
    'fr': 'French',
    'es': 'Spanish',
    'de': 'German',
    'it': 'Italian',
    'pt': 'Portuguese',
    'ru': 'Russian',
    'ja': 'Japanese',
    'ko': 'Korean',
    'zh': 'Chinese (Simplified)',
    'ar': 'Arabic',
    'tr': 'Turkish',
    'nl': 'Dutch',
    'sv': 'Swedish',
    'no': 'Norwegian',
    'da': 'Danish',
    'fi': 'Finnish',
    'pl': 'Polish',
    'cs': 'Czech',
    'hu': 'Hungarian',
    'ro': 'Romanian',
    'bg': 'Bulgarian',
    'hr': 'Croatian',
    'sk': 'Slovak',
    'sl': 'Slovenian',
    'et': 'Estonian',
    'lv': 'Latvian',
    'lt': 'Lithuanian',
    'mt': 'Maltese',
    'ga': 'Irish',
    'cy': 'Welsh',
    'eu': 'Basque',
    'ca': 'Catalan',
    'gl': 'Galician',
    'th': 'Thai',
    'vi': 'Vietnamese',
    'id': 'Indonesian',
    'ms': 'Malay',
    'tl': 'Filipino',
    'sw': 'Swahili',
    'he': 'Hebrew',
    'fa': 'Persian',
    'uk': 'Ukrainian',
    'be': 'Belarusian',
    'mk': 'Macedonian',
    'sq': 'Albanian',
    'sr': 'Serbian',
    'bs': 'Bosnian',
    'me': 'Montenegrin'
}

def transcribe_audio(audio_file):
    if not SPEECH_RECOGNITION_AVAILABLE:
        return "Speech recognition not available on this system"

    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data)
            return text
        except sr.UnknownValueError:
            return "Could not understand audio"
        except sr.RequestError:
            return "Could not request results"

def translate_text_with_gemini(text, target_lang, mode="translation"):
    """Enhanced translation using Gemini AI with multiple modes"""
    if not GEMINI_AVAILABLE:
        return translate_text_fallback(text, target_lang)

    # Language mapping for better prompts
    language_names = {
        'en': 'English', 'hi': 'Hindi', 'ta': 'Tamil', 'te': 'Telugu',
        'mr': 'Marathi', 'bn': 'Bengali', 'gu': 'Gujarati', 'kn': 'Kannada',
        'ml': 'Malayalam', 'pa': 'Punjabi', 'fr': 'French', 'es': 'Spanish',
        'de': 'German', 'it': 'Italian', 'pt': 'Portuguese', 'ru': 'Russian',
        'ja': 'Japanese', 'ko': 'Korean', 'zh': 'Chinese', 'ar': 'Arabic'
    }

    target_language_name = language_names.get(target_lang, target_lang)

    try:
        if mode == "professional":
            prompt = f"""
            You are an expert professional translator and linguist. Translate the following text to {target_language_name} with the highest quality standards.

            Requirements:
            - Provide a professional, polished translation
            - Maintain formal tone and business-appropriate language
            - Ensure cultural sensitivity and appropriateness
            - Use industry-standard terminology when applicable
            - Preserve the original meaning while enhancing clarity

            Text: "{text}"

            Professional Translation:
            """
        elif mode == "conversational":
            prompt = f"""
            You are a friendly, conversational AI translator. Translate the following text to {target_language_name} in a natural, conversational style.

            Guidelines:
            - Use natural, everyday language
            - Make it sound like a native speaker would say it
            - Keep the friendly, approachable tone
            - Use colloquial expressions when appropriate

            Text: "{text}"

            Conversational Translation:
            """
        elif mode == "creative":
            prompt = f"""
            You are a creative translator specializing in literary and artistic content. Translate the following text to {target_language_name} with creative flair.

            Approach:
            - Maintain the artistic and emotional essence
            - Use creative language and expressions
            - Preserve metaphors, wordplay, and literary devices
            - Enhance the poetic or creative elements

            Text: "{text}"

            Creative Translation:
            """
        else:  # default translation mode
            prompt = f"""
            You are a professional translator. Translate the following text to {target_language_name}.

            Instructions:
            - Provide a natural, contextually appropriate translation
            - Maintain the original tone and meaning
            - If the text contains cultural references, adapt them appropriately
            - Return ONLY the translated text, no explanations

            Text: "{text}"

            Translation:
            """

        response = gemini_model.generate_content(prompt)
        translation = response.text.strip()

        # Clean up the response
        if translation.startswith('"') and translation.endswith('"'):
            translation = translation[1:-1]

        return translation

    except Exception as e:
        print(f"Gemini translation error: {e}")
        return translate_text_fallback(text, target_lang)

def translate_text_fallback(text, target_lang):
    """Fallback translation using deep-translator"""
    try:
        translator = GoogleTranslator(source='auto', target=target_lang)
        translation = translator.translate(text)
        return translation
    except Exception as e:
        return f"Translation error: {str(e)}"

def detect_language_with_gemini(text):
    """Detect the language of input text using Gemini AI"""
    if not GEMINI_AVAILABLE:
        return "auto"

    try:
        prompt = f"""
        Detect the language of the following text and return ONLY the language name in English.

        Supported languages: English, Hindi, Tamil, Telugu, Marathi, Bengali, Gujarati, Kannada, Malayalam, Punjabi

        Text: "{text}"

        Language:
        """

        response = gemini_model.generate_content(prompt)
        detected_language = response.text.strip()

        # Map language names to codes
        language_mapping = {
            'English': 'en',
            'Hindi': 'hi',
            'Tamil': 'ta',
            'Telugu': 'te',
            'Marathi': 'mr',
            'Bengali': 'bn',
            'Gujarati': 'gu',
            'Kannada': 'kn',
            'Malayalam': 'ml',
            'Punjabi': 'pa'
        }

        return language_mapping.get(detected_language, "auto")

    except Exception as e:
        print(f"Language detection error: {e}")
        return "auto"

def explain_translation_with_gemini(original_text, translated_text, source_lang, target_lang):
    """Provide detailed explanation of the translation"""
    if not GEMINI_AVAILABLE:
        return "Translation explanation not available."

    language_names = {
        'en': 'English', 'hi': 'Hindi', 'ta': 'Tamil', 'te': 'Telugu',
        'mr': 'Marathi', 'bn': 'Bengali', 'gu': 'Gujarati', 'kn': 'Kannada',
        'ml': 'Malayalam', 'pa': 'Punjabi', 'fr': 'French', 'es': 'Spanish',
        'de': 'German', 'it': 'Italian', 'pt': 'Portuguese', 'ru': 'Russian',
        'ja': 'Japanese', 'ko': 'Korean', 'zh': 'Chinese', 'ar': 'Arabic'
    }

    source_name = language_names.get(source_lang, source_lang)
    target_name = language_names.get(target_lang, target_lang)

    try:
        prompt = f"""
        You are a linguistics expert. Explain the translation from {source_name} to {target_name}.

        Original ({source_name}): "{original_text}"
        Translation ({target_name}): "{translated_text}"

        Provide a brief, educational explanation covering:
        1. Key linguistic choices made
        2. Cultural adaptations (if any)
        3. Alternative translations (if applicable)
        4. Grammar or structure differences

        Keep it concise and educational (2-3 sentences max).
        """

        response = gemini_model.generate_content(prompt)
        return response.text.strip()

    except Exception as e:
        print(f"Translation explanation error: {e}")
        return "Translation explanation not available."

def chat_with_gemini(message, context=""):
    """GPT-like conversational AI feature"""
    if not GEMINI_AVAILABLE:
        return "AI chat not available."

    try:
        prompt = f"""
        You are a helpful, professional AI assistant specializing in languages and translation.
        Respond naturally and helpfully to the user's message.

        {f"Previous context: {context}" if context else ""}

        User message: "{message}"

        Provide a helpful, conversational response:
        """

        response = gemini_model.generate_content(prompt)
        return response.text.strip()

    except Exception as e:
        print(f"Chat error: {e}")
        return "Sorry, I'm having trouble responding right now."

def translate_text(text, target_lang, mode="translation"):
    """Main translation function - uses Gemini if available, falls back to deep-translator"""
    return translate_text_with_gemini(text, target_lang, mode)

def text_to_speech(text, lang):
    try:
        tts = gTTS(text=text, lang=lang)
        # Create a unique filename
        import uuid
        filename = f"audio_{uuid.uuid4().hex[:8]}.mp3"
        filepath = os.path.join(app.config['AUDIO_FOLDER'], filename)
        tts.save(filepath)
        return filename  # Return just the filename, not the full path
    except Exception as e:
        print(f"Text-to-speech error: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html', languages=SUPPORTED_LANGUAGES, gemini_available=GEMINI_AVAILABLE)

@app.route('/detect-language', methods=['POST'])
def detect_language():
    """API endpoint for language detection"""
    text = request.json.get('text', '')
    if not text.strip():
        return jsonify({'error': 'No text provided'}), 400

    detected_lang = detect_language_with_gemini(text)
    language_names = {
        'en': 'English', 'hi': 'Hindi', 'ta': 'Tamil', 'te': 'Telugu',
        'mr': 'Marathi', 'bn': 'Bengali', 'gu': 'Gujarati', 'kn': 'Kannada',
        'ml': 'Malayalam', 'pa': 'Punjabi', 'auto': 'Auto-detect'
    }

    return jsonify({
        'detected_language_code': detected_lang,
        'detected_language_name': language_names.get(detected_lang, 'Unknown'),
        'powered_by': 'Gemini AI' if GEMINI_AVAILABLE else 'Auto-detection'
    })

@app.route('/translate', methods=['POST'])
def translate():
    if 'audio' in request.files:
        audio_file = request.files['audio']
        if audio_file.filename:
            filename = secure_filename(audio_file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            audio_file.save(filepath)
            
            # Transcribe audio to text
            text = transcribe_audio(filepath)
            os.remove(filepath)  # Clean up the audio file
        else:
            return jsonify({'error': 'No audio file provided'}), 400
    else:
        text = request.form.get('text', '')
        if not text:
            return jsonify({'error': 'No text provided'}), 400

    target_lang = request.form.get('target_lang', 'en')
    translation_mode = request.form.get('mode', 'translation')

    # Detect source language (optional, for display purposes)
    detected_lang = detect_language_with_gemini(text)

    # Translate the text with specified mode
    translated_text = translate_text(text, target_lang, translation_mode)

    # Generate explanation if requested
    explanation = ""
    if request.form.get('explain') == 'true':
        explanation = explain_translation_with_gemini(text, translated_text, detected_lang, target_lang)
    
    # Convert translated text to speech
    audio_filename = text_to_speech(translated_text, target_lang)

    response_data = {
        'original_text': text,
        'translated_text': translated_text,
        'detected_language': detected_lang,
        'target_language': target_lang,
        'translation_mode': translation_mode,
        'explanation': explanation,
        'powered_by': 'Gemini AI' if GEMINI_AVAILABLE else 'Google Translate'
    }

    # Only add audio URL if TTS was successful
    if audio_filename:
        response_data['audio_url'] = f'/audio/{audio_filename}'

    return jsonify(response_data)

@app.route('/chat', methods=['POST'])
def chat():
    """AI Chat endpoint for conversational features"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        context = data.get('context', '')

        if not message.strip():
            return jsonify({'error': 'No message provided'}), 400

        response = chat_with_gemini(message, context)

        return jsonify({
            'response': response,
            'powered_by': 'Gemini AI' if GEMINI_AVAILABLE else 'Basic Response'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/explain', methods=['POST'])
def explain():
    """Get detailed explanation of a translation"""
    try:
        data = request.get_json()
        original = data.get('original', '')
        translated = data.get('translated', '')
        source_lang = data.get('source_lang', 'auto')
        target_lang = data.get('target_lang', 'en')

        explanation = explain_translation_with_gemini(original, translated, source_lang, target_lang)

        return jsonify({
            'explanation': explanation,
            'powered_by': 'Gemini AI' if GEMINI_AVAILABLE else 'Basic Explanation'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/audio/<filename>')
def get_audio(filename):
    try:
        # Secure the filename to prevent directory traversal
        filename = secure_filename(filename)
        file_path = os.path.join(app.config['AUDIO_FOLDER'], filename)

        if os.path.exists(file_path):
            return send_file(file_path, mimetype='audio/mpeg', as_attachment=False)
        else:
            print(f"Audio file not found: {file_path}")
            return "Audio file not found", 404
    except Exception as e:
        print(f"Error serving audio file: {e}")
        return "Error serving audio file", 500

# Cleanup function for old audio files
def cleanup_old_audio_files():
    try:
        audio_folder = app.config['AUDIO_FOLDER']
        if os.path.exists(audio_folder):
            import time
            current_time = time.time()
            for filename in os.listdir(audio_folder):
                file_path = os.path.join(audio_folder, filename)
                if os.path.isfile(file_path):
                    # Remove files older than 1 hour
                    if current_time - os.path.getctime(file_path) > 3600:
                        os.remove(file_path)
                        print(f"Cleaned up old audio file: {filename}")
    except Exception as e:
        print(f"Error during cleanup: {e}")

if __name__ == '__main__':
    # Clean up old files on startup
    cleanup_old_audio_files()
    app.run(host='0.0.0.0', port=5000, debug=True)