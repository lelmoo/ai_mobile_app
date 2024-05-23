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


def rank_tracks_cosine(target_track, track_list):
    """
    Rank tracks by cosine distance to the target track.

    :param target_track: Path to the target audio file
    :param track_list: List of paths to audio files to rank
    :return: List of tracks sorted by similarity to the target track
    """
    target_mfcc = calculate_mfcc(target_track)
    track_array = np.array(track_list)

    track_mfccs = np.array([calculate_mfcc(track) for track in track_list])

    distances = np.array(
        [cosine(target_mfcc, track_mfcc) for track_mfcc in track_mfccs]
    )

    sorted_indices = np.argsort(distances)
    sorted_tracks = track_array[sorted_indices]

    return sorted_tracks

