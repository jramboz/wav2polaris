import re

# List of regexes that will match the default Polaris naming scheme.
# Used with the option to exclude unmatched files
POLARIS_FILES_REGEXES = [
    r'^CLASH_\d+_0\.RAW$',
    r'^HUM_\d+\.RAW$',
    r'^POWER(OFF|ON)_\d+\.RAW$',
    r'^SMOOTHSWING(H|L)_\d+_0\.RAW$',
    r'^SWING_\d+_0\.RAW$',
    r'^BEEP\.RAW$'
]


def is_polaris_filename(filename: str) -> bool:
    for pattern in POLARIS_FILES_REGEXES:
        if re.match(pattern, filename):
            return True
    return False

# Function to determine if a file is a hum. Assume anything starting with
# "hum" or "HUM" is a hum.
HUM_REGEX = r"^hum.*$"

def is_hum(filename: str) -> bool:
    if re.match(HUM_REGEX, filename, re.I):
        return True
    else:
        return False