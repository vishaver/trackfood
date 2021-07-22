from flask import Flask,render_template,g,request
import sqlite3
from datetime import datetime

app = Flask(__name__)

def connect_db():
    sql = sqlite3.connect("C:\\Users\\vishaver\\PycharmProjects\\trackfood\\food_log.db")
    sql.row_factory = sqlite3.Row
    return sql

def get_db():
    if not hasattr(g,'sqlite3'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g,'sqlite_db'):
        g.sqlite_db.close()

@app.route('/',methods=['GET','POST'])
def index():
    db = get_db()

    if request.method == 'POST':
        date = request.form['date']
        print(date)
        # formatdate = datetime.strptime(date, '%Y-%m-%d').strftime("%B %d, %Y")
        formatdate = datetime.strptime(date, '%Y-%m-%d').strftime("%Y%m%d")
        print(formatdate)
        db.execute('insert into log_date (entry_date) values (?)',[formatdate])
        db.commit()

    cur = db.execute('select log_date.entry_date, sum(food.protein) as protein, sum(food.carbohydrate) as carbohydrate, sum(food.fat) as fat,sum(food.calories) as calories from log_date join food_date on food_date.log_date_id = log_date.id join food on food.id = food_date.food_id group by log_date.id order by log_date.entry_date desc')
    results  = cur.fetchall()
    date_results = []
    for i in results:
        single_date = {}
        single_date['entry_date'] = i['entry_date']
        single_date['protein'] = i['protein']
        single_date['carbohydrate'] = i['carbohydrate']
        single_date['fat'] = i['fat']
        single_date['calories'] = i['calories']
        single_date['pretty_date'] = datetime.strptime(str(i['entry_date']), '%Y%m%d').strftime("%B %d, %Y")
        date_results.append(single_date)
    return render_template('home.html',results=date_results)


@app.route('/view/<date>',methods=['GET','POST'])
def view(date):
    db = get_db()
    cur = db.execute('select id,entry_date from log_date where entry_date = ?',[date])
    date_result = cur.fetchone()
    if request.method == 'POST':
        print("This is post request.")
        print("filled form value",request.form['food-select'])
        print("date id is", date_result['id'])
        db.execute('insert into food_date (food_id,log_date_id) values (?,?)', [request.form['food-select'],date_result['id']])
        db.commit()
    preety_date = datetime.strptime(str(date_result['entry_date']), '%Y%m%d').strftime("%B %d, %Y")
    food_cur = db.execute('select id,name from food')
    food_results = food_cur.fetchall()

    cur = db.execute('select food.name, food.protein, food.carbohydrate, food.fat,food.calories from log_date join food_date on \
    food_date.log_date_id = log_date.id join food on food.id = food_date.food_id where log_date.entry_date = ?', [date])
    log_results = cur.fetchall()

    total = {}
    total['protein'] = 0
    total['carbohydrate'] = 0
    total['fat'] = 0
    total['calories'] = 0

    for food in log_results:
        total['protein'] += food['protein']
        total['carbohydrate'] += food['carbohydrate']
        total['fat'] += food['fat']
        total['calories'] += food['calories']

    return render_template('day.html',entry_date=date_result['entry_date'],date=preety_date, food_results=food_results,log_results=log_results,total=total)


@app.route('/food',methods=['GET','POST'])
def food():
    db = get_db()
    if request.method == 'POST':
        name = request.form['food-name']
        protein = int(request.form['protein'])
        carbohydrate = int(request.form['carbohydrate'])
        fat = int(request.form['fat'])
        calories = protein * 4 + carbohydrate * 4 + fat * 9
        db.execute('insert into food (name,protein,carbohydrate,fat,calories) values (?,?,?,?,?)',[name,protein,carbohydrate,fat,calories])
        db.commit()
    cur = db.execute('select name,protein,carbohydrate,fat,calories from food')
    results = cur.fetchall()
    return render_template('add_food.html',results=results)