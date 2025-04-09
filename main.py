import pyfiglet
from get_user_inputs import GetUserInputs
from termcolor import colored

def print_logo():
    ascii_logo = pyfiglet.figlet_format("Agent Deployer", font="slant")  # Change font if needed
    colored_logo = colored(ascii_logo, "cyan")  # Change color if needed
    print(colored_logo)

if __name__ == "__main__":
    print_logo()
    take_inputs = GetUserInputs();
    take_inputs.ask_questions()    