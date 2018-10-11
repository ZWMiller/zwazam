from scipy.io import wavfile
import numpy as np
from process_audio_test_method import ProcessAudioTest


class WavFingerprint(ProcessAudioTest):

    def __init__(self, filename, **kwargs):
        """
        Class that reads in a wav file and uses the ProcessAudio methods
        to clean and fingerprint a given WAV. Loads the file, extracts left
        and right channels if available, then computes hashes from those
        channels individually. All major methodology inherited from ProcessAudioTest
        super class.

        Input:
        filename: location on disk of the file to be processed
        """
        self.sample_rate, read_data = wavfile.read(filename)
        self.raw_data = np.array(read_data)
        self.final_sample = self.raw_data.shape[0]
        super(WavFingerprint, self).__init__(**kwargs)

        try:
            self.raw_data_left = self.raw_data[:, 0]
            self.raw_data_right = self.raw_data[:, 1]
        except IndexError:
            self.raw_data_left = self.raw_data
            self.raw_data_right = None

        if self.raw_data_left.any():
            self.process_track(self.raw_data_left)

if __name__ == "__main__":
    track = WavFingerprint("../test_wav/samples_for_test/Bust_This_subsection.wav", peak_sensitivity=20,
                           min_peak_amplitude=40, look_forward_time=10)
    #track.process_track(track.raw_data_left)
    #print(len(track.hashes))
    #print(len(set(track.hashes)))


    spectrogram = track.make_spectrogram(track.raw_data_left)
    track._plot_spectrograms(spectrogram)
    print(track.hashes)