"""The elements required to run a single player game of battleships"""
import logging
from .components import initialise_board,create_battleships,place_battleships

def attack(coordinates: tuple, board_to_attack: list, battleships:dict) -> bool:
    """Proccesses an attack on a battleship.

    param coordinates: the (x, y) coordinates of the attack.
    param board_to_attack: the game board to attack.
    param battleships: dictionary representing battleships and their remaining lengths.

    return bool: a boolean indicating if the attack was successful or not.
    return board_to_attack: the updated game board
    return battleships: the updated battleships dictionary."""
    x, y = coordinates
    #flip coords as python iterates through rows first then columns
    board_value = board_to_attack[int(y)][int(x)]
    if board_value is not None:
        print(f"Hit {board_value}")
        battleships[board_value] -= 1
        board_to_attack[int(y)][int(x)] = None
        if battleships[board_value] == 0:
            logging.info("%s has been sunk!", board_value)
            print(f"{board_value} has been sunk!")
        return True, board_to_attack, battleships
    print("Miss")
    return False, board_to_attack, battleships

def cli_coordinates_input() -> tuple:
    """Gets the user input for the attack coordinates.

    return (x,y): tuple containing the coordinates the user wants to attack."""
    while True:
        try:
            x = int(input("Enter a number for the column you'd like to attack: "))
        except ValueError:
            print("Please enter a valid integer")
            continue
        else:
            break
    while True:
        try:
            y = int(input("Enter a number for the row you'd like to attack: "))
        except ValueError:
            print("Please enter a valid integer")
        else:
            break
    return (x,y)


def simple_game_loop():
    """Runs a simple game loop for a one player game of battleships on the console."""
    logging.info("Simple game started")
    print("Ahoyhoy, Welcome to Battleships!")
    board_size = 0
    while board_size < 6 or board_size > 10:
        try:
            board_size = int(input("What size would you like the board? (6-10):"))
        except ValueError:
            logging.warning("Invalid board size entered: %s", board_size)
            print("Please enter a number between (6-10)")
    grid = initialise_board(size=board_size)
    battleships = create_battleships()
    board = place_battleships(grid, battleships)
    valid_coords = [(x, y) for x in range(board_size) for y in range(board_size)]
    while sum(battleships.values()) > 0:
        attack_coordinates = cli_coordinates_input()
        if attack_coordinates not in valid_coords:
            print(f"""This is not on the board or you have already attacked here.
Please try again with a value between (0-{board_size - 1})""")
            logging.warning("Invalid coordinate input: %s", attack_coordinates)
            continue
        else:
            attack(attack_coordinates,board,battleships)
            logging.info("Player attacked %s", attack_coordinates)
            valid_coords.remove(attack_coordinates)
    logging.info("Game completed successfully.")
    print("Game Over")


if __name__ == "__main__":
    simple_game_loop()
