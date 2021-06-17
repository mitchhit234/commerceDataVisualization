from flask import Flask, render_template, redirect, url_for, request
import graph as g


app = Flask(__name__)




@app.route('/')
def home():
  return render_template("temp-plot.html")

@app.route('/welcome')
def welcome():
  pl = g.main()
  return render_template("welcome.html",plot=pl)


@app.route('/login', methods=['GET', 'POST'])
def login():
  
  error = None
  if request.method == 'POST':
    if request.form['username'] != 'admin' or request.form['password'] != 'admin':
      error = 'Invalid Credentials, please try again'
    else:
      return redirect(url_for('home'))
  
  return render_template('login.html', error=error)



if __name__ == "__main__":
  app.run(debug=True)