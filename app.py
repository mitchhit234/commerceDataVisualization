from re import L
from flask import Flask, render_template, redirect, url_for, request
import graph as g


app = Flask(__name__)

DF = g.initalize()

@app.route('/')
def home():
  pl = g.balance_plot(DF)
  return render_template("index.html",plot=pl)

@app.route('/debit')
def debit():
  pl = g.specalized_plot(DF,'debit')
  return render_template("index.html",plot=pl)

@app.route('/credit')
def credit():
  pl = g.specalized_plot(DF,'credit')
  return render_template("index.html",plot=pl)


if __name__ == "__main__":
  app.run(debug=True)