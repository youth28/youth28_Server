from flask import jsonify, json, request, send_file
from pybo import config
from werkzeug.utils import secure_filename
import pymysql
from pybo.main import bp


@bp.route('/')
def index():
    return '28 청춘'


@bp.route('/user')
def select():
    conn = config.get_connection()
    sql = "SELECT * FROM youthdb.user"
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute(sql)
    data = cursor.fetchall()
    conn.close()
    return jsonify({"code": 200, "count": 0, "data": data})


@bp.route('/register', methods=["POST"])
def register():
    conn = config.get_connection()
    cursor = conn.cursor()
    json_data = request.get_json()
    sql = "INSERT INTO youthdb.user (email, pwd, name, field) VALUES (%s, %s, %s, %s)"
    cursor.execute(sql,
                   (json_data['email'], json_data['pwd'], json_data['name'], json_data['field']))
    conn.commit()
    conn.close()
    return jsonify({"code": 200})


@bp.route('/register/check_email', methods=["POST"])
def check_email():
    conn = config.get_connection()
    cursor = conn.cursor()
    email = request.get_json()
    print(email['email'])
    sql = "SELECT email FROM youthdb.user where email=%s"
    cursor.execute(sql, email['email'])
    data = cursor.fetchone()
    if data is None:
        conn.close()
        return jsonify({'code': 200})
    else:
        print(data[0])
        return '', 204


@bp.route('/login', methods=["POST"])
def login():
    conn = config.get_connection()
    cursor = conn.cursor()
    json_data = request.get_json()
    email = json_data['email']
    pwd = json_data['pwd']
    print(email)
    cursor.execute("SELECT pwd FROM youthdb.user where email=%s", email)
    check_pwd = cursor.fetchone()
    if check_pwd is None:
        conn.close()
        print("204")
        return '', 204

    print(check_pwd[0])
    if check_pwd[0] == pwd:
        print("비번 일치")
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT user_id, name FROM youthdb.user where email=%s", email)
        data = cursor.fetchone()
        print(data)
        conn.close()
        return jsonify(data)

    conn.close()
    return '', 204


@bp.route('/modify_user', methods=["POST"])
def modify_user():
    conn = config.get_connection()
    cursor = conn.cursor()
    json_data = request.get_json()
    sql = "UPDATE youthdb.user SET name=%s, field=%s where user_id=%s"
    cursor.execute(sql, (json_data['name'], json_data['field'], json_data['user_id']))
    conn.commit()
    conn.close()
    return jsonify({"code": 200})


@bp.route('/user_info', methods=['POST'])
def user_info():
    conn = config.get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    json_data = request.get_json()
    sql = "SELECT * FROM youthdb.user WHERE user_id=%s"
    cursor.execute(sql, json_data['user_id'])
    data = cursor.fetchone()
    print(data)
    conn.close()
    return jsonify(data)


@bp.route('/my_room', methods=["POST"])
def my_room():
    conn = config.get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    json_data = request.get_json()
    user_room = []
    cursor.execute("SELECT room_id FROM youthdb.join_room WHERE user_id=%s", json_data['user_id'])
    data = cursor.fetchall()
    print(data)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    for room in data:
        cursor.execute("SELECT room_id, title FROM youthdb.room WHERE room_id=%s", room['room_id'])
        room_data = cursor.fetchone()
        user_room.append(room_data)
    print(user_room)
    conn.close()
    return jsonify({"code": 200, "count": len(data), "room": user_room})


@bp.route('/modify_room', methods=["POST"])
def modify_room():
    conn = config.get_connection()
    cursor = conn.cursor()
    json_data = request.get_json()
    sql = "UPDATE youthdb.room SET title=%s, maxPeo=%s, field=%s, profile=%s where room_id=%s"
    cursor.execute(sql, (
        json_data['title'], json_data['maxPeo'], json_data['field'], json_data['profile'], json_data['room_id']))
    conn.commit()
    conn.close()
    return jsonify({"code": 200})


