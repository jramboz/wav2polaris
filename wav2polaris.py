import argparse
from getch import pause_exit
import glob
import sound
import logging
import sys
import platform
import os
import errno
import utils

script_version = '0.3'
script_authors = 'Jason Ramboz'
script_repo = 'https://github.com/jramboz/wav2polaris'

def _expand_wildcard(pattern: str) -> list[str]:
    '''Expand wildcards using glob. This is needed when system is Windows or when we later modify args to include a wildcard.'''
    log = logging.getLogger()
    log.debug(f'Expanding wildcard: {pattern}')
    expanded_files = glob.glob(pattern)
    log.debug(f'Expanded files: {expanded_files}')
    return expanded_files

def main_func():
    log = logging.getLogger()
    if not log.hasHandlers():
            stream = logging.StreamHandler(sys.stdout)
            #stream.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s: %(message)s'))
            stream.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
            log.addHandler(stream)
    
    exit_code = 0

    # configure command line parser and options
    parser = argparse.ArgumentParser(prog='wav2polaris',
                                    description='A utility for converting lightsaber sound font .wav files to .RAW files for Polaris Anima sabers.')
    parser.add_argument('-v', '--version',
                        action="version",
                        help='display version and author information, then exit',
                        version='%(prog)s v{ver} - Author(s): {auth} - {page}'.format(ver=script_version, auth=script_authors, page=script_repo))
    parser.add_argument('files', nargs="*",
                        help='one or more .wav files to convert (separated by spaces)')
    exit_behavior = parser.add_mutually_exclusive_group()
    exit_behavior.add_argument('-s', '--silent', 
                                action="store_true",
                                help='exit without waiting for keypress')
    exit_behavior.add_argument('-w', '--wait', 
                                action="store_true",
                                help='wait for keypress before exiting (default)')
    parser.add_argument('-c', '--continue-on-file-not-found',
                        action="store_true",
                        help='if one or more specified files do not exist, continue processing the remaining files (otherwise program will exit)')
    parser.add_argument('-D', '--debug',
                        action="store_true",
                        help='Show debugging information')
    parser.add_argument('-N', '--no-rename',
                        action="store_true",
                        help='do not attempt to rename output files to Polaris standards (e.g., CLASH_1_0.RAW)')
    parser.add_argument('-T', '--trim',
                        action="store_true",
                        help='Trim output files to NXT-compatible lengths')
    parser.add_argument('-o', '--outdir',
                        action='store', dest='outdir',
                        help='put output files in specified directory (will be created if it does not exist)')
    parser.add_argument('-E', '--exclude-unmatched',
                        action="store_true",
                        help='do not process files that cannot be matched to a standard Polaris filename')
    
    args = parser.parse_args(args=None if sys.argv[1:] else ['--help'])

    if args.debug:
        log.setLevel(logging.DEBUG)

    try:
        if args.files:
            # for Windows, we need to manually expand any wildcards in the input list
            if platform.system() == 'Windows':
                log.info('Windows system detected. Expanding any wildcards in file names.')
                expanded = []
                for file in args.files:
                    expanded.extend(_expand_wildcard(args.files))

            print(f'\nPreparing to convert {str(len(args.files)) + " " if len(args.files)>1 else ""}file{"s" if len(args.files)>1 else ""}')
            
            # verify that files exist
            verified_files = []
            for file in args.files:
                try:
                    log.debug(f'Checking file: {file}')
                    if not os.path.exists(file):
                        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), file)
                    
                    if os.path.isdir(file): # if a directory is specified, convert all wav files in that directory
                        file = os.path.join(file, '*.wav')
                        args.files.extend(_expand_wildcard(file))
                    else:
                        verified_files.append(file)
                except FileNotFoundError as e:
                    log.error(f'File not found: {e.filename}')
                    if args.continue_on_file_not_found:
                        continue
                    else:
                        log.error('Aborting operation.')
                        exit_code = 1
                        sys.exit(1)
            log.debug(f'Verified {len(verified_files)} file{"s" if len(verified_files)>1 or len(verified_files)==0 else ""}: {verified_files}')

            if not verified_files:
                exit_code = 1
                return

            # Convert files
            converted_files = []
            error_files = []
            if args.no_rename:
                log.info('Skipping file renaming.')
            
            for file in verified_files:
                outdir = '' # Empty string instead of None lets us safely use it in functions
                # Check to see if output dir is specified. Need to do this for each file in case user specified a relative path and files in multiple directories
                if args.outdir:
                    if not os.path.isabs(args.outdir): # if relative path is provided, add it to the input file's path
                        basepath = os.path.dirname(os.path.realpath(file))
                        outdir = os.path.join(basepath, args.outdir)
                    else: # absolute path given
                        outdir = args.outdir

                if args.no_rename:
                    output = sound.convert_wav_to_polaris_raw(file, outdir, args.trim)
                else:
                    destination = sound.get_polaris_filename(file)
                    log.debug(f'Auto-matching result: {os.path.basename(file)} -> {destination}')
                    if args.exclude_unmatched:
                        if not utils.is_polaris_filename(destination):
                            log.debug(f'Skipping unmatched file: {os.path.basename(file)}')
                            continue # Go to the next file
                    target = os.path.join(outdir, destination)
                    log.debug(f'Destination output: {target}')
                    output = sound.convert_wav_to_polaris_raw(file, target, args.trim)

                if output:
                    log.debug(f'Converted file successfully: {file} -> {output}')
                    converted_files.append((file, output))
                else:
                    log.error(f'Error converting file {os.path.basename(file)}. Unable to process this file.')
                    log.debug(f'Details: {file} -> {output}')
                    error_files.append((file, output))
    
            # Report on conversion
            print(f'\nConversion{"s" if len(verified_files)>1 else ""} complete.')
            if converted_files:
                print('\nFiles converted successfully:')
                for input, output in converted_files:
                    print(f'\t{os.path.basename(input)} -> {os.path.basename(output)}')
            if error_files:
                exit_code = 1
                print('\nErrors occurred processing files:')
                for input, output in error_files:
                    print(os.path.basename(input))
    
    except Exception as e:
        log.error(e)
        exit_code = 1
    
    finally:
        if not args.silent:
            pause_exit(exit_code, '\nPress any key to exit.')
        else:
            sys.exit(exit_code)

if __name__ == '__main__':
    main_func()