from flask import Flask, flash, render_template, session, request, redirect
import sqlite3
app = Flask(__name__)
app.debug = True
app.secret_key = 'secretKeyshh'

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/showAll")
def showAll():
    limit = 100 # this will be used to put a limit on the amount shown
    # if the session data exists get the info from the session that’s set
    if session.get("limit"):
        limit = session["limit"]
        query = "select * from shippedAmounts where platform not LIKE 'Multi' LIMIT (?)"
        con = sqlite3.connect("games.db")
        con.row_factory = sqlite3.Row
        curs = con.cursor()
        curs.execute(query, (limit,))
        rows = curs.fetchall()
        return render_template("results.html", results = rows)
    else:
        return render_template("results.html", results = [])

@app.route("/showAll<sortby>")
def sort(sortby):
    limit = 100
    if session.get("limit"):
        limit = session["limit"]
        if sortby == "NameAsc":
            query = "select * from shippedAmounts where platform not LIKE 'Multi' ORDER BY Name ASC LIMIT (?)"
        elif sortby == "NameDesc":
            query = "select * from shippedAmounts where platform not LIKE 'Multi' ORDER BY Name DESC LIMIT (?)"
        elif sortby == "DateAsc":
            query = "select * from shippedAmounts where platform not LIKE 'Multi' ORDER BY Date ASC LIMIT (?)"
        elif sortby == "DateDesc":
            query = "select * from shippedAmounts where platform not LIKE 'Multi' ORDER BY Date DESC LIMIT (?)"
        else:
            query = "select * from shippedAmounts where platform not LIKE 'Multi' LIMIT (?)"
        con = sqlite3.connect("games.db")
        con.row_factory = sqlite3.Row
        curs = con.cursor()
        curs.execute(query,(limit,))
        rows = curs.fetchall()
        return render_template("results.html", results = rows)
    
@app.route("/filter")
def filters():
    if request.method == "GET":
        limit = 100
        if session.get("limit"):
            limit = session["limit"]
        query ="select distinct platform from shippedAmounts"
        con = sqlite3.connect("games.db")
        con.row_factory = lambda cursor, row: row[0]
        curs = con.cursor()
        curs.execute(query)
        platforms = curs.fetchall()
        rows = []
        if session.get("platform"):
            query = "select * from shippedAmounts where platform LIKE (?) LIMIT (?)"
            con.row_factory = sqlite3.Row
            curs = con.cursor()
            curs.execute(query, (session.get("platform"), limit))
            rows = curs.fetchall()
        return render_template("filtered.html", platform = platforms, results = rows)

@app.route('/filter', methods = ['POST'])
def filter_post():
    if request.method == 'POST':
        session['platform'] = request.form['platform']
        return redirect(request.referrer)

@app.route('/limit', methods = ['POST'])
def setLimit():
    if request.method == 'POST':
        session['limit'] = request.form['limit']
        return redirect(request.referrer)

@app.route("/graphs")
def graphs():
    query = "select distinct platform from shippedAmounts"
    con = sqlite3.connect("games.db")
    con.row_factory = lambda cursor, row: row[0]
    curs = con.cursor()
    curs.execute(query)
    platforms = curs.fetchall()
    con.row_factory = sqlite3.Row
    curs = con.cursor()
    if session.get("platform"):
        query = "SELECT distinct name, shipped from shippedAmounts where platform like (?) order by shipped DESC Limit 10"
        curs.execute(query, (session.get("platform"),))
        rows = curs.fetchall()
    else:
        query = "select distinct name, shipped from shippedAmounts order by shipped DESC Limit 10"
        curs.execute(query)
        rows = curs.fetchall()
    labels = []
    values = []
    for r in rows:
        labels.append(r["name"])
        values.append(r["shipped"])
    return render_template("graph.html", platform = platforms, labels = labels, values = values)

app.run()