@bp.route('/make_room', methods=["POST"])
def make_room():
    conn = config.get_connection()
    cursor = conn.cursor()
    json_data = request.get_json()
    sql = "INSERT INTO youthdb.room (title, maxPeo, field, profile, room_manager) VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(sql, (
        json_data['title'], json_data['maxPeo'], json_data['field'], json_data['profile'], json_data['user_id']))
    conn.commit()
    sql = "SELECT room_id FROM youthdb.room WHERE title=%s"
    cursor.execute(sql, json_data['title'])
    room_id = cursor.fetchone()
    sql = "INSERT INTO youthdb.join_room (user_id, room_id) VALUES (%s, %s)"
    cursor.execute(sql, (json_data['user_id'], room_id))
    conn.commit()
    conn.close()
    return jsonify({"code": 200})


@bp.route('/room_join', methods=["POST"])
def room_join():
    conn = config.get_connection()
    cursor = conn.cursor()
    json_data = request.get_json()
    sql = "SELECT * FROM youthdb.join_room WHERE user_id=%s and room_id=%s"
    cursor.execute(sql, (json_data['user_id'], json_data['room_id']))
    data = cursor.fetchone()
    print(data)
    if data is not None:
        conn.close()
        return '', 204
    sql = "INSERT INTO youthdb.join_room (user_id, room_id) VALUES (%s, %s)"
    cursor.execute(sql, (json_data['user_id'], json_data['room_id']))
    conn.commit()
    conn.close()
    return jsonify({"code": 200})


@bp.route('/room_search', methods=["POST"])
def room_search():
    conn = config.get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    json_data = request.get_json()
    print(json_data['room_name'])
    cursor.execute("SELECT * FROM youthdb.room WHERE title LIKE '%" + json_data['room_name'] + "%'")
    data = cursor.fetchall()
    print(data)
    conn.close()
    return jsonify({"code": 200, "room": data})


@bp.route('/room_info', methods=["POST"])
def room_info():
    conn = config.get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    json_data = request.get_json()
    cursor.execute("SELECT title, maxPeo, field, profile, room_manager FROM youthdb.room WHERE room_id=%s",
                   json_data['room_id'])
    data = cursor.fetchone()
    print(data)
    conn.close()
    return jsonify(data)


@bp.route('/room_list', methods=["POST"])
def room_list():
    data = []
    conn = config.get_connection()
    cursor = conn.cursor()
    json_data = request.get_json()
    cursor.execute("SELECT field FROM youthdb.user WHERE user_id=%s", json_data['user_id'])
    field = cursor.fetchone()
    print(field[0])
    split_field = field[0].split(',')
    print(split_field)
    for i in split_field:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM youthdb.room WHERE field LIKE '%" + i + "%'")
        data += cursor.fetchall()
        print(data)
    conn.close()
    return jsonify({"code": 200, "room": data})


@bp.route('/schedule_write', methods=["POST"])
def schedule_write():
    conn = config.get_connection()
    cursor = conn.cursor()
    json_data = request.get_json()
    sql = "INSERT INTO youthdb.schedule (content, date, user_id) VALUES (%s, %s, %s)"
    cursor.execute(sql, (json_data['content'], json_data['date'], json_data['user_id']))
    conn.commit()
    conn.close()
    return jsonify({"code": 200})


@bp.route('/schedule_read', methods=["POST"])
def schedule_read():
    conn = config.get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    json_data = request.get_json()
    print(json_data['user_id'])
    sql = "SELECT content, date FROM youthdb.schedule WHERE user_id=%s"
    cursor.execute(sql, json_data['user_id'])
    data = cursor.fetchall()
    print(data)
    conn.close()
    return jsonify({"code": 200, "schedule": data})


@bp.route('/room_schedule_read', methods=['POST'])
def room_schedule_read():
    conn = config.get_connection()
    cursor = conn.cursor()
    json_data = request.get_json()
    schedule_data = []
    sql = "SELECT user_id FROM youthdb.join_room WHERE room_id=%s"
    cursor.execute(sql, json_data['room_id'])
    data = cursor.fetchall()
    print(data)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    for i in data:
        sql = "SELECT * FROM youthdb.schedule WHERE user_id=%s"
        cursor.execute(sql, i)
        schedule_data += cursor.fetchall()
    conn.close()
    return jsonify({"code": 200, "room_schedule": schedule_data})


