"""
    @author Zhida Li
    @email zhidal@sfu.ca
    @date Feb. 19, 2022
    @version: 1.1.0
    @description:
                This is the main file used to start the bgpGuard.

    @copyright Copyright (c) Feb. 19, 2022
        All Rights Reserved

    This Python code (versions 3.6 and newer)
"""

# ==============================================
# main file: app.py
# ==============================================
# Last modified: Sept. 27, 2023
# task: added custom dataset option for offline classification

# Import the built-in libraries
import os
import sys
import time
import zipfile
import glob

# Import external libraries
import numpy as np
from flask import Flask, render_template, url_for, request, send_file, abort
from flask_socketio import SocketIO, emit, disconnect
from werkzeug.utils import secure_filename

# Import customized libraries
from app_realtime import app_realtime_detection
from app_offline import app_offline_classification
from config import flask_config
from config import flask_folder
from src.time_tracker import are_dates_valid

# print(__doc__)

# Load Flask configuration
async_mode, app, socketio, thread, thread_lock = flask_config()
flask_folder()

# Headers (html)
header_realTime = "Real-Time BGP Anomaly Detection"
header_offLine = "Off-Line BGP Anomaly Classification"
ALLOWED_EXTENSIONS = {'csv'}  # for custom dataset


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


"""
## Establish routes
"""


# Home index (route)
@app.route('/')
def index():
    return render_template('index.html')


# Real-Time Detection (route)
@app.route('/bgp_ad_realtime')
def bgp_ad_realtime():
    return render_template('bgp_ad_realtime.html', header1=header_realTime,
                           async_mode=socketio.async_mode)


# Off-Line Classification (route)
@app.route('/bgp_ad_offline')
def bgp_ad_offline():
    return render_template('bgp_ad_offline.html', header2=header_offLine)


