import base64
from flask import Flask, flash, request, redirect, send_file, url_for, session, Response
from flask import render_template
from flask import current_app as app
from application.models import User, Books, Ad, Issue_Request, Section, Section_Contents
from .database import db
from datetime import datetime, timedelta
import datetime
# from application.models import Article

@app.route('/',methods=["GET","POST"])
def index():
    if request.method=="GET":
        return render_template('home_login.html')
    elif request.method=="POST":
        login_email=request.form["email"]
        login_password=request.form["password"]
        user=User.query.filter_by(email=login_email).first()
       
        if not user:
            new_user=User(name="None",email=login_email,password=login_password) 
            db.session.add(new_user)
            db.session.commit()
            flash("Profile created")
            return render_template('home_login.html')
        print(user.password)
        if str(user.password)==login_password:
            session["id"]=user.id
            return redirect("/user_home")
        return "Invalid pwd...Try again!!"

@app.route('/user_home',methods=["GET","POST"])
def user_home():
     if request.method=="GET":
      issued=Books.query.filter_by(issued_to=session["id"])
      for i in issued:
            if i.renewal_date<datetime.date.today():
                i.issued_to=0
      db.session.commit()
      books = Books.query.filter(Books.issued_to != session["id"]).order_by(Books.upload_date.desc()).all()
      sections=Section.query.order_by(Section.name).all()
      
      for book in books:
            # Assuming `book.book_cover` contains Blob data
            encoded_image_data = base64.b64encode(book.book_cover).decode('utf-8')
            book.book_cover = encoded_image_data
      issued=Books.query.filter_by(issued_to=session["id"])
      for i in issued:          
            # Assuming `book.book_cover` contains Blob data
            encoded_image_data = base64.b64encode(i.book_cover).decode('utf-8')
            i.book_cover = encoded_image_data
      return render_template("user_home.html", books=books,issued=issued,sections=sections,usr=session["id"])
     if request.method=="POST":
         b_id=request.form["book_id"]
         newRequest=Issue_Request(book_id=b_id,user_id=session["id"],dt=datetime.date.today(),period=request.form["days"])
         db.session.add(newRequest)
         db.session.commit()
         return redirect("/user_home")
@app.route('/signup',methods=["GET","POST"])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        new_user = User(name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        session["id"]=new_user.id
        return redirect(url_for('user_home'))
    return render_template('signup.html')
@app.route('/read/<int:id>')
def read(id):
    print(id)
    book = Books.query.filter_by(book_id=id).first()
    with open('static/cover.jpg', 'wb') as i:
      i.write(book.book_cover)
    with open('static/output_file.pdf', 'wb') as f:
      f.write(book.book_content)
    return render_template("books_view.html",title=book.book_name,author=book.book_author)
@app.route("/admin_login",methods=["GET","POST"])
def admin_login():
    if request.method=="GET":
        return render_template("admin_login.html")
    elif request.method=="POST":
      em=request.form['email']
      pwd=request.form['password']
      cred=Ad.query.filter_by(email=em).first()
      if not cred:
         return "Invalid credentials"
      if cred.password!=pwd:
          return "invalid credentials"
      return redirect("admin_home")

@app.route('/return/<int:id>')
def ret(id):
    x=Books.query.filter_by(book_id=id).first()
    x.issued_to=0
    db.session.commit()
    return redirect("/user_home")
@app.route("/admin_home", methods=["GET", "POST"])
def admin():
    if request.method == "GET":
        # Retrieve all books and pending issues
        books = Books.query.order_by(Books.upload_date.desc()).all()
        issues = Issue_Request.query.order_by(Issue_Request.dt).all()
        sections=Section.query.order_by(Section.name).all()
        # Encode book covers to base64 for display in HTML
        for book in books:
            encoded_image_data = base64.b64encode(book.book_cover).decode('utf-8')
            book.book_cover = encoded_image_data
        users = {user.id: user for user in User.query.all()}
        print(users[3])
        return render_template("admin_home.html", books=books, issues=issues,sections=sections,users=users)
    
    elif request.method == "POST":
         action = request.form["action"]
         if action == "1":  # Approve issue
            # Handle issue approval
            book_id = request.form["book_id"]
            user_id = request.form["user_id"]
            i = Issue_Request.query.filter_by(book_id=book_id, user_id=user_id).first()
            curr_books = Books.query.filter_by(issued_to=user_id).count()
            if curr_books < 4:
                book = Books.query.filter_by(book_id=book_id).first()
                book.issued_to = user_id
                book.renewal_date=datetime.date.today()+timedelta(days=i.period)
                db.session.commit()
            # Delete the issue request
            issue = Issue_Request.query.filter_by(book_id=book_id, user_id=user_id).first()
            db.session.delete(issue)
            db.session.commit()
         elif action == "2":  # Upload new book
            # Handle uploading new book
            name = request.form["book_name"]
            author = request.form["book_author"]
            content = request.files["content"].read()
            cover = request.files["cover"].read()
            new_book = Books(
                book_name=name,
                book_author=author,
                book_content=content,
                book_cover=cover,
                issue_date=datetime.date.today(),
            )
            db.session.add(new_book)
            db.session.commit()
        
         elif action == "3":  # Delete book
            # Handle deleting a book
            book_id = request.form["book_id"]
            sec=Section_Contents.query.filter_by(book_id=book_id).all()
            for i in sec:
                db.session.delete(i)
            book = Books.query.filter_by(book_id=book_id).first()
            db.session.delete(book)
            db.session.commit()
        
         elif action == "4":  # Update book
            # Handle updating existing book
            book_id = request.form["b_id"]
            book = Books.query.filter_by(book_id=book_id).first()
            
            if "content" in request.files:

               ct=request.files["content"].read()
               if ct!=b'':
                  book.book_content = ct

            if "cover" in request.files :
               im=request.files["cover"].read()
               print(im)
               if im!=b'':
                  book.book_cover = im

            if "book_name" in request.form and request.form["book_name"]:
               book.book_name = request.form["book_name"]

            if "book_author" in request.form and request.form["book_author"]:
               book.book_author = request.form["book_author"]

         # Commit changes to the database
            db.session.commit()
         elif request.form["action"]=="5":
             s_name=request.form["section_name"]
             s_desc=request.form["section_description"]
             newSec=Section(name=s_name,description=s_desc)
             db.session.add(newSec)
             db.session.commit()
         elif action=="6":
             newSecCont=Section_Contents(section_id=request.form["s_id"],book_id=request.form["b_id"])
             db.session.add(newSecCont)
             db.session.commit()
         elif action=="7":
             b=Books.query.filter_by(book_id=request.form["book_id"]).first()
             b.issued_to=0
             db.session.commit()
         elif action=="8":
             print("Delete section: ",request.form["sec"])
             sec=Section_Contents.query.filter_by(section_id=request.form["sec"]).all()
             for i in sec:
                 db.session.delete(i)
             s=Section.query.filter_by(id=request.form["sec"]).first()
             db.session.delete(s)
             db.session.commit()
         elif action=="9":
             print(request.form["search-input"])
         return redirect("/admin_home")