@bp.route('/image_upload', methods=['POST'])
def image_upload():
    if 'file' not in request.files:
        print("아무것도 없음")
        return '', 204
    conn = config.get_connection()
    cursor = conn.cursor()
    u = request.form.get('user_id')
    user_id = u.replace("{", '').replace('}', '').split(':')[1]
    f = request.files['file']
    print(f)
    f.save("D:/flask_image_upload/profile/" + secure_filename(f.filename))
    sql = "INSERT INTO youthdb.profile(img, user_id) VALUES(%s, %s)"
    cursor.execute(sql, (f.filename, user_id))
    conn.commit()
    conn.close()
    return jsonify({"code": 200})


@bp.route('/image_re_upload', methods=['POST'])
def image_re_upload():
    if 'file' not in request.files:
        print("아무것도 없음")
        return '', 204
    conn = config.get_connection()
    cursor = conn.cursor()
    f = request.files['file']
    u = request.form.get('user_id')
    user_id = u.replace("{", '').replace('}', '').split(':')[1]
    print(f)
    f.save('D:/flask_image_upload/profile/' + secure_filename(f.filename))
    sql = "UPDATE youthdb.profile set img=%s where user_id=%s"
    cursor.execute(sql, (f.filename, user_id))
    conn.commit()
    conn.close()
    return jsonify({"code": 200})


@bp.route('/room_image_upload', methods=['POST'])
def room_image_upload():
    if 'file' not in request.files:
        print("아무것도 없음")
        return '', 204
    conn = config.get_connection()
    cursor = conn.cursor()
    u = request.form.get('room_id')
    room_id = u.replace("{", '').replace('}', '').split(':')[1]
    f = request.files['file']
    print(f)
    f.save("D:/flask_image_upload/room_profile/" + secure_filename(f.filename))
    sql = "INSERT INTO youthdb.room_profile(img, room_id) VALUES(%s, %s)"
    cursor.execute(sql, (f.filename, room_id))
    conn.commit()
    conn.close()
    return jsonify({"code": 200})


@bp.route('/room_image_re_upload', methods=['POST'])
def room_image_re_upload():
    if 'file' not in request.files:
        print("아무것도 없음")
        return '', 204
    conn = config.get_connection()
    cursor = conn.cursor()
    f = request.files['file']
    u = request.form.get('room_id')
    room_id = u.replace("{", '').replace('}', '').split(':')[1]
    print(f)
    f.save('D:/flask_image_upload/room_profile/' + secure_filename(f.filename))
    sql = "UPDATE youthdb.room_profile set img=%s where room_id=%s"
    cursor.execute(sql, (f.filename, room_id))
    conn.commit()
    conn.close()
    return jsonify({"code": 200})


@bp.route('/image_load', methods=['POST'])
def image_load():
    conn = config.get_connection()
    cursor = conn.cursor()
    json_data = request.get_json()
    sql = "SELECT img FROM youthdb.profile WHERE user_id=%s"
    cursor.execute(sql, json_data['user_id'])
    data = cursor.fetchone()
    if data is None:
        return '', 204
    print(data[0])
    file_dir = 'D:/flask_image_upload/profile/' + data[0]
    return send_file(file_dir)


@bp.route('/room_image_load', methods=['POST'])
def room_image_load():
    conn = config.get_connection()
    cursor = conn.cursor()
    json_data = request.get_json()
    sql = "SELECT img FROM youthdb.room_profile WHERE room_id=%s"
    cursor.execute(sql, json_data['room_id'])
    data = cursor.fetchone()
    if data is None:
        return '', 204
    file_dir = 'D:/flask_image_upload/room_profile/' + data[0]
    return send_file(file_dir)


@bp.route('/chat_load', methods=['POST'])
def chat_load():
    conn = config.get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    json_data = request.get_json()
    print(json_data['room_id'])
    sql = "SELECT message, time, userName, user_id FROM youthdb.chat WHERE room_id=%s"
    cursor.execute(sql, json_data['room_id'])
    data = cursor.fetchall()
    print(data)
    return jsonify({'code': 200, 'data': data})


