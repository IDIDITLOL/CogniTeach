from flask import (Flask, redirect, render_template, request,send_from_directory, url_for)
app=Flask(__name__)
@app.route("/")
def home():
    return "this is something <h1>It works</h1>"
@app.route("/siha")
def lol():
    return render_template("imalive.html")
@app.route("why")
def hi():
    return render_template("imalive.html")
if __name__=="__main__":
    app.run()
