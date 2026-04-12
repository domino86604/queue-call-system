import eventlet
eventlet.monkey_patch()

import os
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'queue-system-secret-2024')
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# 현재 대기번호 목록 (최대 30개)
queue = []
MAX_QUEUE = 30

@app.route('/')
def index():
    return render_template('control.html')

@app.route('/display')
def display():
    return render_template('display.html')

@socketio.on('connect')
def on_connect():
    emit('queue_update', {'queue': queue})

@socketio.on('add_number')
def on_add_number(data):
    number = str(data.get('number', '')).strip()
    if len(number) == 4 and number.isdigit():
        if len(queue) < MAX_QUEUE and number not in queue:
            queue.append(number)
            socketio.emit('queue_update', {'queue': queue})

@socketio.on('remove_number')
def on_remove_number(data):
    number = str(data.get('number', '')).strip()
    if number in queue:
        queue.remove(number)
        socketio.emit('queue_update', {'queue': queue})

@socketio.on('clear_all')
def on_clear_all():
    queue.clear()
    socketio.emit('queue_update', {'queue': queue})

@socketio.on('test_sound')
def on_test_sound(data):
    socketio.emit('play_test_sound', data)

if __name__ == '__main__':
    import socket
    try:
        local_ip = socket.gethostbyname(socket.gethostname())
    except:
        local_ip = '127.0.0.1'
    port = int(os.environ.get('PORT', 8080))
    print(f"\n{'='*50}")
    print(f"  대기번호 호출 시스템 서버 시작!")
    print(f"{'='*50}")
    print(f"  아이패드 (컨트롤):  http://{local_ip}:{port}")
    print(f"  TV 화면   (출력):   http://{local_ip}:{port}/display")
    print(f"{'='*50}\n")
    socketio.run(app, host='0.0.0.0', port=port, debug=False)
