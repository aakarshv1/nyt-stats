from flask import Flask, render_template, request, redirect
import subprocess
import logging
import numpy as np
import ast
from getStats import getSolveTimes
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('nytlogin.html')

@app.route('/mini-stats', methods=['POST'])
def submit_form():
    if request.method == 'POST':
    # Extract the username and password from the form submission
        username = request.form['email']
        password = request.form['password']
        cookie = request.form['cookie']  # Retrieve the NYT-S cookie from the form

        

        try:
            if cookie:  # If the NYT-S cookie is provided, use it instead of username and password
                output = getSolveTimes(key=cookie)
            else:  # If the NYT-S cookie is not provided, use the username and password
                output = getSolveTimes(username, password)
            app.logger.setLevel(logging.DEBUG)
            app.logger.addHandler(logging.StreamHandler())
            
            app.logger.debug(request.form)
            app.logger.debug(output)

            data = output #ast.literal_eval(output)
            app.logger.info(f'Output: {type(data)}, elem: {type(data[0])}')

            mean = np.mean(data).round(2)
            median = np.median(data)
            maxVal = max(data)
            minVal = min(data)

            bins = list(range(min(data), max(data), 3))

            counts = []

            for i in range(len(bins) - 1):
                count = 0
                for value in data:
                    if value >= bins[i] and value < bins[i+1]:
                        count += 1
                counts.append(count)

            total = sum(counts)
            freqs = [x/total for x in counts]

            # Render a new template with the data and statistics
            return render_template('miniresults.html', data=data , bins=bins, counts=counts, mean=mean, median=median, min=minVal, max=maxVal, freqs=freqs)

        except requests.exceptions.HTTPError as r:
            # Handle incorrect login information
            error_message = f"Invalid credentials, please ensure your username and password are correct. Alternatively, you may have exceeded the number of allowed logins. If so, \
            please login with your NYT-S cookie instead."
            return render_template('nytlogin.html', error_message=error_message)

    return redirect('/')

# @app.route('/about')
# def about():
#     return render_template('about.html')

if __name__ == '__main__':
    app.run()
