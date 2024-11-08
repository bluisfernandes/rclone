import sys
import os
from utils_rclone import run_command, get_input, get_directories, choose_mode, get_subpath, get_subfolders

# Config print colors
RED = '\033[31m'
GREEN = '\033[32m'
UNDERLINE = '\033[4m'
RESET = '\033[0m'

# Check usage
inputs = sys.argv
if len(inputs) != 2:
    sys.exit(f'Usage "python {inputs[0]} $PWD"')

# Check if input path exists
pwd = inputs[1]
if not os.path.exists(pwd):
    sys.exit(f"ERROR: input path '{pwd}' does not exist")

home_path = os.getenv('HOME')
directory_path = 'projects/rclone/directories'
url_directories = os.path.join(home_path, directory_path)

dirs = get_directories(url_directories)

is_subpath, base_path = get_subpath(pwd, dirs)
if is_subpath:
    rel_path = get_subfolders(base_path, pwd)

    print(f"Your current path is:\t {GREEN}{base_path}{RESET}/{rel_path}")
# Check if current directory is on directories file
else:
    print(f"{RED}ERROR{RESET}: '{pwd}' not in directories file or subpath")
    sys.exit()

modes = choose_mode(dirs[base_path].get('mode'))

print("Please select an option:")
choices_mode = {}
for option in modes:
    choices_mode[option[0]] = option
    choices_mode[option] = option
    print(f"{option[0]} > {option}")
other_choices = ['check', 'quit']
for other in other_choices:
    choices_mode[other[0]] = other
    choices_mode[other] = other
    print(f"{other[0]} > {other}")

choice = get_input(choices_mode)
choice_mode = choices_mode[choice]
print(f"You selected {choice}: {choice_mode}")

target_dir = os.path.join(dirs[base_path]['target'], rel_path)
source_dir = os.path.join(dirs[base_path]['source'], rel_path)

if choice_mode == 'check':

    source = source_dir
    destination = target_dir

    print(f'\tFROM: \t{source}\n\tTO: \t{destination}\n\tMODE: \t{UNDERLINE}{choice_mode}{RESET}\n')

    command = f'temp_file=$(mktemp) && rclone check {source} {destination} --combined $temp_file; cat $temp_file | grep -v "^="; rm $temp_file'

    return_code = run_command(command, ask=True)

elif choice_mode == 'download' or choice_mode == 'upload':

    source = target_dir if choice_mode == 'download' else source_dir
    destination = source_dir if choice_mode == 'download' else target_dir

    print(f'\tFROM: \t{source}\n\tTO: \t{destination}\n\tMODE: \t{UNDERLINE}{choice_mode}{RESET}\n')

    command = f'rclone copy {source} {destination} -P -v'

    return_code = run_command(command, ask=True)

status = f'{GREEN}Done.{RESET}' if return_code == 0 else f'{RED}Error.{RESET}'
# exit
get_input(None,False, msg= f'{status} Press any key to exit')