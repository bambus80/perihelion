import os
from typing import List, Dict, Any
import re

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_valid_input(prompt: str, validator=None, error_msg: str = "Invalid input. Please try again.") -> str:
    while True:
        user_input = input(prompt).strip()
        if validator is None or validator(user_input):
            return user_input
        print(error_msg)

def validate_name(name: str) -> bool:
    return bool(re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', name))

def validate_folder(name: str) -> bool:
    is_format = bool(re.match(r'^[0-9]+-[a-zA-Z0-9_\-]*$', name))
    return is_format and os.path.exists(f"cogs/{name}")

def validate_desc(desc: str) -> bool:
    return bool(re.match(r'^[^"\\]*(\\.[^"\\]*)*$', desc))

def main():
    commands = []

    clear_screen()
    print("Perihelion Cog Generator")
    print("=" * 50)

    # Get cog name
    cog_name = get_valid_input(
        "\nEnter the name for your cog (alphanumeric, starts with letter): ",
        validate_name,
        "Invalid cog name. Use only letters, numbers, and underscores, starting with a letter."
    )

    # Get cog name
    cog_folder = get_valid_input(
        "\nEnter the folder for your cog to go in [number, hyphen, alphanumeric, e.g. \"0-load-first\"]: ",
        validate_folder,
        "Invalid folder name, or the folder doesn't exist."
    )

    while True:
        clear_screen()
        print(f"Creating cog: {cog_name} (@priority {cog_folder})")
        print(f"Current commands: {', '.join(cmd['name'] for cmd in commands) or 'None'}")
        print("\nOptions:")
        print("1. Add new command")
        print("2. Delete command")
        print("3. Generate cog file")
        print("4. Exit")

        choice = get_valid_input(
            "\nSelect an option (1-4): ",
            lambda x: x in ['1', '2', '3', '4'],
            "Please enter 1, 2, 3, or 4."
        )

        if choice == '1':
            command = {}
            clear_screen()
            print("Adding new command")
            print("-" * 30)

            # Get command name
            command['name'] = get_valid_input(
                "\nEnter command name (alphanumeric, starts with letter): ",
                validate_name,
                "Invalid command name. Use only letters, numbers, and underscores, starting with a letter."
            )

            # Get command description
            command['description'] = get_valid_input("\nEnter command description: ")

            # Get parameters
            command['parameters'] = []
            while True:
                clear_screen()
                print(f"Command: {command['name']}")
                print(f"Current parameters: {', '.join(param['name'] for param in command['parameters']) or 'None'}")
                add_param = get_valid_input(
                    "\nAdd a parameter? (y/n): ",
                    lambda x: x.lower() in ['y', 'n'],
                    "Please enter 'y' or 'n'."
                ).lower()

                if add_param == 'n':
                    break

                param = {}
                param['name'] = get_valid_input(
                    "\nParameter name: ",
                    validate_name,
                    "Invalid parameter name. Use only letters, numbers, and underscores, starting with a letter."
                )
                param['description'] = get_valid_input(
                    "\nParameter description: ",
                    validate_desc,
                    "Invalid parameter description, double quotes must be escaped!"
                )

                print("\nCommon types:")
                print("1. str")
                print("2. int")
                print("3. float")
                print("4. bool")
                print("5. discord.Member")
                print("6. discord.User")
                print("7. discord.TextChannel")
                print("8. Other (specify)")

                type_choice = get_valid_input(
                    "\nSelect parameter type (1-8): ",
                    lambda x: x in [str(i) for i in range(1, 9)],
                    "Please enter a number between 1 and 8."
                )

                type_map = {
                    '1': 'str',
                    '2': 'int',
                    '3': 'float',
                    '4': 'bool',
                    '5': 'discord.Member',
                    '6': 'discord.User',
                    '7': 'discord.TextChannel'
                }

                if type_choice == '8':
                    param['type'] = input("\nEnter type: ")
                else:
                    param['type'] = type_map[type_choice]

                param['optional'] = get_valid_input(
                    "\nIs this parameter optional? (y/n): ",
                    lambda x: x.lower() in ['y', 'n'],
                    "Please enter 'y' or 'n'."
                ).lower() == 'y'

                command['parameters'].append(param)

            commands.append(command)

        elif choice == '2':
            # Add this new option between adding commands and generating
            clear_screen()
            if not commands:
                print("No commands to delete!")
                input("\nPress Enter to continue...")
                continue

            print("Select command to delete:")
            for i, cmd in enumerate(commands, 1):
                print(f"{i}. {cmd['name']}")
            print(f"{len(commands) + 1}. Cancel")

            delete_choice = get_valid_input(
                f"\nSelect command to delete (1-{len(commands) + 1}): ",
                lambda x: x.isdigit() and 1 <= int(x) <= len(commands) + 1,
                f"Please enter a number between 1 and {len(commands) + 1}."
            )

            if int(delete_choice) <= len(commands):
                deleted = commands.pop(int(delete_choice) - 1)
                print(f"\nDeleted command: {deleted['name']}")
                input("\nPress Enter to continue...")

        elif choice == '3':
            # Generate the cog file
            filename = f"cogs/{cog_folder}/{cog_name.lower()}.py"

            # Header
            content = f'''import discord
from discord import app_commands
from discord.ext import commands
from utils.logging import log
from utils.embeds import *
from typing import Optional
from utils.userdata import get_data_manager
from discord.app_commands import locale_str

class {cog_name}Cog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        log.info("Cog: {cog_name.lower()} loaded")

'''

            # Commands
            for cmd in commands:
                # Build parameter string
                params = ["self", "interaction: discord.Interaction"]
                for param in cmd['parameters']:
                    param_str = f"{param['name']}: "
                    if param['optional']:
                        param_str += f"Optional[{param['type']}] = None"
                    else:
                        param_str += param['type']
                    params.append(param_str)

                param_str = ", ".join(params)

                descrs = []
                for param in cmd['parameters']:
                    if not param['description']: pass
                    descrs.append(f"{param['name']}=\"{param['description']}\",")

                description_str = f"\n    @app_commands.describe(\n        {'\n        '.join(descrs)}\n    )" if descrs else ""
                content += f'''    @app_commands.command(name="{cmd['name']}", description="{cmd['description']}"){description_str}
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def {cmd['name']}({param_str}):
        ... # TODO: implement

'''

            # Footer
            content += f'''async def setup(client):
    await client.add_cog({cog_name}Cog(client))
'''

            # Write to file
            with open(filename, 'w') as f:
                f.write(content)

            print(f"\nCog file generated at {cog_folder} as '{filename}'")
            input("\nPress Enter to continue...")

        else:  # choice == '4'
            break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
