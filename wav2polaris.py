import argparse
from getch import pause_exit
import glob
import sound
import logging
import sys
import platform
import os
import errno

script_version = '0.1'
script_authors = 'Jason Ramboz'
script_repo = 'https://github.com/jramboz/wav2polaris'

def main_func():
    log = logging.getLogger()
    
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
    
    args = parser.parse_args(args=None if sys.argv[1:] else ['--help'])

    if args.debug:
        log.setLevel(logging.DEBUG)

    try:
        if args.files:
            # for Windows, we need to manually expand any wildcards in the input list
            if platform.system() == 'Windows':
                log.info('Windows system detected. Expanding any wildcards in file names.')
                expanded_files = []
                for file in args.files:
                    expanded_files.extend(glob.glob(file))
                args.files = expanded_files
                log.debug(f'Expanded files: {args.files}')

            print(f'\nPreparing to convert {str(len(args.files)) + " " if len(args.files)>1 else ""}file{"s" if len(args.files)>1 else ""}')
            
            # verify that files exist
            verified_files = []
            for file in args.files:
                try:
                    if not os.path.isfile(file):
                        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), file)
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

            # Convert files
            converted_files = []
            error_files = []
            if args.no_rename:
                log.info('Skipping file renaming.')
            
            if not verified_files:
                exit_code = 1
                return
            
            for file in verified_files:
                if args.no_rename:
                    output = sound.convert_wav_to_polaris_raw(file)
                else:
                    destination = sound.get_polaris_filename(file)
                    log.debug(f'Auto-matching result: {os.path.basename(file)} -> {destination}')
                    output = sound.convert_wav_to_polaris_raw(file, destination)

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