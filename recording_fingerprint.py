import numpy as np
from process_audio import ProcessAudio
import pyaudio


class RecordingFingerprint(ProcessAudio):

    def __init__(self,**kwargs):
        """
        Class that reads in sounds from the microphone and uses the ProcessAudio methods
        to clean and fingerprint the recorded sound. Computes hashes from the
        recorded channel. All major methodology inherited from ProcessAudio
        super class.

        Input:
        filename: location on disk of the file to be processed
        """
        read_data = self.record_from_microphone()
        self.raw_data = np.frombuffer(read_data, dtype='B')
        self.final_sample = self.raw_data.shape[0]
        super(RecordingFingerprint, self).__init__(**kwargs)

        if self.raw_data.any():
            self.process_track(self.raw_data)

    def record_from_microphone(self):
        """
        Using pyAudio, opens a channel to the microphone and records a
        5 second blurb. Extracts the raw audio waveform and sends that
        back to the processor for fingerprinting.
        Return:
        list of recorded amplitudes
        """
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 2
        RATE = 44100
        RECORD_SECONDS = 5

        p = pyaudio.PyAudio()

        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

        print("* recording")

        frames = []

        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)

        print("* done recording")

        stream.stop_stream()
        stream.close()
        p.terminate()

        return b''.join(frames)

if __name__ == "__main__":
    track = RecordingFingerprint(peak_sensitivity=10, min_peak_amplitude=None)
    spectrogram = track.make_spectrogram(track.raw_data)
    track._plot_spectrograms(spectrogram)
    #print(track.hashes)