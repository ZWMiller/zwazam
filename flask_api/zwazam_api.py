import flask
import numpy as np
import sys
import psycopg2 as pg
import os
from collections import defaultdict
sys.path.append("../src")
from binary_stream_fingerprint import BinaryStreamFingerprint
from stream_fingerprint import StreamFingerprint
from wav_fingerprint import WavFingerprint
from zwazam_settings import *
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'temp_file_storage/'
ALLOWED_EXTENSIONS = set(['wav'])

# Initialize the app

app = flask.Flask("zwazam")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

base_match_query = "SELECT track, count(hash) FROM zwazam WHERE hash = {} GROUP BY track"
base_insert_query = "INSERT INTO zwazam(track, hash) VALUES ('{}', {});"
connection_args = {
    'host': '', # You'll have to update this to your IP
    'user': 'zachariahmiller',    # username
    'dbname': 'zachariahmiller',   # DB that we are connecting to
}
connection = pg.connect(**connection_args)
cursor = connection.cursor()


@app.route("/")
def api_information():
    output = """
    Thanks for trying zwazam. To use, please use the 'match' endpoint with
    ip_address_of_api/match. This system expects JSON input with the wave form stored in
    a format:
    {
        'waveform': [1,95,83,47... rest, of, wave, form, data]
    }\n"""
    return output


@app.route("/match", methods=["POST"])
def match_provided_track():

    data = flask.request.json
    waveform = np.array(data["waveform"]).ravel()
    datatype = waveform.dtype
    new_track = None
    if datatype == 'B':
        new_track = BinaryStreamFingerprint(waveform, min_peak_amplitude=MIN_FINGER_PRINT_MIC)
    elif datatype == int or datatype == float:
        new_track = StreamFingerprint(waveform, min_peak_amplitude=MIN_FINGER_PRINT_WAV)
    else:
        print(api_information)

    best_match = compare_hashes(new_track.hashes)
    del waveform
    del data
    del new_track
    return flask.jsonify({"result": best_match})

@app.route("/add_track_to_database", methods=["POST"])
def add_track_to_database():
    data = flask.request.json
    waveform = np.array(data["waveform"]).reshape(-1,1)
    track_name = str(data['name'])
    new_track = StreamFingerprint(waveform, min_peak_amplitude=MIN_FINGER_PRINT_WAV)
    if new_track:
        for hash in set(new_track.hashes):
            cursor.execute(base_insert_query.format(str(track_name), int(hash)))
        cursor.execute("commit;")
    print("{} added to database".format(track_name))

def compare_hashes(hashes):
    match_counter = defaultdict(int)
    for hash in set(hashes):
        cursor.execute(base_match_query.format(int(hash)))
        for track_name, count in cursor.fetchall():
            match_counter[track_name] += count
    sorted_matches = sorted(match_counter.items(), key=lambda x: x[1], reverse=True)
    try:
        result = sorted_matches[0][0]
    except IndexError:
        result = "No track found"
    return result

@app.route('/wav_upload', methods=['POST'])
def upload_file():
    print("1")
    if flask.request.method == 'POST':
        print("2")
        # check if the post request has the file part
        if 'file' not in flask.request.files:
            return {"result": "Invalid File Type"}

        file = flask.request.files['file']
        print("YEAH ", allowed_file(file.filename))
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            print('NAH')
            return {"result": "Invalid File Type"}
        if file and allowed_file(file.filename):
            print("YEA")
            print(file.filename)
            filename = secure_filename(file.filename)
            path_to_file = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(path_to_file)
            new_track = WavFingerprint(path_to_file, peak_sensitivity=20,
                           min_peak_amplitude=40, look_forward_time=10)
            best_match = compare_hashes(new_track.hashes)
            del new_track
            os.remove(path_to_file)
            return flask.jsonify({"result": best_match})


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



# For local development:
app.run(debug=True)

# For public web serving:
# app.run(host='0.0.0.0')
