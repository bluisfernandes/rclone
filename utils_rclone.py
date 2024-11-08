import sys
import os
import subprocess
import threading

def get_directories(url):
    home_path = os.getenv('HOME')
    paths = {}
    with open(url, "r") as file:
        for k, line in enumerate(file.readlines()):
            if line.strip() and line.strip()[0] == '#':
                continue
            line = line.replace("~", home_path )
            line = line.split(",")
            if len(line) < 2 or len(line) > 4:
                sys.exit(f'Error in directories file. line: {k}\n{line}')
            source, target, *mode = line
            source, target = source.strip(), target.strip()
            mode = [m.strip() for m in mode] if mode else []

            if source[0] != '#':
                paths[source] = {'source': source,
                                'target': target,
                                'mode': mode}
    return paths


def choose_mode(modes):
    options = []
    for mode in modes:
        if 'download' in mode or 'upload' in mode:
            options.append(mode)
    return options


def get_input(options, print_confirmation=True, msg=''):
    if msg:
        print(msg)
    text = "Enter your choice: " if print_confirmation else ''
    choice = input(text).lower()
    if options:
        while True:
            if choice in ['q', 'quit']:
                sys.exit()
            elif choice in [op.lower() for op in options]:
                break  # Exit the loop after a valid selectionS
            choice = input("Not Valid. Enter your choice: ")
    return choice


def run_command(command, ask=False, return_stdout=False):
    '''
    Runs a command and returns return_code
    if return_stdout=True, returns (return_code, stdout)
    if return_stdout=list, returns (return_code, stdout) for each line that starts with a char in list e.g.(+-=!)
    '''
    RED = '\033[31m'
    GREEN = '\033[32m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'
    
    if ask:
        print(f'Proceed with command {GREEN}{command}{RESET} ? (y/n) ', end='')
        choice_proceed = get_input(['y', 'n'], False)
        if choice_proceed != 'y':
            return False
    print(f"Running {UNDERLINE}{command}{RESET}")

    # Start the process
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if return_stdout is not False:
        to_return = []
    # Function to read stdout in real-time
    def read_stdout():
        for line in process.stdout:
            print(line, end="")
            if return_stdout is True:
                to_return.append(line.strip('\n'))
            elif isinstance(return_stdout,list) and line[0] in return_stdout:
                to_return.append(line.strip('\n'))

    # Function to read stderr in real-time
    def read_stderr():
        for line in process.stderr:
            print(f"{RED}ERROR:{RESET} {line}", end="")

    # Start threads to read stdout and stderr simultaneously
    stdout_thread = threading.Thread(target=read_stdout)
    stderr_thread = threading.Thread(target=read_stderr)
    stdout_thread.start()
    stderr_thread.start()

    # Wait for the process to complete and the threads to finish
    stdout_thread.join()
    stderr_thread.join()
    return_code = process.wait()

    if return_code != 0:
        print(f"\n{RED}ERROR: {RESET}Command exited with errors. Return code: {return_code}")
    
    if return_stdout is False:
        return return_code
    else:
        return return_code, to_return


def get_subpath(path, path_list):
    for base_path in path_list:
        # Check if path starts with base_path as a common path
        if os.path.commonpath([base_path, path]) == base_path:
            return True, base_path
    return False, None


def get_subfolders(base_path, path):
    # Ensure `path` is a subpath of `base_path`
    if os.path.commonpath([base_path, path]) != base_path:
        return None  # Not a subpath

    # Get the relative path
    relative_path = os.path.relpath(path, base_path)
    relative_path = '' if relative_path == '.' else relative_path
    return relative_path