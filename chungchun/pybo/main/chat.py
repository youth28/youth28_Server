from flask_socketio import emit, join_room, leave_room, send
from .. import socket
from pybo import config
import pymysql


@socket.on('connect user')
def connect(user):
    print(user)
    user_id = user['user_id']
    room_id = user['room_id']
    print(user_id, room_id)
    emit("connect user", room=room_id, user_id=user_id)


@socket.on('chat message')
def chat(data):
    print(data)
    conn = config.get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    room_id = data['room_id']
    user_id = data['user_id']
    message = data['msg']
    img = data['profile_image']
    datetime = data['date_time']

    sql = "SELECT name FROM youthdb.user WHERE user_id=%s"
    cursor.execute(sql, user_id)
    name = cursor.fetchone()
    print(name['name'])

    sql = "INSERT INTO youthdb.chat(message, time, userName, user_id, room_id) VALUES(%s, %s, %s, %s, %s)"
    cursor.execute(sql, (message, datetime, name['name'], user_id, room_id))
    conn.commit()

    conn.close()

    emit('chat message', {'room_id': room_id, 'user_id': user_id, 'message': message,
                          'profile_image': img, 'date_time': datetime, 'user_name': name['name']}, broadcast=True)


@socket.on('join')
def join(data):
    join_room(data['room'])
    send({'msg': data['username'] + "참가" + data['room']}, room=data['room'], broadcast=True)


@socket.on('leave')
def leave(data):
    leave_room(data['room'])
    send({'msg': data['username'] + "나감" + data['room']}, room=data['room'], broadcast=True)
