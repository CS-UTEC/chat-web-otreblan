#!/usr/bin/env python3
from sys import stderr
try:
    from flask_socketio import SocketIO, emit, join_room, leave_room
    from flask import Flask,\
        render_template,\
        request,\
        session,\
        Response

    from database import connector
    from model import entities
    from os import access, R_OK
    from isodate import parse_datetime
    from datetime import datetime
    from threading import Lock

    import json
except ImportError:
    print("No olvides usar pip y npm para instalar las dependencias",
          file=stderr)
    print("Las instrucciones están en el README.md", file=stderr)

db = connector.Manager()
engine = db.createEngine()

app = Flask(__name__)
socketio: SocketIO = SocketIO(app)

user_id = 0


@app.route('/static/<content>')
def static_content(content):
    return render_template(content)


@app.route('/<something>', methods=['GET'])
def any(something: str) -> str:
    return render_template(something)


@app.route('/', methods=['GET'])
def index() -> str:
    return render_template('index.html')


@app.route('/authenticate', methods=['POST'])
def authenticate() -> str:
    body = json.loads(request.data)
    username: str = body['username']
    password: str = body['password']

    db_session = db.getSession(engine)
    users = db_session.query(entities.User).\
        filter(entities.User.username == username)

    db_session.close()
    for i in users:
        if (i.password == password):
            # with app.app_context():
            # user_id = i.id
            session['id'] = i.id

            response = {'msg': 'ok', 'id': i.id, 'username': username}
            return Response(json.dumps(response), mimetype='application/json')

    return Response('{"msg": "No"}', status=401, mimetype='application/json')


@app.route('/authenticate', methods=['DELETE'])
def deauthetincate():
    session.pop('id')
    return Response('{"msg": "ok"}', mimetype='application/json')


@app.route('/users', methods=['POST'])
def create_user():
    # c = json.loads(request.data)
    if(not request.is_json):
        c = json.loads(request.form['values'])
    else:
        c = json.loads(request.data)

    user = entities.User(
        username=c['username'],
        name=c['name'],
        fullname=c['fullname'],
        password=c['password']
    )
    _session = db.getSession(engine)
    _session.add(user)
    _session.commit()
    _session.close()
    r_msg = {'msg': 'UserCreated'}
    json_msg = json.dumps(r_msg)
    return Response(json_msg, status=201)


@app.route('/users/<id>', methods=['GET'])
def get_user(id):
    db_session = db.getSession(engine)

    if(id == "-1"):
        id = session['id']

    users = db_session.query(entities.User).filter(entities.User.id == id)
    db_session.close()
    for user in users:
        js = json.dumps(user, cls=connector.AlchemyEncoder)
        return Response(js, status=200, mimetype='application/json')
    message = {'status': 404, 'message': 'Not Found'}
    return Response(json.dumps(message),
                    status=404,
                    mimetype='application/json')


key_users = 'users'
key_messages = 'messages'
cache = {}
user_lock = Lock()
messages_lock = Lock()


@app.route('/users', methods=['GET'])
def get_users():

    def check_cache() -> bool:
        return not (datetime.now() - cache[key_users]['time']).\
            total_seconds() < max_time

    data = []
    old_cache: bool = False
    max_time: int = 20

    if key_users in cache:
        old_cache = check_cache()

        data = cache[key_users]['data']
    else:
        old_cache = True

    if old_cache:
        user_lock.acquire()

        if key_users not in cache or check_cache():

            _session = db.getSession(engine)
            dbResponse = _session.query(entities.User).\
                order_by(entities.User.username)

            _session.close()
            data = dbResponse[:]

            # Set cache
            cache[key_users] = {'data': data, 'time': datetime.now()}

        user_lock.release()

    return Response(json.dumps(data, cls=connector.AlchemyEncoder),
                    mimetype='application/json')


@app.route('/users', methods=['PUT'])
def update_user():
    _session = db.getSession(engine)
    id = request.form['key']
    user = _session.query(entities.User).filter(entities.User.id == id).first()
    c = json.loads(request.form['values'])

    for key in c.keys():
        setattr(user, key, c[key])

    _session.add(user)
    _session.commit()
    _session.close()
    return 'Updated User'


@app.route('/users', methods=['DELETE'])
def delete_user():
    id = request.form['key']
    _session = db.getSession(engine)
    user = _session.query(entities.User).filter(entities.User.id == id).one()
    _session.delete(user)
    _session.commit()
    _session.close()
    return "Deleted User"


