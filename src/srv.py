from datetime import datetime
from flask import (abort, escape, Flask, jsonify, redirect, request,
    render_template, session, url_for)
from flaskext.bcrypt import Bcrypt
#import wtforms as _wtf
from pymongo import MongoClient
import json
from redis import StrictRedis
from users import Users

das_host = "kilrog.dyndns.org"

redis = StrictRedis(host=das_host, port=6379)

client = MongoClient(das_host, 27017)
db = client['mtgo']
c_users = db['users']
c_downloads = db['downloads']
c_vendors = db['vendors']
user_handler = Users(c_users)

srv = Flask(__name__, static_folder='public', static_url_path='')
srv.secret_key = 'b\xa7\x9b\x87\xedR\xd3\xbe\x01{\xb4\x15XK\xc7\xce\x06\x81\xc6\x17\xb7}dZ'
bcrypt = Bcrypt(srv)

#@srv.route('/static/<path:filename>')
#@srv.route('/static', defaults={'filename': ''})
#@srv.route('/static/<path:filename>')
#def statix(filename):
#    return render_template(url_for("static", filename=filename))

@srv.route('/')
def index():
    #return render_template('index.html')
    return render_template('ceepee.html')

@srv.route('/api/vendor')
def get_vendors():
    # #ihatecaching
    return jsonify(result={
        'vendors': [v['name'] for v in c_vendors.find()]
    })

@srv.route('/api/auth', methods=['POST'])
def login():
    data = request.form
    db_user = user_handler.get_by_email(data['email'])
    if not db_user:
        # technically a timing attack
        return jsonify(result={'msg': 'user/pw combination not found'})
        #abort(403)
    if not bcrypt.check_password_hash(db_user['password'], data['password']):
        # technically a timing attack
        return jsonify(result={'msg': 'user/pw combination not found'})
        #abort(403)
    session['email'] = data['email']
    return jsonify(result={'success':True})

@srv.route('/api/user', methods=['POST'])
def user_create():
    print 'user data', request.data
    created = user_handler.create(json.loads(request.data))
    # XXX this probably shouldn't return the user's pw hash
    return jsonify(result=created)

@srv.route('/api/user/<_id>', methods=['PUT'])
def user_update(_id):
    #to_update = json.loads(request.data)
    to_udpate = request.form
    to_update['_id'] = _id
    updated = user_handler.update(to_update)
    return jsonify(result=updated)

@srv.route('/api/<_id>', methods=['DELETE'])
def user_delete(_id):
    user_handler.delete(_id)
    return jsonify(result={'success':True})

@srv.route('/api/user/logout', methods=['POST'])
def user_logout():
    session.pop('email', None)
    return jsonify(result={'success':True})

@srv.route('/api/whoami', methods=['GET'])
def whoami():
    if 'email' in session:
        return jsonify(result={'email': session['email']})
    return jsonify({})

@srv.route('/signup', methods=['POST'])
def user_signup():
    data = request.form
    if not data['password'] == data['password_confirm']:
        # TODO set this as proper error
        return jsonify(result={'msg': 'Passwords did not match!'})
    if user_handler.get_by_email(data['email']):
        return jsonify(result={'msg': 'User exists already!'})
    user = {
        'email': data['email'],
        'password': bcrypt.generate_password_hash(data['password']),
        'createdOn': datetime.today(),
    }
    user = user_handler.create(user)
    session['email'] = data['email']
    print 'signed up w/user:', user
    return jsonify(result={'success':True})

"""
routes
app.post('/api/auth', user.login);
app.post('/api/user', user.post);
app.put('/api/user/:_id', user.put);
app.delete('/api/user/:_id', user.delete);
app.post('/api/user/logout', user.logout);

app.get('/api/whoami', user.whoami);
app.get('/', routes.index);
app.post('/signup', user.signup_post);
"""
if __name__ == "__main__":
    srv.debug=True
    srv.run(host='0.0.0.0')
