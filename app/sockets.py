from app import socketio
from flask_socketio import emit, join_room, leave_room
from flask_login import current_user

@socketio.on('connect')
def handle_connect():
    if current_user.is_authenticated:
        join_room(f'user_{current_user.id}')

@socketio.on('disconnect')
def handle_disconnect():
    if current_user.is_authenticated:
        leave_room(f'user_{current_user.id}')

@socketio.on('send_message')
def handle_send_message(data):
    room = data['room']
    message = data['message']
    emit('new_message', {'message': message}, room=room)

# Add more WebSocket event handlers as needed