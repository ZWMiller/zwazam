import numpy as np
from process_audio import ProcessAudio


class StreamFingerprint(ProcessAudio):

    def __init__(self,read_data, **kwargs):
        """
        Class that takes in an already recorded binary representation of the data
        and uses the ProcessAudio methods to clean and fingerprint the recorded sound.
        Computes hashes channel. All major methodology inherited from ProcessAudio
        super class.

        Input:
        read_data: array in binary format
        """
        self.raw_data = np.array(read_data)
        self.final_sample = self.raw_data.shape[0]
        super(StreamFingerprint, self).__init__(**kwargs)

        if self.raw_data.any():
            self.process_track(self.raw_data)


if __name__ == "__main__":
   pass