from matplotlib.mlab import specgram
import matplotlib.pyplot as plt
from scipy.io import wavfile
import scipy.ndimage as ndi
from scipy.ndimage.morphology import generate_binary_structure, binary_erosion
import numpy as np
from matplotlib.mlab import window_hanning
from process_audio import ProcessAudio


class WavFingerprint(ProcessAudio):



    def __init__(self, filename, **kwargs):
        """
        Class that reads in a wav file and uses the ProcessAudio methods
        to clean and fingerprint a given WAV. Loads the file, extracts left
        and right channels if available, then computes hashes from those
        channels individually. All major methodology inherited from ProcessAudio
        super class.

        Input:
        filename: location on disk of the file to be processed
        """
        self.__doc__ += ProcessAudio.__doc__
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
        if self.raw_data_right.any():
            self.process_track(self.raw_data_right)

if __name__ == "__main__":
    track = WavFingerprint("test_wav/Bust_This_Bust_That.wav", peak_sensitivity=20, min_peak_amplitude=40)
    #track.process_track(track.raw_data_left)
    #print(len(track.hashes))
    #print(len(set(track.hashes)))


    spectrogram = track.make_spectrogram(track.raw_data_left)
    track._plot_spectrograms(spectrogram)
    print(track.hashes)