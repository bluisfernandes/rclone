import sys
import os
import subprocess

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


def run_command(command, ask=False):
    GREEN = '\033[32m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'
    
    if ask:
        print(f'Proceed with command {GREEN}{command}{RESET} ? (y/n) ', end='')
        choice_proceed = get_input(['y', 'n'], False)
        if choice_proceed != 'y':
            return False
    print(f"Running {UNDERLINE}{command}{RESET}")

    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Print output line by line as it is produced
    try:
        for line in process.stdout:
            print(line, end="")  # Print each line as it comes
    except KeyboardInterrupt:
        process.terminate()  # Terminate the process if needed
        print("\nProcess terminated.")

    # Wait for the command to complete and get the return code
    return_code = process.wait()

    # Check for errors
    if return_code != 0:
        error_output = process.stderr.read()
        print("Error:", error_output)
    
    return return_code


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