import eventlet
eventlet.monkey_patch()
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
import flask.cli
import os
import random
import base64
from werkzeug.utils import secure_filename
import mimetypes
import sys
import shutil

# Configurazione percorsi
if hasattr(sys, '_MEIPASS'):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ROOT_DIR = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__))
REAL_AUDIO_PATH = os.path.join(ROOT_DIR, 'audio')

if not os.path.exists(REAL_AUDIO_PATH):
    embedded_audio_path = os.path.join(BASE_DIR, 'audio')
    if os.path.exists(embedded_audio_path):
        shutil.copytree(embedded_audio_path, REAL_AUDIO_PATH)
    else:
        os.makedirs(REAL_AUDIO_PATH, exist_ok=True)

# Inizializzazione app Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'gmprojectorsecret123'
app.config['UPLOAD_FOLDER'] = os.path.join(ROOT_DIR, 'uploads')
app.config['AUDIO_FOLDER'] = REAL_AUDIO_PATH

socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Variabili globali
current_state = {
    'current_image': None,
    'current_audio': None,
    'audio_playing': False
}

ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
ALLOWED_AUDIO_EXTENSIONS = {'mp3', 'wav', 'ogg', 'aac'}

# Funzioni di utilità
def allowed_file(filename, extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in extensions

def get_audio_moods():
    moods = []
    audio_path = app.config['AUDIO_FOLDER']
    if os.path.exists(audio_path):
        for item in os.listdir(audio_path):
            mood_path = os.path.join(audio_path, item)
            if os.path.isdir(mood_path):
                audio_files = [f for f in os.listdir(mood_path) 
                             if allowed_file(f, ALLOWED_AUDIO_EXTENSIONS)]
                if audio_files:
                    moods.append({
                        'name': item,
                        'count': len(audio_files)
                    })
    return moods

def get_random_audio_from_mood(mood):
    mood_path = os.path.join(app.config['AUDIO_FOLDER'], mood)
    if not os.path.exists(mood_path):
        return None
    
    audio_files = [f for f in os.listdir(mood_path) 
                   if allowed_file(f, ALLOWED_AUDIO_EXTENSIONS)]
    
    if not audio_files:
        return None
    
    selected_file = random.choice(audio_files)
    return os.path.join(mood, selected_file)

# Route principali
@app.route('/')
def backend():
    return render_template('backend.html')

@app.route('/frontend')
def frontend():
    return render_template('frontend.html')

@app.route('/get_ip')
def get_ip():
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return jsonify({"ip": ip})

# Gestione immagini
@app.route('/upload_image', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'Nessuna immagine trovata'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'Nessun file selezionato'}), 400
    
    if file and allowed_file(file.filename, ALLOWED_IMAGE_EXTENSIONS):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        current_state['current_image'] = filename
        socketio.emit('image_update', {'image': filename}, namespace='/')
        return jsonify({'success': True, 'filename': filename})
    
    return jsonify({'error': 'Formato file non supportato'}), 400

