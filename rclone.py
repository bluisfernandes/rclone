import sys
import os
from utils_rclone import run_command, get_input, get_directories, choose_mode

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


print(f"Your current path is:\t {pwd}")
dirs = get_directories(url_directories)

# Check if current directory is on directories file
if pwd not in dirs:
    sys.exit(f"ERROR: '{pwd}' not in directories file")

modes = choose_mode(dirs[pwd].get('mode'))

print("Please select an option:")
choices_mode = {}
for k, option in enumerate(modes):
    choices_mode[str(k)] = option
    choices_mode[option] = option
    print(f"{k} > {option}")
print('q > quit')
choices_mode['q'] = 'quit'
choices_mode['quit'] = 'quit'


choice = get_input(choices_mode)
choice_mode = choices_mode[choice]
print(f"You selected {choice}: {choice_mode}")

source = dirs[pwd]['target'] if choice_mode == 'download' else dirs[pwd]['source']
destination = dirs[pwd]['source'] if choice_mode == 'download' else dirs[pwd]['target']

GREEN = '\033[32m'
UNDERLINE = '\033[4m'
RESET = '\033[0m'
print(f'\tFROM: \t{source}\n\tTO: \t{destination}\n\tMODE: \t{UNDERLINE}{choice_mode}{RESET}\n')

command = f'echo clone copy {source} {destination}'

run_command(command, ask=True)
# exit
get_input(None,False, msg= f'{GREEN}Done.{RESET} Press any key to exit')