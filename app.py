from flask import Flask, render_template, redirect, url_for, request
import graph as g


app = Flask(__name__)


@app.route('/')
def home():
  pl = g.main()
  return render_template("welcome.html",plot=pl)


if __name__ == "__main__":
  app.run(debug=True)