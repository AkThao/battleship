import time
from random import randint, choice

##############################################################################
#### DEFINE SHIP CLASS THAT STORES SIZE AND POSITIONS OF EACH SHIP OBJECT ####
##############################################################################
class Ship():
    def __init__(self, id):
        self.size = None
        self.positions = []
        self.x = None
        self.y = None
        self.id = id
        self.ship_size = None # This is actually (true length - 1) because it doesn't account for starting position

    def pick_random_point(self, used_pos, max_size):
        exclude = [pos[:2] for pos in used_pos]
        [self.x, self.y] = [randint(0, max_size - 1), randint(0, max_size - 1)]
        return self.pick_random_point(used_pos, max_size) if [self.y, self.x] in exclude else [self.x, self.y]

    def place_on_board(self, used_pos, max_size, board):
        # Pick random starting coordinate for ship, as long as coordinate is not already occupied
        [self.x, self.y] = self.pick_random_point(used_pos, max_size)

        used_pos.append([self.y, self.x, self.id])
        self.positions.append([self.y, self.x])
        coords = [pos[:2] for pos in used_pos]
        #### SHIP PLACEMENT ALGORITHM ####
        # Check in NSEW directions to see how much space there is for ship
        # This will be space between ship start and nearest occupied position
        # Out of the available directions, choose direction that allows for longest ship
        # If there are multiple directions of the maximum amount of space, just pick the first one (max() does this)
        # Set the size of the ship to be a random size that will fit in that direction

        spaces = {
        "east_spaces" : 0,
        "west_spaces" : 0,
        "north_spaces" : 0,
        "south_spaces" : 0
        }

        # Check North direction
        for i in range(self.y, 0, -1):
            if [i - 1, self.x] not in coords:
                spaces["north_spaces"] += 1
            else:
                break

        # Check East direction
        for i in range(self.x, len(board) - 1):
            if [self.y, i + 1] not in coords:
                spaces["east_spaces"] += 1
            else:
                break

        # Check South direction
        for i in range(self.y, len(board) - 1):
            if [i + 1, self.x] not in coords:
                spaces["south_spaces"] += 1
            else:
                break

        # Check West direction
        for i in range(self.x, 0, -1):
            if [self.y, i - 1] not in coords:
                spaces["west_spaces"] += 1
            else:
                break

        # Choose direction for ship
        max_space = max(spaces.items(), key = lambda x : x[1])
        # spaces.items() returns an iterable containing tuples of direction and space in that direction

        # Now that we have found the direction with the most space, extend the ship length in that direction
        self.ship_size = randint(0, max_space[1])
        if self.ship_size == 0:
            return used_pos

        if max_space[0] == "north_spaces":
            for i in range(self.y, self.y - self.ship_size, -1):
                used_pos.append([i - 1, self.x, self.id])
                self.positions.append([i - 1, self.x])

        elif max_space[0] == "east_spaces":
            for i in range(self.x, self.x + self.ship_size):
                used_pos.append([self.y, i + 1, self.id])
                self.positions.append([self.y, i + 1])

        elif max_space[0] == "south_spaces":
            for i in range(self.y, self.y + self.ship_size):
                used_pos.append([i + 1, self.x, self.id])
                self.positions.append([i + 1, self.x])

        elif max_space[0] == "west_spaces":
            for i in range(self.x, self.x - self.ship_size, -1):
                used_pos.append([self.y, i - 1, self.id])
                self.positions.append([self.y, i - 1])

        return used_pos

