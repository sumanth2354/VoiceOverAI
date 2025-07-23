import os
import uuid
import subprocess
from flask import Flask, render_template, request, jsonify, send_from_directory
from gtts import gTTS
from translatepy import Translator
import whisper
import wave
import contextlib
from threading import Thread

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'static/outputs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

jobs = {}  # to store progress of each job

language_map = {
    'english': 'English',
    'hindi': 'Hindi',
    'telugu': 'Telugu',
    'tamil': 'Tamil',
    'bengali': 'Bengali',
    'marathi': 'Marathi',
    'punjabi': 'Punjabi',
    'gujarati': 'Gujarati',
    'kannada': 'Kannada',
    'malayalam': 'Malayalam',
    'oriya': 'Oriya',
    'assamese': 'Assamese',
    'urdu': 'Urdu',
    'french': 'French',
    'spanish': 'Spanish',
    'german': 'German',
    'italian': 'Italian',
    'portuguese': 'Portuguese',
    'russian': 'Russian',
    'chinese': 'Chinese',
    'japanese': 'Japanese',
    'korean': 'Korean',
    'arabic': 'Arabic',
    'turkish': 'Turkish',
    'thai': 'Thai',
    'vietnamese': 'Vietnamese',
    'indonesian': 'Indonesian',
    'swedish': 'Swedish',
    'dutch': 'Dutch',
    'polish': 'Polish',
    'greek': 'Greek',
    'hebrew': 'Hebrew',
    'czech': 'Czech',
    'romanian': 'Romanian',
    'hungarian': 'Hungarian',
    'danish': 'Danish',
    'finnish': 'Finnish',
    'norwegian': 'Norwegian'
}

lang_code_map = {
    'english': 'en', 'hindi': 'hi', 'telugu': 'te', 'tamil': 'ta',
    'bengali': 'bn', 'marathi': 'mr', 'punjabi': 'pa', 'gujarati': 'gu',
    'kannada': 'kn', 'malayalam': 'ml', 'oriya': 'or', 'assamese': 'as',
    'urdu': 'ur', 'french': 'fr', 'spanish': 'es', 'german': 'de',
    'italian': 'it', 'portuguese': 'pt', 'russian': 'ru', 'chinese': 'zh',
    'japanese': 'ja', 'korean': 'ko', 'arabic': 'ar', 'turkish': 'tr',
    'thai': 'th', 'vietnamese': 'vi', 'indonesian': 'id', 'swedish': 'sv',
    'dutch': 'nl', 'polish': 'pl', 'greek': 'el', 'hebrew': 'he',
    'czech': 'cs', 'romanian': 'ro', 'hungarian': 'hu', 'danish': 'da',
    'finnish': 'fi', 'norwegian': 'no'
}


def get_audio_duration(filepath):
    with contextlib.closing(wave.open(filepath, 'rb')) as wf:
        frames = wf.getnframes()
        rate = wf.getframerate()
        return frames / float(rate)


def get_video_duration(filepath):
    result = subprocess.run(
        ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
         '-of', 'default=noprint_wrappers=1:nokey=1', filepath],
        stdout=subprocess.PIPE
    )
    return float(result.stdout)


def match_audio_to_video(input_audio, output_audio, audio_duration, video_duration):
    speed_factor = audio_duration / video_duration
    atempo = speed_factor
    filters = []
    while atempo > 2.0:
        filters.append("atempo=2.0")
        atempo /= 2.0
    while atempo < 0.5:
        filters.append("atempo=0.5")
        atempo /= 0.5
    filters.append(f"atempo={atempo:.6f}")
    filter_str = ",".join(filters)
    subprocess.run([
        'ffmpeg', '-y', '-i', input_audio,
        '-filter:a', filter_str,
        output_audio
    ], check=True)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['reel']
        if file.filename == '':
            return 'No file selected!'
        lang = request.form.get('language')
        if not lang:
            return 'No language selected!'

        job_id = str(uuid.uuid4())
        jobs[job_id] = {'progress': 0, 'status': 'Queued…'}

        input_video = os.path.join(UPLOAD_FOLDER, f"{job_id}.mp4")
        file.save(input_video)

        Thread(target=process_job, args=(job_id, input_video, lang)).start()

        return render_template('progress.html', job_id=job_id)

    return render_template('index.html', language_map=language_map)


@app.route('/status/<job_id>')
def job_status(job_id):
    return jsonify(jobs[job_id])


def process_job(job_id, input_video, lang):
    jobs[job_id]['status'] = 'Extracting audio…'
    jobs[job_id]['progress'] = 10

    audio_wav = os.path.join(UPLOAD_FOLDER, f"{job_id}.wav")
    subprocess.run(['ffmpeg', '-y', '-i', input_video, '-q:a', '0', '-map', 'a', audio_wav])

    video_duration = get_video_duration(input_video)

    jobs[job_id]['status'] = 'Transcribing…'
    jobs[job_id]['progress'] = 30
    model = whisper.load_model("base")
    result = model.transcribe(audio_wav)
    text = result['text']

    jobs[job_id]['status'] = 'Translating…'
    jobs[job_id]['progress'] = 50
    translator = Translator()
    translated_text = translator.translate(text, language_map[lang]).result

    jobs[job_id]['status'] = 'Synthesizing speech…'
    jobs[job_id]['progress'] = 65
    tts = gTTS(translated_text, lang=lang_code_map[lang])
    tts_audio_mp3 = os.path.join(UPLOAD_FOLDER, f"{job_id}_{lang}.mp3")
    tts_audio_wav = os.path.join(UPLOAD_FOLDER, f"{job_id}_{lang}.wav")
    tts.save(tts_audio_mp3)
    subprocess.run(['ffmpeg', '-y', '-i', tts_audio_mp3, tts_audio_wav])

    jobs[job_id]['status'] = 'Adjusting audio speed…'
    jobs[job_id]['progress'] = 80
    adjusted_audio = os.path.join(UPLOAD_FOLDER, f"{job_id}_{lang}_adjusted.wav")
    tts_duration = get_audio_duration(tts_audio_wav)
    match_audio_to_video(tts_audio_wav, adjusted_audio, tts_duration, video_duration)

    jobs[job_id]['status'] = 'Merging audio & video…'
    jobs[job_id]['progress'] = 90
    output_video = os.path.join(OUTPUT_FOLDER, f"{job_id}_{lang}.mp4")
    subprocess.run([
        'ffmpeg', '-y', '-i', input_video, '-i', adjusted_audio,
        '-map', '0:v:0', '-map', '1:a:0', '-c:v', 'copy', '-c:a', 'aac',
        '-shortest', output_video
    ])

    jobs[job_id]['status'] = 'Done!'
    jobs[job_id]['progress'] = 100
    jobs[job_id]['video_url'] = f"/static/outputs/{job_id}_{lang}.mp4"


@app.route('/download/<path:filename>')
def download(filename):
    return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
