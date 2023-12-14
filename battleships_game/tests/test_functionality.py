import pytest
import json
from .test_helper_functions import count_ships_on_board
from components import initialise_board, create_battleships, json_to_dict, is_valid_placement, place_battleships
from game_engine import attack, cli_coordinates_input
from mp_game_engine import generate_attack

def test_initialise_board_return_size():
    """
    Test if the initialise_board function returns a list of the correct s1ize.
    """
    size = 10
    # Run the function
    board = initialise_board(size)
    # Check that the return is a list
    assert isinstance(board, list), "initialise_board function does not return a list"
    # check that the length of the list is the same as board
    assert len(board) == size, "initialise_board function does not return a list of the correct size"
    for row in board:
        # Check that each sub element is a list
        assert isinstance(row, list), "initialise_board function does not return a list of lists"
        # Check that each sub list is the same size as board
        assert len(row) == size, "initialise_board function does not return lists of the correct size"
    size = "no"
    with pytest.raises(TypeError) as excinfo:
        board = initialise_board(size)  # This should raise a TypeError
    assert "Size must be an integer." in str(excinfo.value)
    size = 4
    with pytest.raises(ValueError) as excinfo:
        board = initialise_board(size)  # This should raise a ValueError
    assert "Size must be between 5 and 15." in str(excinfo.value)

def test_create_battleships():
    """
    Test if the create_battleships function returns a dictionary with correct data.
    """
    battleship_dict = create_battleships("battleships.txt")
    
    assert isinstance(battleship_dict, dict), "create_battleships function does not return a dictionary"
    assert "Aircraft Carrier" in battleship_dict, "create_battleships function does not contain correct keys"
    assert battleship_dict["Aircraft Carrier"] == 5, "create_battleships function does not contain correct values"
    assert "Destroyer" in battleship_dict, "create_battleships function does not contain correct keys"
    assert battleship_dict["Destroyer"] == 2, "create_battleships function does not contain correct values"
    filename = "no.txt"
    with pytest.raises(FileNotFoundError) as excinfo:
        battleship_dict = create_battleships(filename)  # This should raise a FileNotFoundError
    assert str(excinfo.value) == "File not found: no.txt"
    with pytest.raises(IndexError) as excinfo:
        battleship_dict = create_battleships("tests/invalid_data.txt") # This should raise a IndexError
    assert str(excinfo.value) == "list index out of range"

def test_json_to_dict():
    """
    Test if the json_to_dict function returns a dictionary with correct data.
    """
    json_data = {"Aircraft Carrier": [0, 1, "h"], "Cruiser": [2, 3, "v"]}
    
    result_dict = json_to_dict(json_data)
    
    assert isinstance(result_dict, dict), "json_to_dict function does not return a dictionary"
    assert "Aircraft Carrier" in result_dict, "json_to_dict function does not contain correct keys"
    assert result_dict["Aircraft Carrier"] == [1, 0, "h"], "json_to_dict function does not contain correct values"
    assert "Cruiser" in result_dict, "json_to_dict function does not contain correct keys"
    assert result_dict["Cruiser"] == [3, 2, "v"], "json_to_dict function does not contain correct values"

    result_dict = json_to_dict("custom_board.JSON")

    assert isinstance(result_dict, dict), "json_to_dict function does not return a dictionary"
    assert "Aircraft Carrier" in result_dict, "json_to_dict function does not contain correct keys"
    assert result_dict["Aircraft Carrier"] == [0, 2, "v"], "json_to_dict function does not contain correct values"
    assert "Cruiser" in result_dict, "json_to_dict function does not contain correct keys"
    assert result_dict["Cruiser"] == [1, 6, "h"], "json_to_dict function does not contain correct values"
    with pytest.raises(json.JSONDecodeError):
        error = json_to_dict("tests/decode_error.JSON") # This should raise a JSONDecodeError
        assert error is None
    assert json_to_dict(8) is None

def test_is_valid_placement():
    """
    Test if the is_valid_placement function returns correct results.
    """
    test_board = [[None for i in range(10)] for i in range(10)]
    assert is_valid_placement(length=3, orientation="h", row=1, col=1, board=test_board), "is_valid_placement function returns incorrect result for horizontal placement"
    assert is_valid_placement(length=2, orientation="v", row=2, col=3, board=test_board), "is_valid_placement function returns incorrect result for vertical placement"
    assert not is_valid_placement(length=4, orientation="h", row=1, col=8, board=test_board), "is_valid_placement function returns incorrect result for invalid placement"
    test_board[0][0] = "Aircraft Carrier"
    assert not is_valid_placement(length=4, orientation="h", row=0, col=0, board=test_board), "is_valid_placement function returns incorrect result for invalid placement"
    assert not is_valid_placement(length=4, orientation="v", row=8, col=8, board=test_board), "is_valid_placement function returns incorrect result for invalid placement"
    assert not is_valid_placement(length=4, orientation="v", row=0, col=0, board=test_board), "is_valid_placement function returns incorrect result for invalid placement"

