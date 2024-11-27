from flask import Flask, jsonify, request, render_template, redirect, url_for
import pandas as pd
from path_finder.shortest_path import main  # Import your shortest path function

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/route')
def route():
    return render_template('route.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/search', methods=['POST'])
def search():
    start = request.form.get('start')
    destination = request.form.get('destination')
    search_time = "8:00 AM"

    if not start or not destination:
        return redirect(url_for('home', error='Missing input values'))

    available_routes, detailed_options, output = main(start, destination, search_time)

    return render_template(
        'route.html',
        start=start,
        destination=destination,
        available_routes=available_routes,
        detailed_options=detailed_options,
        output=output
    )

if __name__ == '__main__':
    app.run(debug=True)
