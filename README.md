# wav2polaris
`wav2polaris` is a Python library and command-line utility for converting lightsaber sound font `.wav` files into `.RAW` files for use with a Polaris Anima-based lightsaber, such as those from [Lama di Luce](https://www.lamadiluce.it/) or [LudoSport Atlas](https://ludosportatlas.com/collections/piezas-sables).

<a href="https://www.flaticon.com/free-icons/lightsaber" title="lightsaber icons">Lightsaber icons created by Nhor Phai - Flaticon</a>. Sound wave icon by [KMpumlwana (WMF), CC0, via Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Sound_wave_holding_shape_-_Medium_01.svg)

## Features
- Automatically converts the input `.wav` to the correct sound parameters for Polaris Anima
- Automatically translate file names from various common lightsaber sound font formats (CFX, Proffie, Verso, Xenopixel) to Polaris Anima standard
- Optionally ignore files that can't be matched to a Polaris standard filename (e.g., to exclude things like stabs, drags, force, and other effects that Polaris Anima doesn't use.)
- Process a single file or mutliple files at once
- Process all `.wav` files in a directory/folder
- Supports File Explorer drag-and-drop or command-line usage
- Optionally trim sound files to Anima NXT-compatible lengths

## Program Usage
### Drag-and-Drop
Download the [pre-built executable](https://github.com/jramboz/wav2polaris/releases) for your OS. In Windows Explorer or macOS Finder, drag the files or folder you want to convert onto the `wav2polaris` icon. `wav2polaris` will convert any `.wav` files and place the equivalent `.RAW` files in the same location.

### Command Line
Download the [pre-built executable](https://github.com/jramboz/wav2polaris/releases) for your OS. Place it in the folder with your `.wav` files or somewhere in your environment's PATH.

Alternately, if you have Python3 installed on your system, you can install with the command: `pip install wav2polaris`.

```
usage: wav2polaris [-h] [-v] [-s | -w] [-c] [-D] [-N] [-T] [-o OUTDIR] [-E] [files ...]

A utility for converting lightsaber sound font .wav files to .RAW files for Polaris Anima sabers.

positional arguments:
  files                 one or more .wav files to convert (separated by spaces)

options:
  -h, --help            show this help message and exit
  -v, --version         display version and author information, then exit
  -s, --silent          exit without waiting for keypress
  -w, --wait            wait for keypress before exiting (default)
  -c, --continue-on-file-not-found
                        if one or more specified files do not exist, continue processing the remaining files (otherwise
                        program will exit)
  -D, --debug           Show debugging information
  -N, --no-rename       do not attempt to rename output files to Polaris standards (e.g., CLASH_1_0.RAW)
  -T, --trim            Trim output files to NXT-compatible lengths
  -o, --outdir OUTDIR   put output files in specified directory (will be created if it does not exist)
  -E, --exclude-unmatched
                        do not process files that cannot be matched to a standard Polaris filename
```

