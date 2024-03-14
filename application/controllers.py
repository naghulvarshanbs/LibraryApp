from flask import Flask, request, redirect, url_for, session, Response
from flask import render_template
from flask import current_app as app
from application.functions import validate_email, valid_password, line_plot, song_plot
from application.models import User
from .database import db
from sqlalchemy import func
from datetime import datetime, timedelta
# from application.models import Article

@app.route('/',methods=["GET","POST"])
def index():
    if request.method=="GET":
        return render_template('home_login.html')
    elif request.method=="POST":
        login_email=request.form["email"]
        login_password=hash(request.form["password"])
        user=User.query.filter_by(email=login_email).first()
        if not user:
            new_user=User(name="None",email=login_email,password=login_password) 
            db.session.add(new_user)
            db.session.commit()
            return "Profile created"
        if user.password==login_password:
            return render_template("user_home.html")
        return "Invalid pwd...Try again!!"

@app.route('/user_home')
def user_home():
    return render_template("user_home.html")
@app.route('/signup')
def signup():
    return "helo"
@app.route('/read')
def read():
    name = request.args.get('name')
    print(name)
    return render_template("books_view.html")