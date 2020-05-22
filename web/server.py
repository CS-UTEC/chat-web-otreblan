#!/usr/bin/env python3
from flask import Flask,\
           render_template,\
           request,\
           session,\
           Response,\
           send_from_directory
from database import connector
from model import entities
from os import access, R_OK

import json
import time

db = connector.Manager()
engine = db.createEngine()

app = Flask(__name__)

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

    for i in users:
        if (i.password == password):
            # with app.app_context():
            # user_id = i.id
            session['id'] = i.id
            return Response('{"msg": "ok"}', mimetype='application/json')

    return Response('{"msg": "No"}', status=401, mimetype='application/json')


@app.route('/users', methods=['POST'])
def create_user():
    # c = json.loads(request.data)
    c = json.loads(request.form['values'])
    user = entities.User(
        username=c['username'],
        name=c['name'],
        fullname=c['fullname'],
        password=c['password']
    )
    _session = db.getSession(engine)
    _session.add(user)
    _session.commit()
    r_msg = {'msg': 'UserCreated'}
    json_msg = json.dumps(r_msg)
    return Response(json_msg, status=201)


@app.route('/users/<id>', methods=['GET'])
def get_user(id):
    db_session = db.getSession(engine)

    if(id == "-1"):
        id = session['id']

    users = db_session.query(entities.User).filter(entities.User.id == id)
    for user in users:
        js = json.dumps(user, cls=connector.AlchemyEncoder)
        return Response(js, status=200, mimetype='application/json')
    message = {'status': 404, 'message': 'Not Found'}
    return Response(json.dumps(message),
                    status=404,
                    mimetype='application/json')


@app.route('/users', methods=['GET'])
def get_users():
    _session = db.getSession(engine)
    dbResponse = _session.query(entities.User)
    data = dbResponse[:]
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
    return 'Updated User'


@app.route('/users', methods=['DELETE'])
def delete_user():
    id = request.form['key']
    _session = db.getSession(engine)
    user = _session.query(entities.User).filter(entities.User.id == id).one()
    _session.delete(user)
    _session.commit()
    return "Deleted User"


@app.route('/messages', methods=['POST'])
def create_messages():
    # c = json.loads(request.data)
    c = json.loads(request.form['values'])
    message = entities.Message(
        content=c['content'],
        sent_on=c['sent_on'],
        user_from_id=c['user_from_id'],
        user_to_id=c['user_to_id']
    )
    _session = db.getSession(engine)
    _session.add(message)
    _session.commit()
    r_msg = {'msg': 'MessageCreated'}
    json_msg = json.dumps(r_msg)
    return Response(json_msg, status=201)


@app.route('/messages/<id>', methods=['GET'])
def get_message(id: str):
    db_session = db.getSession(engine)
    messages = db_session.query(entities.Messages).\
        filter(entities.Messages.id == id)

    for message in messages:
        js = json.dumps(message, cls=connector.AlchemyEncoder)
        return Response(js, status=200, mimetype='application/json')

    message = {'status': 404, 'message': 'Not Found'}
    return Response(json.dumps(message),
                    status=404,
                    mimetype='application/json')


@app.route('/messages', methods=['GET'])
def get_messages():
    _session = db.getSession(engine)
    dbResponse = _session.query(entities.Message)
    data = dbResponse[:]
    return Response(json.dumps(data, cls=connector.AlchemyEncoder),
                    mimetype='application/json')


@app.route('/messages', methods=['PUT'])
def update_message():
    _session = db.getSession(engine)
    id = request.form['key']
    message = _session.query(entities.Message).\
        filter(entities.Mesage.id == id).first()

    c = json.loads(request.form['values'])

    for key in c.keys():
        setattr(message, key, c[key])

    _session.add(message)
    _session.commit()
    return 'Updated Message'


@app.route('/messages', methods=['DELETE'])
def delete_message():
    id = request.form['key']
    _session = db.getSession(engine)
    message = _session.query(entities.Message).\
        filter(entities.Message.id == id).one()
    _session.delete(message)
    _session.commit()
    return "Deleted User"


# https://serversforhackers.com/c/redirect-http-to-https-nginx
if __name__ == '__main__':
    app.secret_key = ".."
    context = ('/etc/letsencrypt/live/otreblan.ddns.net/fullchain.pem',
               '/etc/letsencrypt/live/otreblan.ddns.net/privkey.pem')

    if access(context[1], R_OK):
        app.run(port=443, threaded=True, host=('0.0.0.0'), ssl_context=context)
    else:
        app.run(port=8080, threaded=True, host=('127.0.0.1'))