# Received parameters for the off-Line experiment (route)
@app.route('/bgp_ad_offline', methods=['POST'])
def analyze_offline():
    print('Dict. params. received from the front-end: \n', request.form)  # check if receive keys (name) from front-end

    if request.form.get('site_choice') == 'custom':
        # Handle the uploaded file
        if 'customFile' not in request.files or request.files['customFile'].filename == '':
            # We might want to send a more user-friendly response
            return 'No file uploaded', 400  # Bad Request

        model_params = {
            'site_choice',
            'cut_pct_key',
            'algo_key',
            'rnn_seq_key'
        }

        file = request.files['customFile']
        print('Received file:', file.filename)  # Debugging line

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            print('Saving to:', filepath)  # Debugging line
            file.save(filepath)

            # Read the uploaded CSV into a DataFrame
            data_upload = np.loadtxt(filepath, delimiter=',')
            print(data_upload)  # Display the data in the console

            # Here, we can further process the data as needed...
            # Information from back-end to front-end, "Results are available" (developing)
            context_offLine = {'site_selected': "Results are ready to download!",
                               'header2': header_offLine}
            return render_template('bgp_ad_offline.html', **context_offLine)
        else:
            return "File not allowed", 400

    # If not processing an uploaded file, then run the existing code
    else:
        model_params = {
            'site_choice',
            'start_date_key', 'end_date_key',
            'start_date_anomaly_key', 'end_date_anomaly_key',
            'start_time_anomaly_key', 'end_time_anomaly_key',
            'cut_pct_key',
            'algo_key',
            'rnn_seq_key'
        }

        # Ensure all parameters are received for non-custom datasets
        if set(request.form.keys()) != model_params:
            return "Missing parameters", 400
            # return render_template('bgp_ad_offline.html', header2=header_offLine)

        print("\n Server checked: Parameter received from the client :-) \n")

        site = request.form.get('site_choice')  # or use 'request.form['']' due to dict format
        site = 'RIPE' if site == 'ripe' else 'RouteViews'
        start_date = request.form.get('start_date_key')
        end_date = request.form.get('end_date_key')
        start_date_anomaly = request.form.get('start_date_anomaly_key')
        end_date_anomaly = request.form.get('end_date_anomaly_key')
        start_time_anomaly = request.form.get('start_time_anomaly_key')
        end_time_anomaly = request.form.get('end_time_anomaly_key')
        cut_pct = request.form.get('cut_pct_key')
        ALGO = request.form.get('algo_key')
        rnn_seq = request.form.get('rnn_seq_key')

        input_exp_key = [site, start_date, end_date, start_date_anomaly, end_date_anomaly,
                         start_time_anomaly, end_time_anomaly, cut_pct, ALGO, rnn_seq]

        # Check if the dates are valid
        if not are_dates_valid(start_date, start_date_anomaly, end_date_anomaly, end_date,
                               start_time_anomaly, end_time_anomaly):
            return "Please re-enter the date/time", 400
        # Pass the parameters (list) to the off-line classification
        context_offLine = app_offline_classification(header_offLine, input_exp_key)

        time.sleep(5)  # to be changed
        print("--------------------Saving Results-begin--------------------------")
        # if not os.path.exists('./src/STAT/results.zip'):
        # zip results
        zipObj = zipfile.ZipFile('./src/STAT/results.zip', 'w')
        zipObj.write('./src/STAT/train_test_stat.txt')
        # Use glob find the csv file with prefix "labels_"
        for file in glob.glob('./src/STAT/labels_*.csv'):
            zipObj.write(file)  # RIPE or Route Views
        for file in glob.glob('./src/STAT/results_*.csv'):
            zipObj.write(file)  # (* = cut_pct, site)
        # zipObj.write('./src/STAT/labels_*.csv')
        # zipObj.write('./src/STAT/results_*.csv')

        # zipObj = zipfile.ZipFile('./src/STAT/sample.zip', 'w')  # for test Download function
        # zipObj.write('./src/STAT/train_test_stat.txt')  # for test Download function
        # zipObj.write('./src/STAT/labels_RIPE.csv')  # for test Download function
        # zipObj.write('./src/STAT/results_64_RIPE.csv')  # for test Download function
        zipObj.close()
        print("--------------------Saving Results-end--------------------------")

        return render_template('bgp_ad_offline.html', **context_offLine)
        # return render_template('bgp_ad_offline.html', result_prediction=result_prediction)


# Off-Line Download GET request
@app.route('/download_file', methods=['GET'])
def download_file():
    try:
        return send_file('./src/STAT/results.zip',
                         mimetype='application/zip',  # text/csv
                         download_name='Results_%s.zip' % time.strftime('%b_%d_%Y_%H_%M_%S', time.localtime()),
                         as_attachment=True)
    except FileNotFoundError:
        abort(404)


# Contact (route)
@app.route('/contact')
def contact():
    return render_template('contact.html')


# WebSocket for Real-Time Detection  -begin
@socketio.on('main_event', namespace='/test_conn')
def test_connect(message):
    mem = message.get('selected_option1')  # Get the selected option from the message
    ALGO = message.get('selected_option2')
    num_features = message.get('selected_option3')
    print("Received feature option: ", mem)
    print("Received algorithm option: ", ALGO)
    print("Received no. of features option: ", num_features)
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(app_realtime_thread, mem, ALGO, num_features)


