# This file contains functions for detecting and repairint hum sounds that are 
# likely to cause issues with Anima NXTs. 
# 
# Code generated with help from Claud AI, but incorporated and checked by hand.

from pydub import AudioSegment
import numpy as np

def get_sample_count(segment: AudioSegment) -> int:
    """Total number of audio frames (samples per channel) in the segment."""
    return int(segment.frame_count())

def check_parity(segment: AudioSegment) -> dict:
    """
    Check a segment's raw sample count parity and return a prediction.

    Returns a dict: {"samples": int, "parity": "even"|"odd", "predicted_safe": bool}
    """
    n = get_sample_count(segment)
    is_even = (n % 2 == 0)
    return {
        "samples": n,
        "parity": "even" if is_even else "odd",
        "predicted_safe": is_even,
    }

def _segment_to_array(segment: AudioSegment) -> np.ndarray:
    """Extract samples as a numpy array, dtype inferred from the segment's own format."""
    return np.array(segment.get_array_of_samples())

def repair_segment(segment: AudioSegment, position: float = 0.5,
                    crossfade_ms: int = 10) -> AudioSegment:
    """
    Unconditionally apply a single crossfade splice repair to `segment`.

    Cuts the segment at `position` (fraction of total duration, 0-1) and
    rejoins the two pieces with a `crossfade_ms` linear crossfade. Output
    loudness (dBFS) is matched to the input to avoid an audible level jump.

    This does not check whether the segment is actually flagged as
    dangerous first. Only mono audio is currently supported, matching the d
    ocumented hum file format (16-bit, mono, 44.1kHz).
    """
    if segment.channels != 1:
        raise NotImplementedError(
            "repair_segment() currently only supports mono audio "
            f"(got {segment.channels} channels)."
        )

    n = get_sample_count(segment)
    crossfade_samples = int(round(segment.frame_rate * crossfade_ms / 1000.0))

    if n <= crossfade_samples * 2:
        raise ValueError(
            f"Segment too short ({n} samples) for a {crossfade_samples}-sample crossfade splice."
        )

    cut = int(n * position)
    # Keep the cut point away from the very start/end so there's room for
    # the crossfade window on both sides.
    cut = max(crossfade_samples + 1, min(n - crossfade_samples - 1, cut))

    samples = _segment_to_array(segment)
    dtype = samples.dtype
    info = np.iinfo(dtype)

    data = samples.astype(np.float64)
    a = data[:cut]
    b = data[cut:]

    ramp = np.linspace(1, 0, crossfade_samples)
    junction = a[-crossfade_samples:] * ramp + b[:crossfade_samples] * (1 - ramp)
    spliced = np.concatenate([a[:-crossfade_samples], junction, b[crossfade_samples:]])

    # This guarantees len(spliced) == n - crossfade_samples exactly, every
    # time, regardless of position -- which is what makes the parity flip
    # deterministic (unlike the pydub-ms-based approach this replaced).

    original_dbfs = segment.dBFS

    spliced = np.clip(spliced, info.min, info.max)
    spliced_int = spliced.astype(dtype)

    new_segment = segment._spawn(spliced_int.tobytes())

    # Preserve original loudness (the blend can shift overall level slightly)
    if original_dbfs != float("-inf") and new_segment.dBFS != float("-inf"):
        new_segment = new_segment.apply_gain(original_dbfs - new_segment.dBFS)

    return new_segment