def test_place_battleships():
    """
    Test if the place_battleships function modifies the board correctly.
    """
    
    test_board_simple = [[None for i in range(5)] for i in range(5)]
    error_ships = {"Aircraft Carrier": 6, "Battleship":5, "Cruiser": 5,"Submarine":5, "Destroyer":5}
    assert place_battleships(test_board_simple, error_ships, algorithm="simple") == "Cannot fit the ships on the board! Increase board size or reduce no. of ships","place_battleships does not return an Error if the ships dont fit on the board in any configuration"
    test_ships_simple = {"Aircraft Carrier": 3, "Cruiser": 2}
    simple_placement = place_battleships(test_board_simple, test_ships_simple, algorithm="simple")
    assert simple_placement == [["Aircraft Carrier", "Aircraft Carrier", "Aircraft Carrier", None, None,],
                                ["Cruiser", "Cruiser", None, None, None],
                                [None, None, None, None, None],
                                [None, None, None, None, None],
                                [None, None, None, None, None]], "place_battleships function does not place ships correctly with 'simple' algorithm"
    
    test_board_random = [[None for i in range(5)] for i in range(5)]
    test_ships_random = {"Aircraft Carrier": 5, "Battleship":4, "Cruiser": 3}

    random_placement = place_battleships(test_board_random, test_ships_random, algorithm="random")
    assert isinstance(random_placement,list), "place_battleships with 'random' algorithm does not return list"
    assert count_ships_on_board(random_placement,"Aircraft Carrier") == 5

    test_board_custom = [[None for i in range(10)] for i in range(10)]
    test_ships_custom = {"Aircraft Carrier": 5, "Battleship":4, "Cruiser": 3,"Submarine":3, "Destroyer":2}

    result_board_custom = place_battleships(test_board_custom, test_ships_custom, algorithm="custom", custom_placement="custom_board.JSON")
    assert result_board_custom == [[None, None, 'Aircraft Carrier', None, None, None, None, None, None, None], 
                                    [None, None, 'Aircraft Carrier', None, None, None, 'Cruiser', 'Cruiser', 'Cruiser', None],
                                    [None, None, 'Aircraft Carrier', None, None, None, None, None, None, None], 
                                    [None, None, 'Aircraft Carrier', None, None, None, None, None, None, 'Destroyer'], 
                                    [None, None, 'Aircraft Carrier', None, None, None, None, None, None, 'Destroyer'], 
                                    [None, 'Submarine', None, None, None, None, None, None, None, None], 
                                    [None, 'Submarine', None, None, None, None, None, None, None, None], 
                                    [None, 'Submarine', None, None, None, 'Battleship', 'Battleship', 'Battleship', 'Battleship', None], 
                                    [None, None, None, None, None, None, None, None, None, None], 
                                    [None, None, None, None, None, None, None, None, None, None]], "place_battleships function does not place ships correctly with 'custom' algorithm"
    error_custom_board = place_battleships(test_board_custom, test_ships_custom, algorithm="custom", custom_placement="tests/error_custom_board.JSON")
    assert error_custom_board == ("Invalid Placement of Aircraft Carrier"), "place_battleships function does not correctly handle error placement"
    
def test_attack(capsys):
    """
    Test if the attack proccesses attacks correctly.
    """
    test_board = [[None for i in range(5)] for i in range(5)]
    test_ships = {"Aircraft Carrier": 4,"Cruiser": 2}
    coordinates = (2,0)
    test_board[0][0] = "Cruiser"
    test_board[0][1] = "Cruiser"
    
    hit, updated_board, updated_ships = attack(coordinates, test_board, test_ships)

    assert hit is False, "attack function not correctly registering missed attack"

    coordinates = (0,0)
    hit, updated_board, updated_ships = attack(coordinates, test_board, test_ships)

    assert hit == True, "attack function not correctly registering hit attack"
    assert updated_board == [[None, "Cruiser", None, None, None],
                                [None, None, None, None, None],
                                [None, None, None, None, None],
                                [None, None, None, None, None],
                                [None, None, None, None, None]], "attack function not correctly updating board after attack"
    assert updated_ships ==  {"Aircraft Carrier": 4,"Cruiser": 1}, "attack function not correctly updating ships dict after attack"
    coordinates = (1,0)
    hit, updated_board, updated_ships = attack(coordinates, test_board, test_ships)
    captured = capsys.readouterr()
    assert "Cruiser has been sunk!" in captured.out

def test_cli_coordinates_input(monkeypatch, capsys):
    """
    Test if the coordinate input function works correctly.
    """
    user_input_values = ["no","2","no", "3"]

    def mock_input(prompt):
        nonlocal user_input_values
        print(prompt, end="")
        value = user_input_values.pop(0)
        print(value)
        return value
    
    monkeypatch.setattr('builtins.input', mock_input)
    result = cli_coordinates_input()
    captured = capsys.readouterr()
    assert result == (2, 3)
    assert captured.out.count("Please enter a valid integer") == 2

