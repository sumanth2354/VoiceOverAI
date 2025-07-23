🎬 VoiceOverAI
Multilingual Video Dubbing Web App
🎙️ Dub your videos into 40+ Indian and global languages using AI transcription, translation, and text-to-speech — all in your browser.

🌟 Features
• 🎥 Upload a video reel and transcribe the original audio using Whisper
• 🌏 Translate to 40+ languages — Hindi, Telugu, Tamil, Kannada, Bengali, Spanish, French, German, etc.
• 🗣️ Generate natural-sounding dubbed audio using TTS
• 🎬 Combine dubbed audio with video or download audio separately
• 📊 See real-time progress with an animated progress bar
• 📱 Responsive, mobile-friendly UI

🚀 Getting Started
🖥️ Prerequisites
Install these on your system:
• 🐍 Python 3.9 or newer
• 🔊 FFmpeg (must be in your system PATH)

📦 Python Packages
This app uses the following Python libraries:
• Flask
• gTTS
• translatepy
• openai-whisper
• torch
• tqdm
• numpy
• gitpython (optional, for contributors)

You can install them one by one:

-->pip install flask gtts translatepy openai-whisper torch tqdm numpy

🧪 Running the App

python app.py
Then open your browser and visit:
🔗 http://127.0.0.1:5000

📂 Folder Structure
swift

VoiceOverAI/
├── app.py
├── templates/
│   ├── index.html
│   └── progress.html
├── uploads/
├── static/outputs/
├── README.md
🛠️ Tech Stack
Languages & Frameworks:
• 🐍 Python 3.9+
• 🌐 Flask (web framework)
• 💻 HTML/CSS & JavaScript (frontend)

AI & Audio Tools:
• 🎧 OpenAI Whisper (speech-to-text)
• 🔊 Google TTS (text-to-speech)
• 🌏 TranslatePy (translation)
• 🎬 FFmpeg (media processing)

🌏 Supported Languages
🇮🇳 Major Indian Languages:
• Hindi, Telugu, Tamil, Kannada, Malayalam, Bengali, Marathi, Gujarati, Punjabi, Oriya, Assamese

🌎 Global Languages:
• English, Spanish, French, German, Italian, Chinese, Japanese, Korean, Arabic, Russian, Portuguese… and more!
