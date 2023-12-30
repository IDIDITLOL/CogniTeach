from flask import (Flask, redirect, render_template, request,send_from_directory, url_for)
app=Flask(__name__)
@app.route("/")
def home():
    return "lamooo <h1>his</h1>"
@app.route("/why")
def why():
    return render_template("imalive.html")
if __name__=="__main__":
    app.run()
