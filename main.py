from flask import (Flask, redirect, render_template, request,send_from_directory, url_for)
app=Flask(__name__)
@app.route("/")
def home():
    return render_template("imalive.html")
@app.route("/lol")
def lol():
    return render_template("imalive.html")
@app.route("hi")
def hi():
    return render_template("imalive.html")
if __name__=="__main__":
    app.run()