@app.route('/messages', methods=['POST'])
def create_messages():
    # c = json.loads(request.data)
    if(not request.is_json):
        c = json.loads(request.form['values'])
    else:
        c = json.loads(request.data)

    message = entities.Message(
        content=c['content'],
        # sent_on=parse_datetime(c['sent_on']),
        sent_on=datetime.now(),
        user_from_id=c['user_from_id'],
        user_to_id=c['user_to_id']
    )

    _session = db.getSession(engine)
    _session.add(message)
    _session.commit()
    r_msg = {'msg': 'MessageCreated'}
    json_msg = json.dumps(r_msg)
    _session.close()

    socketio.emit("newMessage", {'data': 'New messages'},
                  room=str(c['user_from_id']) + "-" + str(c['user_to_id']),
                  namespace="/messages")

    return Response(json_msg, status=201)


@app.route('/messages/<id>', methods=['GET'])
def get_message(id: str):
    db_session = db.getSession(engine)
    messages = db_session.query(entities.Message).\
        filter(entities.Message.id == id)

    db_session.close()
    for message in messages:
        js = json.dumps(message.to_dict())
        return Response(js, status=200, mimetype='application/json')

    message = {'status': 404, 'message': 'Not Found'}
    return Response(json.dumps(message),
                    status=404,
                    mimetype='application/json')


@app.route('/messages/<user_from>/<user_to>', methods=['GET'])
def get_users_messages(user_from: str, user_to: str):
    users = [user_from, user_to]

    db_session = db.getSession(engine)
    messages = db_session.query(entities.Message).\
        filter(entities.Message.user_from_id.in_(users)).\
        filter(entities.Message.user_to_id.in_(users))

    db_session.close()

    if messages:
        return Response(json.dumps([x.to_dict() for x in messages]),
                        mimetype='application/json')

    message = {'status': 404, 'message': 'Not Found'}
    return Response(json.dumps(message),
                    status=404,
                    mimetype='application/json')


@app.route('/messages', methods=['GET'])
def get_messages():

    data = []
    update_cache: bool = False
    max_time: int = 20

    if key_messages in cache:
        update_cache = not (datetime.now() - cache[key_messages]['time']).\
            total_seconds() < max_time

        data = cache[key_messages]['data']
    else:
        update_cache = True

    if update_cache:
        _session = db.getSession(engine)
        dbResponse = _session.query(entities.Message)

        data = dbResponse[:]
        _session.close()

        # Set cache
        cache[key_messages] = {'data': data, 'time': datetime.now()}

    return Response(json.dumps([x.to_dict() for x in data]),
                    mimetype='application/json')


@app.route('/messages', methods=['PUT'])
def update_message():
    _session = db.getSession(engine)
    id = request.form['key']
    message = _session.query(entities.Message).\
        filter(entities.Message.id == id).first()

    c = json.loads(request.form['values'])

    for key in c.keys():
        setattr(message,
                key,
                parse_datetime(c[key]) if key == "sent_on" else c[key])

    _session.add(message)
    _session.commit()
    _session.close()
    return 'Updated Message'


@socketio.on('connect', namespace='/messages')
def connect_message():
    emit('info', {'data': 'Connected'})


@socketio.on('listen', namespace='/messages')
def listen_messages(data):
    print("listen")
    join_room(str(data["toId"])+"-"+str(data["fromId"]))


@socketio.on('ignore', namespace='/messages')
def ignore_messages(data):
    print("ignore")
    leave_room(str(data["toId"])+"-"+str(data["fromId"]))


@app.route('/messages', methods=['DELETE'])
def delete_message():
    id = request.form['key']
    _session = db.getSession(engine)
    message = _session.query(entities.Message).\
        filter(entities.Message.id == id).one()
    _session.delete(message)
    _session.commit()
    _session.close()
    return "Deleted User"


# https://serversforhackers.com/c/redirect-http-to-https-nginx
def main():
    app.secret_key = ".."
    context = ('/etc/letsencrypt/live/otreblan.ddns.net/fullchain.pem',
               '/etc/letsencrypt/live/otreblan.ddns.net/privkey.pem')

    # socketio.run(app)
    if access(context[1], R_OK):
        socketio.run(app, port=443, host=('0.0.0.0'),
                     certfile=context[0],
                     keyfile=context[1],
                     log_output=True,
                     debug=True
                     )
    else:
        socketio.run(app, port=8080, host=('127.0.0.1'))


if __name__ == '__main__':
    main()
