import psycopg2 as pg
from wav_fingerprint import WavFingerprint
import sys
from collections import defaultdict
from zwazam_settings import *

DEBUG = True

def connect_to_sql():
    connection_args = {
        'host': '', # You'll have to update this to your IP
        'user': 'zachariahmiller',    # username
        'dbname': 'zachariahmiller',   # DB that we are connecting to
    }
    connection = pg.connect(**connection_args)
    return connection.cursor()


def print_help_message():
    print("Usage:")
    print("python match_wav.py path_to_wav_file_directory")
    exit(0)


def match_file(file_path):
    cursor = connect_to_sql()
    match_counter = defaultdict(int)
    base_match_query = "SELECT track, count(hash) FROM zwazam WHERE hash = {} GROUP BY track"

    new_track = WavFingerprint(file_path, min_peak_amplitude=MIN_FINGER_PRINT_WAV)
    for hash in set(new_track.hashes):
        cursor.execute(base_match_query.format(int(hash)))
        for track_name, count in cursor.fetchall():
            match_counter[track_name] += count
    sorted_matches = sorted(match_counter.items(), key=lambda x: x[1], reverse=True)
    if DEBUG:
        return sorted_matches
    else:
        return sorted_matches[0][0]


def parse_args(user_arguments):
    if len(user_arguments) > 2:
        raise IndexError("Must provide location of one wav file. -h' for help.")
    if user_arguments[1] == "-h":
        print_help_message()
    elif type(user_arguments[1]) == str:
        print(match_file(user_arguments[1]))
    else:
        print_help_message()


if __name__ == "__main__":
    requested_action = parse_args(sys.argv)