import psycopg2 as pg
from wav_fingerprint import WavFingerprint
from glob import glob
import sys


def connect_to_sql():
    connection_args = {
        'host': '', # You'll have to update this to your IP
        'user': 'zachariahmiller',    # username
        'dbname': 'zachariahmiller',   # DB that we are connecting to
    }
    connection = pg.connect(**connection_args)
    return connection.cursor()


def process_batch_files(path):
    cursor = connect_to_sql()
    base_insert_query = "INSERT INTO zwazam(track, hash) VALUES ('{}', {});"
    if path[-1] == "/":
        path = path[:-1]

    for file in glob("{}/*.wav".format(path)):
        print("Working on File", file)
        track = WavFingerprint(file, min_peak_amplitude=50)
        track.process_track(track.raw_data_left)
        track_name = file.split(('/'))[-1]
        for hash in set(track.hashes):
            cursor.execute(base_insert_query.format(str(track_name), int(hash)))
    cursor.execute("commit;")
    return None


def print_help_message():
    print("Usage:")
    print("python fingerprint_directory_of_files.py path_to_wav_file_directory")
    exit(0)


def parse_args(user_arguments):
    if len(user_arguments) > 2:
        raise IndexError("Must provide location for files. -h' for help.")
    if user_arguments[1] == "-h":
        print_help_message()
    elif type(user_arguments[1]) == str:
        process_batch_files(user_arguments[1])
    else:
        print_help_message()


if __name__ == "__main__":
    requested_action = parse_args(sys.argv)