@bp.route('/question_make', methods=['POST'])
def question_make():
    conn = config.get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    json_data = request.get_json()
    sql = "SELECT name FROM youthdb.user WHERE user_id=%s"
    cursor.execute(sql, json_data['user_id'])
    user_name = cursor.fetchone()
    sql = "INSERT INTO youthdb.question(question_text, content1, content2, content3, content4, content5, " \
          "time, dead_line, done, room_id, user_id, name) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    cursor.execute(sql, (json_data['question_text'], json_data['content1'], json_data['content2'],
                         json_data['content3'], json_data['content4'], json_data['content5'], json_data['time'],
                         json_data['dead_line'], json_data['done'], json_data['room_id'], json_data['user_id'],
                         user_name['name']))
    conn.commit()
    conn.close()
    return jsonify({"code": 200})


@bp.route('/vote', methods=['POST'])
def vote():
    conn = config.get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    json_data = request.get_json()
    sql = "SELECT name FROM youthdb.user WHERE user_id=%s"
    cursor.execute(sql, json_data['user_id'])
    user_name = cursor.fetchone()
    sql = "INSERT INTO youthdb.select_table(select_text, name, user_id, question_id) VALUES(%s, %s, %s, %s)"
    cursor.execute(sql, (json_data['select_text'], user_name['name'], json_data['user_id'], json_data['question_id']))
    conn.commit()
    conn.close()
    return jsonify({"code": 200})


@bp.route('/look_vote', methods=['POST'])
def look_vote():
    conn = config.get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    json_data = request.get_json()
    sql = "SELECT question_text, content1, content2, content3, content4, content5, time, dead_line, name " \
          "FROM youthdb.question WHERE question_id=%s"
    cursor.execute(sql, json_data['question_id'])
    data = cursor.fetchone()
    conn.close()
    return jsonify(data)


@bp.route('/end_vote', methods=['POST'])
def end_vote():
    conn = config.get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    json_data = request.get_json()
    sql = "UPDATE youthdb.question SET done=%s WHERE question_id=%s"
    cursor.execute(sql, (json_data['done'], json_data['question_id']))
    conn.commit()
    conn.close()
    return jsonify({'code': 200})


@bp.route('/list_vote', methods=['POST'])
def list_vote():
    conn = config.get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    json_data = request.get_json()
    sql = "SELECT question_id, question_text, time, done, name FROM youthdb.question WHERE room_id=%s"
    cursor.execute(sql, (json_data['room_id']))
    data = cursor.fetchall()
    conn.close()
    return jsonify({'data': data})


@bp.route('/now_vote', methods=['POST'])
def now_vote():
    content1_cnt = int(0)
    content2_cnt = int(0)
    content3_cnt = int(0)
    content4_cnt = int(0)
    content5_cnt = int(0)
    conn = config.get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    json_data = request.get_json()
    sql = "SELECT * FROM youthdb.question WHERE question_id=%s"
    cursor.execute(sql, json_data['question_id'])
    data = cursor.fetchone()
    print(data)
    for i in range(1, 6):
        sql = "SELECT count(select_id) as cnt FROM youthdb.select_table WHERE select_text=%s"
        if data['content' + str(i)] is not None:
            cursor.execute(sql, data['content' + str(i)])
            if i == 1:
                content1_cnt = cursor.fetchone()
            elif i == 2:
                content2_cnt = cursor.fetchone()
            elif i == 3:
                content3_cnt = cursor.fetchone()
            elif i == 4:
                content4_cnt = cursor.fetchone()
            elif i == 5:
                content5_cnt = cursor.fetchone()
    return jsonify({'question_text': data['question_text'], 'content1': data['content1'], 'content2': data['content2'],
                    'content3': data['content3'], 'content4': data['content4'], 'content5': data['content5'],
                    'content1_cnt': content1_cnt['cnt'], 'content2_cnt': content2_cnt['cnt'],
                    'content3_cnt': content3_cnt['cnt'], 'content4_cnt': content4_cnt['cnt'],
                    'content5_cnt': content5_cnt['cnt'], 'time': data['time'],
                    'dead_line': data['dead_line'], 'name': data['name']})
