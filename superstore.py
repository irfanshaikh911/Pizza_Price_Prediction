import sqlite3
from flask import Flask, render_template, url_for, request, redirect,jsonify
from joblib import load
from flask_bcrypt import Bcrypt
import pickle

app = Flask(__name__)
app.secret_key = "__privatekey__"
bcrypt = Bcrypt(app)


conn = sqlite3.connect('sqlite.db')
c = conn.cursor()
c.execute("""
    CREATE TABLE IF NOT EXISTS user (
        user_name VARCHAR(10) PRIMARY KEY,
        password TEXT,
        Email Email
    )
""")
conn.commit()
conn.close()

@app.route('/', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('sqlite.db')
        c = conn.cursor()
        c.execute("SELECT * FROM user WHERE user_name = ? AND password = ?", (username, password))
        if not c.fetchone():
            conn.close()
            return render_template('login.html', error="Incorrect Username or Password")
        else:
            conn.close()
            return render_template('index.html', name=username)
    if request.method=='GET':
        pass 
    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username and password:
            conn = sqlite3.connect('sqlite.db')
            c = conn.cursor()
            c.execute("SELECT * FROM user WHERE user_name = (?)", (username,))
            if c.fetchone():
                conn.close()
                return render_template('error.html', error="User already exists")
            else:
                c.execute("INSERT INTO user (user_name, password) VALUES (?, ?)", (username, password))
                conn.commit()
                conn.close()
                return redirect(url_for('login'))
    return render_template('signup.html')


@app.route('/predict', methods=['POST'])
def predict(): 
    le1 = load('data/Encoder_files/Ship Mode_joblib')
    le2 = load('data/Encoder_files/Segment_joblib')
    le3 = load('data/Encoder_files/Region_joblib')
    le4 = load('data/Encoder_files/Category_joblib')
    
    with open ('data/Encoder_files/Model.pkl','rb') as f:
        nb = pickle.load(f)

    if request.method == 'POST':
        data = request.form
        sample = list(data.values())
        
        
        sample[0] = le1.transform([sample[0]])[0]
        sample[1] = le2.transform([sample[1]])[0]
        sample[2] = le3.transform([sample[2]])[0]
        sample[3] = le4.transform([sample[3]])[0]
        
        sample = list(map(float, sample))
        print(sample)
        prediction = nb.predict([sample])[0] 
        final_pred = 'Prediction say that it can be Profit' if prediction =='P' else 'Prediction say that it can be Loss'
        return render_template('result_prediction.html',prediction=final_pred)

if __name__ == '__main__':
    app.run(host='192.168.1.27', port=5000, debug=True) 
