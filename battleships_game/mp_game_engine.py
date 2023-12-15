"""The elements required to run a game of battleships against an ai opponent"""
import random
import logging
from components import initialise_board,create_battleships,place_battleships
from game_engine import cli_coordinates_input,attack

logging.basicConfig(filename="battleships.log", level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

players = {}


def generate_attack(previous_attacks=None, board_size=10, difficulty="easy", previous_hits=None):
    """Generates AI attack coordinates based on difficulty level and previous attacks.

    param previous_attacks: list of previous attack coordinates.
    param board_size: size of the game board.
    param difficulty: difficulty level ('easy', 'medium' or 'hard').
    param previous_hits: list of previous hit outcomes (True or False for Hit or Miss).

    return: the AI attack coordinates.
    """
    if previous_attacks is None:
        previous_attacks = []
    if previous_hits is None:
        previous_hits = []
    valid_coords = [(x, y) for x in range(board_size) for y in range(board_size)]
    available_coords = [(x, y) for x in range(board_size) for y in range(board_size)
                        if (x, y) not in previous_attacks]
    if difficulty == "easy":
        if not available_coords:
            logging.debug("No available coordinates for easy difficulty.")
            return None
        coordinates = random.choice(available_coords)
        return coordinates
    if difficulty == "medium":
        if not available_coords:
            logging.debug("No available coordinates for medium difficulty.")
            return None

        # If no previous attacks, make a random move
        if not previous_attacks:
            coordinates = random.choice(available_coords)
            return coordinates

        if previous_hits[-1]:
            #If the last shot was a hit, an adjacent point will be attacked if available
            x, y = previous_attacks[-1]
            neighbours = [(x - 1, y), (x, y - 1), (x + 1, y), (x, y + 1)]
            valid_neighbours = [i for i in neighbours if i in available_coords]
            if valid_neighbours:
                return random.choice(valid_neighbours)
            else:
                # If no valid neighbours, make a random move
                coordinates = random.choice(available_coords)
                return coordinates
        else:
            coordinates = random.choice(available_coords)
            return coordinates
    if difficulty == "hard":
        if not available_coords:
            logging.debug("No available coordinates for hard difficulty.")
            return None

        # If no previous attacks, make a random move
        if not previous_attacks:
            coordinates = random.choice(available_coords)
            return coordinates
        #creates a ditionary that has key of previous attacks (Tuple)
        #and value of if they were hit or miss (True or False)
        attack_dict = {previous_attacks[i]: previous_hits[i]
                        for i in range(len(previous_attacks))}
        coord_check = previous_attacks[-1]
        unchecked_hits = [key for key, value in attack_dict.items() if value]
        orientation = None
        #loops until it has checked the neighbours for all previous hits for a potential attack
        while unchecked_hits:
            coord_check = unchecked_hits[-1]
            x,y = coord_check
            hit_neighbours = [coord_check]
            neighbours = [(x - 1, y), (x, y - 1), (x + 1, y), (x, y + 1)]
            attacked_neighbours = [i for i in neighbours if i in previous_attacks]
            unattacked_neighbours = [i for i in neighbours if i in available_coords]
            #loops through all the attacked neighbours until we find one that has been hit
            for i in attacked_neighbours:
                if attack_dict[i]:
                    #if a attack was a hit on the same row, change orientation to horizontal
                    if x - i[0] == 0:
                        orientation = "h"
                        hit_neighbours.append(i)
                        break
                    #if a attack was a hit on the same column, change orientation to vertical
                    elif y - i[1] == 0:
                        orientation = "v"
                        hit_neighbours.append(i)
                        break
            # if there are no neighbours of the previous hit that have been attacked,
            # then attack a random neighbour
            else:
                coordinates = random.choice(unattacked_neighbours)
                return coordinates
            if orientation == "h":
                #check left coordinates
                current_y = y-1
                while (x,current_y) in valid_coords:
                    # if the left neighbour hasnt been attacked then attack it
                    if (x, current_y) in available_coords:
                        coordinates = (x,current_y)
                        return coordinates
                    # if the attack is a miss break out the loop
                    elif not attack_dict[(x,current_y)]:
                        break
                    # if the attack is a hit check the next left neighbour
                    elif (x, current_y) not in hit_neighbours and attack_dict[(x, current_y)]:
                        hit_neighbours.append((x, current_y))
                        current_y -= 1
                    # if the attack is a hit check the next left neighbour
                    elif attack_dict[(x,current_y)]:
                        current_y -= 1
                    else:
                        logging.error("Error - checked all possible scenarios and none were valid.")
                        break
                current_y = y+1
                while (x,current_y) in valid_coords:
                    if (x, current_y) in available_coords:
                        coordinates = ((x,current_y))
                        return coordinates
                    elif  not attack_dict[(x,current_y)]:
                        break
                    elif (x, current_y) not in hit_neighbours and attack_dict[(x, current_y)]:
                        hit_neighbours.append((x, current_y))
                        current_y += 1
                    elif attack_dict[(x,current_y)]:
                        current_y += 1
                    else:
                        logging.error("Error - checked all possible scenarios and none were valid.")
                        break

            if orientation == "v":
                #check above coordinates
                current_x = x-1
                while (current_x,y) in valid_coords:
                    # if the below neighbour hasnt been attacked then attack it
                    if (current_x, y) in available_coords:
                        coordinates = (current_x,y)
                        return coordinates
                    # if the attack is a miss break out the loop
                    elif  not attack_dict[(current_x,y)]:
                        break
                    # if the attack is a hit check the next below neighbour
                    elif (current_x, y) not in hit_neighbours and attack_dict[(current_x, y)]:
                        hit_neighbours.append((current_x, y))
                        current_x -= 1
                    # if the attack is a hit check the next below neighbour
                    elif attack_dict[(current_x,y)]:
                        current_x -= 1
                    else:
                        logging.error("Error - checked all possible scenarios and none were valid.")
                        break
                current_x = x+1
                while (current_x,y) in valid_coords:
                    if (current_x, y) in available_coords:
                        coordinates = (current_x,y)
                        return coordinates
                    elif not attack_dict[(current_x,y)]:
                        break
                    elif (current_x, y) not in hit_neighbours and attack_dict[(current_x, y)]:
                        hit_neighbours.append((current_x, y))
                        current_x += 1
                    elif attack_dict[(current_x,y)]:
                        current_x += 1
                    else:
                        print("Error")
                        logging.error("Error - checked all possible scenarios and none were valid.")
                        break
            for i in hit_neighbours:
                if i in unchecked_hits:
                    unchecked_hits.remove(i)

        #if it loops through the while loop and doesnt find any coordinates to attack.
        #Pick a random cooridinate
        coordinates = random.choice(available_coords)
        return coordinates
def ai_opponent_game_loop():
    """Runs a game loop for a game of battleships on the console with an ai opponent."""

    player1 = input("Ahoyhoy, Welcome to Battleships! \n What is your name?: ")
    board_size = 0
    while board_size < 6 or board_size > 10:
        try:
            board_size = int(input("What size would you like the board? (6-10):"))
        except ValueError:
            logging.warning("Invalid board size entered: %s", board_size)
            print("Please enter a number between (6-10)")
    difficulty = "custom"
    while difficulty not in ["easy", "medium", "hard"]:
        difficulty = input("What difficulty would you like? (easy, medium or hard):").lower()
    board_placement = "random"
    if difficulty == "easy":
        board_placement = "simple"
    player_ships = create_battleships()
    ai_ships = create_battleships()
    player_board = place_battleships(initialise_board(board_size), player_ships, algorithm="random")
    ai_board = place_battleships(initialise_board(board_size), ai_ships,algorithm=board_placement)
    players[player1] = [player_board,player_ships,[]]
    players["AI"] = [ai_board,ai_ships,[],[]]
    valid_coords = [(x, y) for x in range(board_size) for y in range(board_size)]
    ai_hit = False
    while True:
        attack_coordinates = cli_coordinates_input()
        if attack_coordinates in players[player1][2]:
            print("You have already attacked here! Please enter new coordinates")
            continue
        elif attack_coordinates not in valid_coords:
            print(f"Please enter coordinates between 0-{board_size - 1}")
            continue
        else:
            players[player1][2].append(attack_coordinates)
        print(f"{player1} attack: ")
        attack(attack_coordinates,players["AI"][0],players["AI"][1])
        logging.info("%s has attacked coordinates %s.", player1, attack_coordinates)
        if sum(players["AI"][1].values()) == 0:
            logging.info("Game Over, {player1} wins!", player1=player1)
            print(f"Game Over, {player1} wins!")
            break
        ai_attack_coordinates = generate_attack(players["AI"][2],board_size,
                                difficulty=difficulty, previous_hits=players["AI"][3])
        logging.info("AI has attacked coordinates %s.", ai_attack_coordinates)
        players["AI"][2].append(ai_attack_coordinates)
        print("\nAI attack: ")
        ai_hit, players[player1][0], players[player1][1] = attack(ai_attack_coordinates,
                                                            players[player1][0],players[player1][1])
        players["AI"][3].append(ai_hit)
        if sum(players[player1][1].values()) == 0:
            logging.info("Game Over, the robot wins.")
            print("Game Over, the robot wins again...")
            break

if __name__ == "__main__":
    ai_opponent_game_loop()
