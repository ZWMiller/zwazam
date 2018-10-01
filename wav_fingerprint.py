from matplotlib.mlab import specgram
import matplotlib.pyplot as plt
from scipy.io import wavfile
import scipy.ndimage as ndi
from scipy.ndimage.morphology import generate_binary_structure, binary_erosion
import numpy as np


class WavFingerprint:

    def __init__(self, filename, chunk_seconds=5., peak_sensitivity=20, look_forward_time=20,
                 frequency_window_range=10, min_peak_amplitude=None):
        self.sample_rate, read_data = wavfile.read(filename)
        self.raw_data = np.array(read_data)
        self.chunk_seconds = chunk_seconds
        self.final_sample = self.raw_data.shape[0]
        self.peak_sensitivity = int(peak_sensitivity)
        self.look_forward_time = look_forward_time
        self.frequency_window = frequency_window_range
        self.min_peak_amplitude = min_peak_amplitude

        try:
            self.raw_data_left = self.raw_data[:, 0]
            self.raw_data_right = self.raw_data[:, 1]
        except IndexError:
            self.raw_data_left = self.raw_data
            self.raw_data_right = None

    def _generate_chunks_of_wav(self, raw_data):
        """
        Method to chunk the data into a series of n-second chunks and
        act as a generator to return each chunk of data. Chunk length
        set by the chunk_seconds attribute provided by the user.

        Yields a new n-second chunk of data each time.
        """
        samples_per_chunk = int(self.sample_rate * self.chunk_seconds)
        current_chunk_min = 0
        current_chunk_max = 0
        while current_chunk_min < self.final_sample:
            current_chunk_min = current_chunk_max
            current_chunk_max += samples_per_chunk
            yield raw_data[current_chunk_min:current_chunk_max]

    def fft(self, data):
        """
        Computes the fourier transform of the provided data

        Input: array (1D time series)
        Output: Fourier Transform (Array)
        """
        dfft = abs(np.fft.rfft(data))
        dfft = 10 * np.log10(dfft)
        return dfft

    def make_spectrogram(self, data_chunk):
        """
        Given a datachunk, create a spectrogram of the data. This spectrogram
        can then be used with the detect_peaks method to create a fingerprint
        Input:
        data_chunk: array of 1D time series data
        Return:
        Spectrogram (Matrix object) time on x axis, frequency on y axis
        """
        spectrogram, _, _ = specgram(data_chunk, NFFT=1024, Fs=2, noverlap=900)
        spectrogram = 10. * np.log10(spectrogram)
        return spectrogram

    def detect_peaks(self, spectrogram):
        """
        Takes an image of the spectrogram and detect the peaks using the local
        maximum filter.

        Input:
        spectrogram: a matrix of time-frequency strengths from matplotlibs specgram
        method.
        peak_sensitivity: How large of a neighborhood structure to consider when
        looking for peaks
        Returns a boolean mask of the peaks (i.e. 1 when
        the pixel's value is the neighborhood maximum, 0 otherwise)
        """

        # define a connected neighborhood and find max values in neighborhood
        neighborhood_structure = generate_binary_structure(2, 1)
        neighborhood = ndi.iterate_structure(neighborhood_structure, self.peak_sensitivity)
        local_max = ndi.filters.maximum_filter(spectrogram, footprint=neighborhood) == spectrogram

        background = (spectrogram == 0)
        eroded_background = binary_erosion(background, structure=neighborhood, border_value=1)

        detected_peaks = local_max != eroded_background
        return detected_peaks

    def process_track(self, track_data):
        #for chunk in self._generate_chunks_of_wav(track_data):
        #    self.hashes += self.process_chunk(chunk)
        spectrogram = self.make_spectrogram(track_data)
        peak_map = self.detect_peaks(spectrogram)
        peak_locations = self.get_peak_locations(peak_map)
        if self.min_peak_amplitude:
            filtered_peak_locations = self.filter_peaks_by_size(peak_locations, spectrogram)
        else:
            filtered_peak_locations = peak_locations
        partner_peaks_map = self.find_partner_peaks(filtered_peak_locations)
        list_of_hashes = self.create_hashes(partner_peaks_map)
        self.hashes = list_of_hashes


    def process_chunk(self, data_chunk):
        spectrogram = self.make_spectrogram(data_chunk)
        peak_map = self.detect_peaks(spectrogram)
        peak_locations = self.get_peak_locations(peak_map)
        if self.min_peak_amplitude:
            filtered_peak_locations = self.filter_peaks_by_size(peak_locations, spectrogram)
        else:
            filtered_peak_locations = peak_locations
        partner_peaks_map = self.find_partner_peaks(filtered_peak_locations)
        list_of_hashes = self.create_hashes(partner_peaks_map)
        return list_of_hashes

    def filter_peaks_by_size(self, peak_locations, spectrogram):

        # TO DO: Refactor to use broadcasting. Needs thought on process.
        filtered_peaks = []
        for peak in peak_locations:
            if 10**spectrogram[peak[0],peak[1]] > self.min_peak_amplitude:
                filtered_peaks.append(peak)
        return np.array(filtered_peaks)

    def create_hashes(self, partner_peaks_map):

        list_of_hashes = []
        for peak, partners in partner_peaks_map.items():
            for partner in partners:
                x_difference = partner[0] - peak[0]
                y_difference = partner[1] - peak[1]
                hash = self.hash_function(x_difference, y_difference)
                list_of_hashes.append(hash)
        return list_of_hashes

    def get_peak_locations(self, peak_map):
        return np.argwhere(peak_map == 1)

    def hash_function(self, x_difference, y_difference):
        #return (x_difference * 0x1f1f1f1f) ^ y_difference
        return (x_difference, y_difference)

    def find_partner_peaks(self, peak_locations):
        """
        Takes in a peak map and draws up relationships between peaks in a certain window
        of time and frequency. Time is always looking forward from each peak to the next ones,
        frequency creates a window on either side of the peak to search for other peaks.

        Inputs:
        peak_map: a matrix of boolean cells, 1's for peaks, 0's for non peaks
        time_forward: How far forward to look for the next peaks
        frequency_range: how far above and below the frequency of the current peak
        to look for other peaks that could create a connection
        Returns:
        dictionary of format {peak: [partner peaks]}
        """
        partner_peak_map = {}
        for peak in peak_locations:
            time_max_value = peak[0] + self.look_forward_time
            time_min_value = peak[0]
            freq_max_value = peak[1] + self.frequency_window
            freq_min_value = peak[1] - self.frequency_window
            time_condition = (peak_locations[:,0] > time_min_value) & (peak_locations[:,0] < time_max_value)
            found_peaks = peak_locations[time_condition]
            frequency_condition = (found_peaks[:, 1] > freq_min_value) & (found_peaks[:, 1] < freq_max_value)
            found_peaks = found_peaks[frequency_condition]
            list_of_partners = found_peaks.tolist()
            if list_of_partners:
                partner_peak_map[tuple(peak)] = list_of_partners
        return partner_peak_map

    def _plot_spectrograms(self, spectrogram):
        """
        Diagnostic method that plots the spectrogram and the
        peaks found from that spectrogram.

        Input:
        spectrogram: numpy matrix of time-frequency strength
        """
        fig, axes = plt.subplots(2,1, dpi=150)

        axes[0].imshow(spectrogram[::-1])
        axes[1].imshow(self.detect_peaks(spectrogram)[::-1])
        axes[0].set_aspect('equal', adjustable='box')
        axes[1].set_aspect('equal', adjustable='box')
        axes[0].set_title("Left Channel Spectrogram")
        axes[1].set_title("Identified Peaks")
        plt.xlabel("Time (samples)")
        plt.ylabel("Frequency")
        axes[0].set_ylabel("Frequency")
        plt.tight_layout()
        print("Done")
        plt.show()

if __name__ == "__main__":
    track = WavFingerprint("test_wav/test_v1.wav", peak_sensitivity=20)
    track.process_track(track.raw_data_left)
    print(len(track.hashes))
    print(len(set(track.hashes)))


    #spectrogram = track.make_spectrogram(section)
    #track._plot_spectrograms(spectrogram)
    #print(track.process_chunk(section))