#!/usr/bin/env python3
from flask import Flask,render_template, request, session, Response, redirect
from database import connector
from model import entities
import json
import time

db = connector.Manager()
engine = db.createEngine()

app = Flask(__name__)


@app.route('/static/<content>')
def static_content(content):
    return render_template(content)


@app.route('/', methods=['GET'])
def index() -> str:
    return render_template('index.html')


@app.route('/<something>', methods=['GET'])
def any(something: str) -> str:
    return render_template(something)


@app.route('/authenticate', methods=['POST'])
def authenticate() -> str:
    body = json.loads(request.data)
    username: str = body['username']
    password: str = body['password']

    if (username == password):
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
    users = db_session.query(entities.User).filter(entities.User.id == id)
    for user in users:
        js = json.dumps(user, cls=connector.AlchemyEncoder)
        return Response(js, status=200, mimetype='application/json')
    message = {'status': 404, 'message': 'Not Found'}
    return Response(json.dumps(message), status=404, mimetype='application/json')


@app.route('/users', methods=['GET'])
def get_users():
    _session = db.getSession(engine)
    dbResponse = _session.query(entities.User)
    data = dbResponse[:]
    return Response(json.dumps(data, cls=connector.AlchemyEncoder), mimetype='application/json')


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


if __name__ == '__main__':
    app.secret_key = ".."
    context = ('/etc/letsencrypt/live/otreblan.ddns.net/fullchain.pem',
               '/etc/letsencrypt/live/otreblan.ddns.net/privkey.pem')
    app.run(port=443, threaded=True, host=('0.0.0.0'), ssl_context=context)
