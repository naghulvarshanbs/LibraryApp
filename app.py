from flask import Flask, render_template, request

app = Flask(__name__)
if __name__=="main":
    app.run(debug=True,port=8080)
@app.route('/',methods=["GET","POST"])
def index():
    if request.method=="GET":
        return render_template('home_login.html')
    elif request.method=="POST":
        email=request.form["email"]
        password=request.form["password"]
       # password=request.form['pwd']
        print(email,password,hash(password))
        return "Logged in"

@app.route('/user_home')
def user_home():
    return render_template("user_home.html")