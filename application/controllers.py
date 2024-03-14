from flask import Flask, request, redirect, send_file, url_for, session, Response
from flask import render_template
from flask import current_app as app
from application.functions import validate_email, valid_password, line_plot, song_plot
from application.models import User, Books
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
@app.route('/read/<b_name>')
def read(name):
    print(name)
    return render_template("books_view.html")
@app.route("/admin_home",methods=["GET","POST"])
def admin():
    if request.method=="GET":
      return render_template("admin_home.html")
    else:
      #   print(request.form["book_name"])
      #   print(request.form["book_author"])
      #   print(request.files["content"].read())
        name=request.form["book_name"]
        author=request.form["book_author"]
        content=request.files["content"].read()
        cover=request.files["cover"].read()
        new_book=Books(book_name=name,book_author=author,book_content=content,book_cover=cover)
        db.session.add(new_book)
        db.session.commit()
        return render_template("admin_home.html")
@app.route("/document/<int:document_id>")
def get_document(document_id):
    document = Books.query.filter_by(book_id=document_id).first()
    return send_file(
        document.book_content,
        mimetype="application/pdf"
    )