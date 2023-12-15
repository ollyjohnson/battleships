""""This contains all the necessary features to be used in creating and setting up the game"""
import logging
import random
import json

logging.basicConfig(level=logging.DEBUG, filename='battleships.log',
                    format='%(asctime)s - %(levelname)s - %(message)s')

def initialise_board(size: int = 10) -> list[list[None]]:
    """Creates an empty board with a given size.
    
    param size: an integer that is used to determine the number of rows and columns for the board.

    return board_state: a list of lists of the specified size."""
    if not isinstance(size, int):
        raise TypeError("Size must be an integer.")
    if size < 5 or size > 15:
        raise ValueError("Size must be between 5 and 15.")
    board_state = [[None for i in range(size)] for j in range(size)]
    logging.info("Board initialised with size %s", size)
    return board_state

def create_battleships(filename: str = "battleships.txt") -> dict[str, int]:
    """Reads a text file and creates a dictionary of battleships with their lengths.

    param filename : The path to the text file containing battleship data.

    return battleship_dict: a dictionary where keys are battleship names 
    and values are their lengths."""
    battleship_dict = {}
    try:
        with open(filename, "r", encoding="utf-8") as file:
            for line in file:
                battleship_dict[line.split(",")[0]] = int(line.split(",")[1].strip())
            logging.info("Battleships created from file successfully")
        return battleship_dict
    except FileNotFoundError as exc:
        logging.error("File not found: %s", filename)
        raise FileNotFoundError(f"File not found: {filename}") from exc
    except Exception as e:
        logging.error("Error in create_battleships: %s", e)
        raise

def json_to_dict(json_path: str | dict) -> dict[str, list[int,int,str]]:
    """Takes a JSON file and transforms it into a dictionary.

    param json_path: the path to the .JSON file or the dictionary returned from the web server.

    returns swapped_ship_coords: the dictionary with the Ships, Coordinates and Orientation"""
    if isinstance(json_path, str):
        with open(json_path, "r", encoding="utf-8") as file:
            try:
                ship_coords = json.load(file)
            except json.JSONDecodeError as exc:
                logging.error("JSON decode error in json_to_dict function")
                raise exc
    elif isinstance(json_path, dict):
        ship_coords = json_path
    else:
        logging.error("Invalid input for json_to_dict function.")
        return None
    # swap the coords of the ships as python iterates through the rows before the columnns
    swapped_ship_coords = {}
    for ship, coords in ship_coords.items():
        swapped_ship_coords[str(ship)] = [int(coords[1]),int(coords[0]),str(coords[2])]
    return swapped_ship_coords

def is_valid_placement(length: int, orientation: str, row: int, col:int, board:list)-> bool:
    """Checks if placing a battleship of a given length and orientation is valid 
    at a specific position on the board.

    param length : The length of the battleship.
    param orientation : The orientation of the battleship ('h' for horizontal, 'v' for vertical).
    param row : The row on the board to check.
    param col : The column on the board to check.
    param board : The game board.

    return: True if the placement is valid, False otherwise."""
    if orientation == "h":
        if (col + length) > (len(board)):
            return False
        for i in range(length):
            if board[row][col+i] is not None:
                return False
    if orientation == "v":
        if (row + length) > (len(board)):
            return False
        for i in range(length):
            if board[row+i][col] is not None:
                return False
    return True
def place_battleships(board: list, ships:dict, algorithm: str ="simple",
                      custom_placement: str | dict ="custom_board.JSON"):
    """Places battleships on the game board using different placement algorithms.

    param board: The game board.
    param ships: The dictionary of the battleships and their lengths.
    param algorithm: The placement complexity algorithm ('simple', 'random', 'custom').
    param custom_placement: The path to a JSON file or a dictionary 
    containing custom ship placements.

    return: The game board with all battleships placed as per the algorithm choice."""
    if sum(ships.values()) > len(board)**2:
        logging.warning("Not enough space on the board for all ships.")
        return "Cannot fit the ships on the board! Increase board size or reduce no. of ships"
    if algorithm == "simple":
        row = 0
        for ship in ships:
            for index in range(ships[ship]):
                board[row][index] = ship
            row += 1
    if algorithm == "random":
        for ship in ships:
            orientation = random.choice(["h","v"])
            while True:
                row = random.randint(0,len(board)-1)
                col = random.randint(0,len(board)-1)
                if is_valid_placement(ships[ship],orientation, row, col, board):
                    if orientation == "h":
                        for i in range(ships[ship]):
                            board[row][col+i] = ship
                        break
                    if orientation == "v":
                        for i in range(ships[ship]):
                            board[row+i][col] = ship
                        break
    if algorithm == "custom":
        for ship in ships:
            ship_coords = json_to_dict(custom_placement)
            orientation = ship_coords[ship][2]
            row = ship_coords[ship][0]
            col = ship_coords[ship][1]
            if is_valid_placement(ships[ship],orientation,row,col,board):
                if orientation == "h":
                    for i in range(ships[ship]):
                        board[row][col+i] = ship
                elif orientation == "v":
                    for i in range(ships[ship]):
                        board[row+i][col] = ship
            else:
                logging.warning("Placement of %s was invalid", ship)
                return (f"Invalid Placement of {ship}")
    logging.info("Battleships placed on board successfully.")
    return board