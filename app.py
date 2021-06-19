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
  pl = g.balance_graph()
  return render_template("index.html",plot=pl)


if __name__ == "__main__":
  app.run(debug=True)