class Game():
    def __init__(self):
        self.board_size = None
        self.board = None
        self.user_x = None
        self.user_y = None
        self.intro_on = 1
        self.num_ships = None
        self.ships = []
        self.ship_positions = []
        self.ship_hits = [] # How many ships have been hit
        self.ids = [] # IDs of all ships
        self.sunk = [] # Whether or not ships have been sunken
        self.ship_coords = [] # Same as ship_positions, but without the IDs
        self.won = None
        self.hit = None # Has a ship been hit?
        self.user_moves = [] # All the moves the user has taken

    def intro(self):
        print("""
**********************
** Battleship Game! **
**********************
""")
        self.intro_on = 0

    def initialise_board(self):
        print("\nCreating board....")
        self.board = [[0 for x in range(self.board_size)] for y in range(self.board_size)]
        time.sleep(0.5)

    def draw_board(self):
        # Draw a game board with the specified dimensions
        time.sleep(0.5)
        print("\n")
        print("   |", end="")
        for i in range(self.board_size):
            print(f" {str(chr(65 + i))} |", end="")
        print("")
        for j in range(self.board_size):
            print("___" + "____" * self.board_size)
            print(f"{j + 1:2} |",  end="")
            for k in range(self.board_size):
                print(f" {self.board[j][k]} |", end="")
            print("")
        print("\n")

    def update_board(self, symbol):
        self.board[self.user_y][self.user_x] = symbol

    def choose_x_position(self):
        time.sleep(0.5)
        # Range of acceptable letters
        lower_case = range(ord('a'), ord(chr(ord('a') + self.board_size)))
        upper_case = range(ord('A'), ord(chr(ord('A') + self.board_size)))

        # Accept value of x coordinate
        self.user_x = input(f"Choose the x coordinate of your next move (A - {str(chr(65 + self.board_size - 1))}): ")
        if any(char.isdigit() for char in self.user_x) or len(self.user_x) != 1:
            print("\nInput must be a single letter, try again.\n")
            time.sleep(1)
            self.choose_x_position()
        elif ord(self.user_x) not in lower_case and ord(self.user_x) not in upper_case:
            print("\nInput is outside range, try again.\n")
            time.sleep(1)
            self.choose_x_position()
        else:
            self.user_x = self.user_x.upper()
            self.user_x = ord(self.user_x) - 65

    def choose_y_position(self):
        # Accept value of y coordinate
        self.user_y = input(f"Choose the y coordinate of your next move (1 - {self.board_size}): ")
        if self.user_y.isdigit() == False:
            print("\nInput must be a number, try again.\n")
            time.sleep(1)
            self.choose_y_position()
        elif int(self.user_y) not in range(1, self.board_size + 1):
            print("\nInput is outside range, try again.\n")
            time.sleep(1)
            self.choose_y_position()
        else:
            self.user_y = int(self.user_y)
            self.user_y = self.user_y - 1

    def create_enemy_ships(self):
        # Create hidden enemy ships at a random positions and in random orientations on the board
        self.num_ships = self.board_size # Arbitrary but reasonable
        self.ships = [None] * self.num_ships
        # Make a list of ship objects using the Ship class
        for i in range(self.num_ships):
            self.ships[i] = Ship("id_" + str(i + 1))
        # For each ship object, create a number of positions the ship will occupy and add them to self.ship_positions
        for ship in self.ships:
            self.ship_positions = ship.place_on_board(self.ship_positions, self.board_size, self.board)
        """for position in self.ship_positions: # TESTING
                                    self.board[position[0]][position[1]] = position[2].lstrip("id_") # TESTING"""

        for ship in self.ships:
            self.ids.append(len(ship.positions))

        self.ship_hits = [0] * len(self.ids)
        self.sunk = [0] * len(self.ids)
        self.ship_coords = [pos[:2] for pos in self.ship_positions]

    def check_for_repeat_position(self, turns):
        if [self.user_x, self.user_y] in self.user_moves:
            if turns == 1:
                print("\nYou have already chosen this position.\n")
                time.sleep(1)
                return True
            else:
                print("\nYou have already chosen this position, choose another one.\n")
                time.sleep(1)
                return True
        return False

    def check_for_enemy_hit(self):
        #### SHIP HIT DETECTION ALGORITHM ####
        # Make a list with length = self.num_ships
        # Each element will be the number of times a ship position of a particular id has been hit
        # The list will begin with all elements equal to 0
        # When a full ship has been hit, its element in this list will be equal to ship.ship_size + 1
        # When a ship has been hit, rather than placing an 'X' on the board, place some other unique identifier
        if [self.user_y, self.user_x] in self.ship_coords:
            print("\nYou have scored a hit!")
            index = self.ship_coords.index([self.user_y, self.user_x])
            id = int(self.ship_positions[index][2].lstrip("id_"))
            self.ship_hits[id - 1] += 1
            self.hit = 1
            self.update_board(str(id))


        for i in range(len(self.ship_hits)):
            if self.ship_hits[i] == self.ids[i] and self.sunk[i] == 0:
                print(f"\nYou have sunken ship {i + 1}!")
                self.sunk[i] = 1

        if self.ids == self.ship_hits:
            print(f"\nYou have sunken all ships!")
            self.won = 1

        if self.hit:
            self.hit = 0
            return True
        return False


    def win(self):
        time.sleep(1)
        print("\nCongratulations! You have won the game!\n")

    def game_over(self):
        time.sleep(1)
        print("\nGame over! You have failed to sink all ships.\n")


def game_loop():
    game.draw_board()
    game.create_enemy_ships()
    turns = len(game.ship_positions) + game.board_size
    game.won = 0
    while turns >= 0:
        if turns == 0:
            game.game_over()
            break
        if game.won:
            game.win()
            break
        print(f"Turns = {turns}")
        game.choose_x_position()
        game.choose_y_position()
        if game.check_for_repeat_position(turns):
            # turns -= 1
            continue
        if game.check_for_enemy_hit():
            game.draw_board()
            game.user_moves.append([game.user_x, game.user_y])
            turns -= 1
            continue
        game.update_board("*")
        game.draw_board()
        game.user_moves.append([game.user_x, game.user_y])
        turns -= 1

def main():
    if game.intro_on:
        game.intro()
    time.sleep(1)
    try:
        desired_size = int(input("Enter the desired dimension of the board (between 5 and 26)\nE.g. Enter 5 for a 5x5 board: "))
    except ValueError:
        print("\nInvalid input, try again.\n")
        time.sleep(1)
        main()
        return
    if (desired_size < 5 or desired_size > 26):
        print("\nBoard size must be between 5 and 26.\n")
        time.sleep(1)
        main()
    else:
        game.board_size = desired_size
        game.initialise_board()
        game_loop()

if __name__ == "__main__":
    game = Game()
    main()