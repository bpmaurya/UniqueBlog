from flask import Flask, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_mail import Mail
import json

with open('config.json', 'r') as c:
    params = json.load(c)["params"]

local_server = True
app = Flask(__name__)
app.secret_key = 'super-secret-key'
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT='465',
    MAIL_USE_SSL=True,
    MAIL_USERNAME=params['gmail_user'],
    MAIL_PASSWARD=params['gmail_pass']
)
mail = Mail(app)

if (local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']

else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']

db = SQLAlchemy(app)


class Contact(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    phonNo = db.Column(db.String(120), nullable=False)
    msg = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(120), nullable=True)
    email = db.Column(db.String(120), nullable=False)


class posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    slug = db.Column(db.String(120), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    tag_line = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(120), nullable=True)
    img_file = db.Column(db.String(120), nullable=True)


@app.route('/')
def home():
    post = posts.query.filter_by().all()[0:params['no_of_post']]
    return render_template('index.html', params=params, posts=post)


@app.route('/about')
def about():
    return render_template('about.html', params=params)


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if ('user' in session and session['user'] == params['admin_user']):
        post = posts.query.all()
        return render_template('dashboard.html', params=params,post=post)

    if request.method == 'POST':
        username = request.form.get('uname')
        userpass = request.form.get('pass')
        if (username == params['admin_user'] and userpass == params['admin_pass']):
            session['user'] = username
            post = posts.query.all()
            return render_template('dashboard.html',post=post)

    return render_template('login.html', params=params)


@app.route("/contact", methods={'GET', 'POST'})
def contact():
    if request.method == 'POST':
        '''add entry to database'''
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        msg = request.form.get('msg')
        entry = Contact(name=name, phonNo=phone, date=datetime.now(), msg=msg, email=email)
        db.session.add(entry)
        db.session.commit()

    return render_template('contact.html', params=params)


@app.route("/post/<string:post_slug>", methods=['GET'])
def post_route(post_slug):
    post = posts.query.filter_by(slug=post_slug).first()
    return render_template('post.html', params=params, post=post)


if __name__ == '__main__':
    app.run(debug=True)
