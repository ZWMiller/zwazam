from matplotlib.mlab import specgram
import matplotlib.pyplot as plt
import scipy.ndimage as ndi
from scipy.ndimage.morphology import generate_binary_structure, binary_erosion
import numpy as np
from matplotlib.mlab import window_hanning


class ProcessAudio:

    def __init__(self, chunk_seconds=5., peak_sensitivity=20, look_forward_time=70, min_peak_amplitude=None):
        """
        Parent class for processing audio clips and extracting fingerprints via peaks
        in the spectrogram. This class does not accept input and should only be used
        as a parent class to port similar behavior across multiple file types. General
        behavior is to compute the spectrogram, find local peaks via neighborhood searches,
        erode backgrounds to make those peaks distinct, then calculate hash values that encode
        the relative time and frequency differences between peaks in the spectrogram within
        some time window. Also has the capability of breaking a single file into n-second chunks
        if necessary.

        Input:
        chunk_seconds: how many seconds each chunk will be if chunks are requested
        peak_sensitivity: A tunable parameter to decide how large the neighborhood should be
        when searching for peaks. Larger = fewer but more distinct peaks
        look_forward_time: Size of time window when considering what peaks are "close" enough
        to create hashes
        min_peak_amplitude: A filter to remove small peaks. Larger value makes fewer peaks,
        but may lower accuracy by removing useful peaks.
        """
        self.chunk_seconds = chunk_seconds
        self.peak_sensitivity = int(peak_sensitivity)
        self.look_forward_time = look_forward_time
        self.min_peak_amplitude = min_peak_amplitude
        self.hashes = None

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
        spectrogram, _, _ = specgram(data_chunk, NFFT=4096, Fs=44100, noverlap=2048, window=window_hanning)
        spectrogram = 10. * np.log10(spectrogram+1e-6)
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

        if self.min_peak_amplitude:
            filtered_peak_locations = self.filter_peaks_by_size(detected_peaks, spectrogram)
        else:
            filtered_peak_locations = detected_peaks

        return filtered_peak_locations

    def process_track(self, track_data):
        """
        A process controller that will take given track data and compute all of the
        relevant hashes.
        Input:
        track_data: Array of floats consisting of the amplitude at a given time.
        """
        spectrogram = self.make_spectrogram(track_data)
        peak_map = self.detect_peaks(spectrogram)
        partner_peaks_map = self.find_partner_peaks(peak_map)
        list_of_hashes = self.create_hashes(partner_peaks_map)
        self.hashes = list_of_hashes

    def filter_peaks_by_size(self, peak_map, spectrogram):
        """
        Takes in the spectrogram and the locations of all peaks, then decides whether the peak
        in the spectrogram is tall enough to pass through the requested noise filter.
        Inputs:
        peak_map: Matrix of 0's (non peak) and 1's (peaks)
        spectrogram: Matrix of amplitudes in time and frequency space

        Returns:
        Matrix of 0's (non peak) and 1's (peaks), but with small peaks removed based on an
        amplitude filter
        """

        # TO DO: Refactor to use broadcasting. Needs thought on process.
        peak_locations = self.get_peak_locations(peak_map)
        filtered_peaks = np.zeros_like(peak_map)
        for peak in peak_locations:
            if spectrogram[peak[0],peak[1]] > self.min_peak_amplitude:
                filtered_peaks[peak[0],peak[1]] = 1
        return filtered_peaks

    def create_hashes(self, partner_peaks_map):
        """
        Given dictionary in the form {peak: [list, of, associated, peaks]}, computes
        the relationship between these peaks and encodes it into a single long integer
        hash that can be stored with low overhead.
        Inputs:
        partner_peaks_map: Dictionary of the form {peak: [list, of, associated, peaks]},
        Return:
        list of all hashes for the processed track
        """
        list_of_hashes = []
        for peak, partners in partner_peaks_map.items():
            for partner in partners:
                x_difference = partner[0] - peak[0]
                y_difference = partner[1] - peak[1]
                hash = self.hash_function(x_difference, y_difference)
                list_of_hashes.append(hash)
        return list_of_hashes

    def hash_function(self, x_difference, y_difference):
        """
        Uses the time difference and frequency difference between two peaks to compute a
        "unique" hash for each time, frequency difference.
        Inputs:
        x_difference: float that specifies the time difference between peaks
        y_difference: float that specifies the freq difference between peaks
        Return:
        long int hash to specify the relationship between two peaks
        """
        return (x_difference * 0x1f1f1f1f) ^ y_difference

    def get_peak_locations(self, peak_map):
        """
        Given a matrix of 0's and 1's, finds the coordinates in the matrix of all
        1's and returns them in the format [(x0,y0,z0), (x1,y1,z1)...]
        peak_map: Matrix of 0's (non peak) and 1's (peaks)
        Return:
        array of peak coordinates, 1 row per peak
        """
        return np.argwhere(peak_map == 1)

    def find_partner_peaks(self, peak_map):
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
        peak_locations = self.get_peak_locations(peak_map)
        for peak in peak_locations:
            time_max_value = peak[0] + self.look_forward_time
            time_min_value = peak[0]
            time_condition = (peak_locations[:,0] > time_min_value) & (peak_locations[:,0] < time_max_value)
            found_peaks = peak_locations[time_condition]
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
        plt.show()