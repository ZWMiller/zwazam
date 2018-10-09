from wav_fingerprint import WavFingerprint

track1 = WavFingerprint('test_wav/Bust_This_Bust_That.wav', min_peak_amplitude=50)
track2 = WavFingerprint('test_wav/I_Want_To_Destroy_Something_Beautiful.wav', min_peak_amplitude=50)

print("Trying Track 1")
track1.process_track(track1.raw_data_left)
print("Trying Track 2")
track2.process_track(track2.raw_data_left)

# track1._plot_spectrograms(track1.make_spectrogram(track1.raw_data_left))
# track2._plot_spectrograms(track2.make_spectrogram(track2.raw_data_left))

print("Trying Test")
test_track = WavFingerprint('test_wav/Bust_This_Bust_That.wav', min_peak_amplitude=50)
data_chunk = test_track._generate_chunks_of_wav(test_track.raw_data_left)
for ix, chunk in enumerate(data_chunk):
    section = chunk
    if ix > 8:
        break
test_track.process_track(section)

def test_hash_matches(hash_list_1, hash_list_2):
    counter = 0
    for hash in hash_list_1:
        if hash in hash_list_2:
            counter += 1
    return counter

print("---\nMatches with Track 1: ", test_hash_matches(test_track.hashes,track1.hashes))
print("Matches with Track 2: ", test_hash_matches(test_track.hashes,track2.hashes))


# print(test_track.hashes)
# print("---")
# print(set(track1.hashes))
# print("---")
# print(set(track2.hashes))