def app_realtime_thread(mem, ALGO, num_features):
    print("Running thread with feature option: ", mem)
    print("Running thread with algorithm option: ", ALGO)
    print("Running thread with no. of features option: ", num_features)
    if mem is None:
        mem = 'low'  # default memory
    if ALGO is None:
        ALGO = 'VFBLS'  # default algorithm
    if num_features is None:
        num_features = 'all'  # default no. of features

    count = 0  # count the number of received update messages
    site = 'RIPE'
    if site == 'RIPE':
        time_interval = 5 * 60  # RIPE provides new update msg every 5 minutes
    elif site == 'RouteViews':
        time_interval = 15 * 60  # Route Views provides new update msg every 15 minutes

    num_reg, num_ano = 0, 0
    results_total_time = 0
    while True:
        # if second = 5, wait 1 min until RIPE or Route Views do update
        if int(time.strftime('%M', time.localtime())) % 5 == 0:
            time.sleep(60)

        # start processing...
        time_start = time.time()

        # === Load the data for the front-end (real-time) ===
        web_results, t_utc, t_ann, data_for_plot_ann, data_for_plot_wdrl, count, predicted_labels, \
            t_cpu, cpus = app_realtime_detection(ALGO, num_features, site, mem, count)

        # Show results
        # Emit uct date & time, predicted labels of 5min
        socketio.emit('server_response_text',
                      {'data_results': [web_results[0], web_results[1], web_results[2], web_results[3], web_results[4]],
                       'data_t': [t_utc]}, namespace='/test_conn')
        socketio.sleep(0.5)

        # Pie-chart
        # Emit no. of total regular and anomaly points, total time spent
        for regAno in predicted_labels:
            if regAno == 1:
                num_ano += 1
            else:
                num_reg += 1
        results_total_time += len(predicted_labels)

        socketio.emit('server_response_echart_pie',
                      {'data_pie': [num_reg, num_ano, results_total_time]}, namespace='/test_conn')

        # Label-chart
        # Emit labels, uct time
        socketio.emit('server_response_echart0',
                      {'data_labels': [t_ann, predicted_labels]},
                      namespace='/test_conn')
        socketio.sleep(0.5)

        # Feature-chart
        # Emit features, uct time
        socketio.emit('server_response_echart2',
                      {'data_features': [t_ann, data_for_plot_ann, data_for_plot_wdrl], 'count': count},
                      namespace='/test_conn')

        # CPU-chart
        # Emit multi-core cpu usage, uct time
        socketio.emit('server_response_echart_cpu',
                      {'data_cpu': [t_cpu, cpus], 'count': count},
                      namespace='/test_conn')

        # completed processing...
        time_end = time.time()

        # Subtract the processing time
        time_realTime_server = time_end - time_start
        print('Entire processing time: %.4f s' % time_realTime_server,
              '\nCurrent time:', time.strftime('%H:%M:%S', time.localtime()))
        t_sleep = time_interval - time_realTime_server
        if t_sleep <= 0:  # if processing time is longer than waiting time
            continue
        time.sleep(t_sleep)


# Trigger disconnection of the real-time detection
@socketio.on('disconnect_request', namespace='/test_conn')
def disconnect_request():
    # @copy_current_request_context
    def can_disconnect():
        disconnect()

    emit('disconnect_response', {'data': 'Disconnected!'}, callback=can_disconnect)


@socketio.on('disconnect', namespace='/test_conn')
def test_disconnect():
    print('Client disconnected', request.sid)


# WebSocket for Real-Time Detection  -end


# Data Clustering GET (route)
@app.route('/data_clustering', methods=['GET'])
def get_data_clustering():
    return render_template('data_clustering.html', header2="Data Clustering")


# # Data Clustering POST (route)
@app.route('/data_clustering', methods=['POST'])
def post_data_clustering():
    print('Dict. params. received from the front-end: \n', request.form)  # check if receive keys (name) from front-end
    return render_template('data_clustering.html', header2=str(request.form))


"""
## Launch app
"""
if __name__ == '__main__':
    socketio.run(app, debug=True)

    # Sometimes Flask notices the build/run process creates files and restarts itself.  If that
    # hapens use the following instead of the "debug" version above.
    # socketio.run(app, use_reloader=False)

"""
use of app.run vs. socketio.run :

https://github.com/miguelgrinberg/Flask-SocketIO/issues/1273
Flask-SocketIO needs a web server. There are a few that you can use:
The Gevent web server, started via socketio.run()
The eventlet web server, also started via socketio.run()
The Flask dev web server, which can be started either via app.run() or for convenience also via socketio.run()
The Gunicorn web server with the eventlet or gevent workers, started via the gunicorn command.
The uwsgi web server with gevent, started via the uwsgi command.
"""
