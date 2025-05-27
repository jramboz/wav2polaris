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
