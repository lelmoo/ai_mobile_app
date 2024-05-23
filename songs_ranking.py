import librosa
import numpy as np
from scipy.spatial.distance import cosine

import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)


def calculate_mfcc(file_path, n_mfcc=13):
    """
    Calculate the mean MFCC for an audio file.

    :param file_path: Path to the audio file
    :param n_mfcc: Number of MFCC features to extract
    :return: Mean MFCC vector
    """
    try:
        y, sr = librosa.load(file_path)
    except:
        return np.ones((n_mfcc,), dtype=float)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)
    return np.mean(mfcc, axis=1)


def rank_tracks_cosine(target_mfcc, mfcc_dict):
    """
    Rank tracks by cosine distance to the target track.

    :param target_track: Feature list of the target audio file
    :param track_list: Dict[int, List[features]]of features of audio files to rank
    :return: List of tracks sorted by similarity to the target track
    """

    target_mfcc = np.array(target_mfcc)
    for key in mfcc_dict:
        mfcc_dict[key] = np.array(mfcc_dict[key])

    distances = {key: cosine(target_mfcc, mfcc_dict[key]) for key in mfcc_dict}

    return [k for k, _ in sorted(distances.items(), key=lambda item: item[1])]
