# Main hub for all Decked Him! sports betting and fantasy analytics tools
import nfl
import mlb
import tennis
import general
import os

def help():
    # Update the working directory for file imports
    script_directory = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_directory)
    
    with open("help.txt", "r") as file:
        contents = file.read()

    print(contents)

def main():
    print("Welcome to The Forge.\n")
            
    main_input = 0
    
    while main_input != "quit":
        # Update the working directory for file imports
        script_directory = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_directory)
        
        # Dictionary of available commands/functions
        command_to_function = {}
        with open('commands.txt', 'r') as file:
            for line in file:
                command, function_path = line.strip().split(',')
                command_to_function[command] = function_path

        main_input = input("Type command, type 'help' to see a list of all commands, or 'quit' to exit: ")
        
        if main_input in command_to_function:
            # Retrieve command function from dictionary
            function_path = command_to_function[main_input]
            
            try:
                eval(function_path + '()') # Call the function using its path
            except NameError:
                print(f"Function '{function_name}' is not defined.\n")
        else:
            print("Invalid input.\n")

if __name__ == "__main__":
    main()
