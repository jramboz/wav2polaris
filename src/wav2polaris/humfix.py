# This file contains functions for detecting and repairint hum sounds that are 
# likely to cause issues with Anima NXTs. 
# 
# Code generated with help from Claud AI, but incorporated and checked by hand.

from pydub import AudioSegment

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

def repair_segment(segment: AudioSegment, position: float = 0.5,
                    crossfade_ms: int = 10) -> AudioSegment:
    """
    Unconditionally apply a single crossfade splice repair to `segment`.

    Cuts the segment at `position` (fraction of total duration, 0-1) and
    rejoins the two pieces with a `crossfade_ms` linear crossfade. Output
    loudness (dBFS) is matched to the input to avoid an audible level jump.

    This does not check whether the segment is actually flagged as
    dangerous first.
    """
    duration_ms = len(segment)  # pydub AudioSegment length is in milliseconds

    if duration_ms <= crossfade_ms * 2:
        raise ValueError(
            f"Segment too short ({duration_ms}ms) for a {crossfade_ms}ms crossfade splice."
        )

    cut_ms = int(duration_ms * position)
    # Keep the cut point away from the very start/end so there's room for
    # the crossfade window on both sides.
    cut_ms = max(crossfade_ms + 1, min(duration_ms - crossfade_ms - 1, cut_ms))

    first_half = segment[:cut_ms]
    second_half = segment[cut_ms:]

    original_dbfs = segment.dBFS

    spliced = first_half.append(second_half, crossfade=crossfade_ms)

    # Preserve original loudness (append+crossfade can shift overall level slightly)
    if original_dbfs != float("-inf") and spliced.dBFS != float("-inf"):
        spliced = spliced.apply_gain(original_dbfs - spliced.dBFS)

    return spliced