def test_generate_attack():
    """
    Test if the attack generate function is working correctly for easy, medium and hard settings.
    """
    easy_attack = generate_attack(previous_attacks=None, board_size=10, difficulty="easy", previous_hits=None)
    assert isinstance(easy_attack, tuple)
    assert 0 <= easy_attack[0] < 10
    assert 0 <= easy_attack[1] < 10
    #make it so there is no space on the board and ensure none is returned
    full_attack_list = [(x, y) for x in range(10) for y in range(10)]
    failed_easy_attack = generate_attack(previous_attacks=full_attack_list, board_size=10, difficulty="easy", previous_hits=None)
    assert failed_easy_attack is None
    #make (0,0) the only possible attack and ensure that is picked
    almost_full_attack_list = full_attack_list
    almost_full_attack_list.remove((0,0))
    predictable_easy_attack = generate_attack(previous_attacks=almost_full_attack_list, board_size=10, difficulty="easy", previous_hits=None)
    assert predictable_easy_attack == (0,0)
    medium_attack = generate_attack(previous_attacks=None, board_size=10, difficulty="medium", previous_hits=None)
    assert isinstance(medium_attack, tuple)
    assert 0 <= medium_attack[0] < 10
    assert 0 <= medium_attack[1] < 10
    #make it so there is no space on the board and ensure none is returned
    full_attack_list = [(x, y) for x in range(10) for y in range(10)]
    failed_easy_attack = generate_attack(previous_attacks=full_attack_list, board_size=10, difficulty="medium", previous_hits=None)
    assert failed_easy_attack is None
    medium_attack_list = [(0,0), (4,4), (7,1)]
    medium_hits = [False, False, True]
    neighbours = [(7,0), (7,2), (6,1), (8,1)]
    predictable_medium_attack = generate_attack(previous_attacks=medium_attack_list, board_size=10, difficulty="medium", previous_hits=medium_hits)
    assert predictable_medium_attack in neighbours
    medium_attack_list = [(7,0), (7,2), (6,1), (8,1), (0,0), (4,4), (7,1)]
    medium_hits = [True, True, False, False, False, False, True]
    random_medium_attack = generate_attack(previous_attacks=medium_attack_list, board_size=10, difficulty="medium", previous_hits=medium_hits)
    assert random_medium_attack not in neighbours
    medium_hits = [True, True, False, False, False, False, False]
    random_medium_attack = generate_attack(previous_attacks=medium_attack_list, board_size=10, difficulty="medium", previous_hits=medium_hits)
    assert random_medium_attack not in medium_attack_list
    hard_attack = generate_attack(previous_attacks=None, board_size=10, difficulty="hard", previous_hits=None)
    assert isinstance(hard_attack, tuple)
    assert 0 <= hard_attack[0] < 10
    assert 0 <= hard_attack[1] < 10
    #make it so there is no space on the board and ensure none is returned
    full_attack_list = [(x, y) for x in range(10) for y in range(10)]
    failed_easy_attack = generate_attack(previous_attacks=full_attack_list, board_size=10, difficulty="hard", previous_hits=None)
    assert failed_easy_attack is None
    hard_attack_list = [(0,0), (4,4), (7,1)]
    hard_hits = [False, False, True]
    neighbours = [(7,0), (7,2), (6,1), (8,1)]
    predictable_hard_attack = generate_attack(previous_attacks=hard_attack_list, board_size=10, difficulty="hard", previous_hits=hard_hits)
    assert predictable_hard_attack in neighbours
    hard_attack_list = [(0,0), (4,4),(7,0), (7,1)]
    hard_hits = [False, False, True, True]
    predictable_hard_attack = generate_attack(previous_attacks=hard_attack_list, board_size=10, difficulty="hard", previous_hits=hard_hits)
    assert predictable_hard_attack == ((7,2))
    hard_attack_list = [(0,0), (4,4),(6,1), (7,1)]
    hard_hits = [False, False, True, True]
    predictable_hard_attack = generate_attack(previous_attacks=hard_attack_list, board_size=10, difficulty="hard", previous_hits=hard_hits)
    assert predictable_hard_attack in [(5,1),(8,1)]
    hard_attack_list = [(7,0), (7,2), (6,1), (8,1), (0,0), (4,4), (7,1)]
    hard_hits = [True, True, False, False, False, False, True]
    predictable_hard_attack = generate_attack(previous_attacks=hard_attack_list, board_size=10, difficulty="hard", previous_hits=hard_hits)
    assert predictable_hard_attack == ((7,3))
    hard_attack_list = [(7,3),(7,0), (7,2), (6,1), (8,1), (0,0), (4,4), (7,1)]
    hard_hits = [False, True, True, False, False, False, False, True]
    predictable_hard_attack = generate_attack(previous_attacks=hard_attack_list, board_size=10, difficulty="hard", previous_hits=hard_hits)
    assert predictable_hard_attack not in hard_attack_list


if __name__ == "__main__":
    test_create_battleships()
    test_json_to_dict()
    test_is_valid_placement()
    test_place_battleships()
    test_attack()
    test_cli_coordinates_input()
    test_generate_attack()
    print("All tests passed!")