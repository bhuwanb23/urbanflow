from flask import Flask, jsonify, request, render_template, redirect, url_for
import pandas as pd
from path_finder.shortest_path import main  # Import your shortest path function

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')  # Renders the home page template

@app.route('/route')
def route():
    return render_template('route.html')  # Renders the route page template

@app.route('/profile')
def profile():
    return render_template('profile.html')  # Renders the profile page template

@app.route('/login')
def login():
    return render_template('login.html')  # Renders the login page template

@app.route('/search', methods=['POST'])
def search():
    start = request.form.get('start')  # Retrieve the 'start' input value from the form
    destination = request.form.get('destination')  # Retrieve the 'destination' input value from the form
    search_time = "8:00 AM"  # Hardcoded search time, can be adjusted as needed

    if not start or not destination:
        return redirect(url_for('home', error='Missing input values'))

    available_routes, detailed_options, output = main(start, destination, search_time)

    return render_template(
        'route.html',
        start=start,
        destination=destination,
        available_routes=available_routes,
        detailed_options=detailed_options,
        output=output  # Pass the captured output to the template
    )

if __name__ == '__main__':
    app.run(debug=True)