@app.route('/upload_portrait', methods=['POST'])
def upload_portrait():
    if 'file' not in request.files:
        return jsonify({'error': 'Nessun file ricevuto'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Nome file vuoto'}), 400

    if allowed_file(file.filename, ALLOWED_IMAGE_EXTENSIONS):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        socketio.emit('add_portrait', {'image': filename})
        return jsonify({'success': True, 'filename': filename})
    else:
        return jsonify({'error': 'Formato file non valido'}), 400

@app.route('/clear_last_portrait')
def clear_last_portrait():
    socketio.emit('clear_last_portrait')
    return jsonify({'success': True})

@app.route('/clear_screen')
def clear_screen():
    current_state['current_image'] = None
    socketio.emit('clear_screen', namespace='/')
    socketio.emit('clear_dice')
    return jsonify({'success': True})

# Gestione testo
@app.route('/show_text', methods=['POST'])
def show_text():
    data = request.get_json()
    text = data.get('text', '').strip()
    if not text:
        return jsonify({'error': 'Testo mancante'}), 400

    socketio.emit('show_text', {'text': text})
    return jsonify({'success': True, 'text': text})

@app.route('/clear_text')
def clear_text():
    socketio.emit('clear_text')
    return jsonify({'success': True})

# Gestione audio
@app.route('/get_moods')
def get_moods():
    moods = get_audio_moods()
    return jsonify({'moods': moods})

@app.route('/play_mood/<mood>')
def play_mood(mood):
    mood_folder = os.path.join('audio', mood)
    if not os.path.exists(mood_folder):
        return jsonify({'error': 'Mood non trovato'}), 404

    files = [f for f in os.listdir(mood_folder) if allowed_file(f, {'mp3', 'wav', 'ogg'})]
    if not files:
        return jsonify({'error': 'Nessun file audio trovato'}), 404

    filename = random.choice(files)
    socketio.emit('play_audio', {'mood': mood, 'audio': filename})
    return jsonify({'success': True, 'audio': filename})

@app.route('/stop_audio')
def stop_audio():
    current_state['audio_playing'] = False
    current_state['current_audio'] = None
    socketio.emit('stop_audio', namespace='/')
    return jsonify({'success': True})

@app.route('/upload_audio', methods=['POST'])
def upload_audio():
    if 'file' not in request.files:
        return jsonify({'error': 'Nessun file ricevuto'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Nome file vuoto'}), 400

    if allowed_file(file.filename, {'mp3', 'wav', 'ogg'}):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        socketio.emit('play_audio', {'audio': filename, 'mood': 'custom'})
        return jsonify({'success': True, 'filename': filename})
    else:
        return jsonify({'error': 'Formato audio non valido'}), 400

# Gestione file
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/audio/<path:filepath>')
def audio_file(filepath):
    directory = os.path.dirname(filepath)
    filename = os.path.basename(filepath)
    full_directory = os.path.join(app.config['AUDIO_FOLDER'], directory)
    return send_from_directory(full_directory, filename)

# Gestione canvas
@app.route('/send_canvas', methods=['POST'])
def send_canvas():
    data = request.get_json()
    image_data = data.get('image')
    if image_data:
        socketio.emit('canvas_update', {'image': image_data})
        return jsonify({'success': True})
    return jsonify({'success': False}), 400

@app.route('/clear_drawing')
def clear_drawing():
    return jsonify({'success': True})

@app.route('/hide_canvas')
def hide_canvas():
    socketio.emit('hide_canvas')
    return jsonify({'success': True})

# Gestione dadi
@app.route('/roll_dice/<die>')
def roll_dice(die):
    faces = {
        'd4': 4,
        'd6': 6,
        'd8': 8,
        'd10': 10,
        'd12': 12,
        'd20': 20
    }
    if die not in faces:
        return jsonify({"error": "Dado non valido"}), 400
    result = random.randint(1, faces[die])
    socketio.emit("show_dice", {"die": die, "result": result})
    return jsonify({"success": True, "result": result})

@app.route('/clear_dice')
def clear_dice():
    socketio.emit('clear_dice')
    return jsonify({'success': True})

# Stato e socket
@app.route('/get_status')
def get_status():
    return jsonify(current_state)

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    if current_state['current_image']:
        emit('image_update', {'image': current_state['current_image']})
    if current_state['audio_playing'] and current_state['current_audio']:
        emit('play_audio', {'audio': current_state['current_audio']})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

# Shutdown
@app.route('/shutdown')
def shutdown():
    socketio.emit('shutdown', namespace='/')
    return """
    <html>
        <body style="background:black;color:white;font-family:sans-serif;">
            <script>
                window.open('','_self').close();
                setTimeout(() => window.close(), 500);
            </script>
            <h2>🔌 Applicazione chiusa. Puoi ora chiudere la finestra del terminale.</h2>
        </body>
    </html>
    """

# Avvio applicazione
if __name__ == '__main__':
    print("=" * 50)
    print("🎲  GMProjector Server Starting...")
    print("=" * 50)
    print("Creato da Karoo da una idea di Marco Pulicati")
    print("=" * 50)
    print("📱 Backend (Control Panel): http://localhost:5000")
    print("🖥️  Frontend (Display):      http://localhost:5000/frontend")
    print("=" * 50)
    print("📁 Cartelle necessarie:")
    print(f"   • uploads/     - Per le immagini")
    print(f"   • audio/       - Per i file audio")
    print("=" * 50)

    import webbrowser
    import time

    def open_browser():
        time.sleep(1)
        webbrowser.open("http://127.0.0.1:5000")

    open_browser()
    socketio.run(app, host="0.0.0.0", port=5000)