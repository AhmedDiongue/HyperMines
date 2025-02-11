

import sys
sys.setrecursionlimit(10000)
# NO ADDITIONAL IMPORTS


class HyperMinesGame:
    def __init__(self, dimensions, bombs):
        """Start a new game.

        This method should properly initialize the "board", "mask",
        "dimensions", and "state" attributes.

        Args:
           dims (list): Dimensions of the board
           bombs (list): Bomb locations as a list of lists, each an
                         N-dimensional coordinate

        >>> g = HyperMinesGame([2, 4, 2], [[0, 0, 1], [1, 0, 0], [1, 1, 1]])
        >>> g.dump()
        dimensions: [2, 4, 2]
        board: [[3, '.'], [3, 3], [1, 1], [0, 0]]
               [['.', 3], [3, '.'], [1, 1], [0, 0]]
        mask:  [[False, False], [False, False], [False, False], [False, False]]
               [[False, False], [False, False], [False, False], [False, False]]
        state: ongoing
        """
                
        self.dimensions = dimensions
        board = self.make_board(dimensions, bombs)
        self.board = board
        self.mask = self.init_N_dim_array(dimensions, False)
        self.state = "ongoing"


    def init_N_dim_array(self, dimensions, init_val):
        """
        Initialize an N-dimensional empty array with value init_val.
        Args:
            dimensions (list): [d_0,...,d_k], k = N-1, specifies the dimensions of the array
            init_val (boolean or int): the initial value in this N-dim array

        Return:
            array (list): N-dimensional array with init_val
            
        >>> game = HyperMinesGame([3,3,2],[[1,2,0]])
        >>> game.init_N_dim_array(game.dimensions,0)
        [[[0, 0], [0, 0], [0, 0]], [[0, 0], [0, 0], [0, 0]], [[0, 0], [0, 0], [0, 0]]]
        """
        if len(dimensions) == 0:
            return init_val
        return [self.init_N_dim_array(dimensions[1:],init_val) for j in range(dimensions[0])]

    def get_item(self, coords, array):
        """Get the value of a square or its mask at the given coordinates on the board.

        (Optional) Implement this method to return the value of a square or its mask at the given
        coordinates.

        Args:
            coords (list): Coordinates of the square

        Returns:
            any: Value of the square
        """
        if len(coords) == 1:
            return array[coords[0]]
        else:
            return self.get_item(coords[1:], array[coords[0]])

    
    def set_item(self, coords, array, value):
        """Set the value of a square or its mask at the given coordinates on the board.

        (Optional) Implement this method to set the value of a square or its mask at the given
        coordinates.

        Args:
            coords (list): Coordinates of the square
        """
        def recurse_set(sub_coords, sub_array, value):
            #base case - 
            if len(sub_coords) == 1:
                sub_array[sub_coords[0]] = value
            else:#recursive case
                recurse_set(sub_coords[1:], sub_array[sub_coords[0]], value)     
        recurse_set(coords, array, value)
        return array  
    
    def make_board(self, dimensions, bombs):
        # Base case: when we have just one dimension left

        board = self.init_N_dim_array(dimensions, 0)

        for bomb_coords in bombs:
            self.set_item(bomb_coords, board, '.')
        
        for bomb in bombs:
            for neighbor in self.neighbors(bomb):
                x = self.get_item(neighbor, board)
                if x != ".":
                    x = self.set_item(neighbor, board, x+1)
        return board
    def get_all_coord(self, dimensions):
        """
        Return the list of all coordinates with given dimensions
        
        Args:
            dimensions (list): dimensions of the board
            
        Return:
            (list): list of all coordinates in the board
        
        >>> game = HyperMinesGame([2,3],[[1,2]])
        >>> game.get_all_coord([2,3])
        [[0, 0], [1, 0], [0, 1], [1, 1], [0, 2], [1, 2]]
        
        """
        if len(dimensions) == 0:
            return [[]]
        d_i = dimensions[0]
        new_coord = []
        for prev_coord in self.get_all_coord(dimensions[1:]):
            for i in range(d_i):
                new_coord.append([i]+prev_coord)
        return new_coord
    def is_in_bounds(self, coords):
        """Return whether the coordinates are within bound

        (Optional) Implement this method to check boundaries for N-Dimensional boards.

        Args:
            coords (list): Coordinates of a square

        Returns:
            boolean: True if the coordinates are within bound and False otherwise
        """

        is_in_bounds = True
        bounds_bool = [0 <= x < self.dimensions[i] for i, x in enumerate(coords)]
        for bool in bounds_bool:
            if bool == False:
                is_in_bounds = False
                return is_in_bounds
        return is_in_bounds

    def neighbors(self, coords):
        """Return a list of the neighbors of a square

        Args:
            coords (list): List of coordinates for the square (integers)

        Returns:
            list: coordinates of neighbors
        """
        def generate_neighbors(current_coords, dimensions=0):
            # Base case: iterated through all of the dimensions
            if dimensions == len(coords):
                if current_coords != coords:
                    return [current_coords]
                return []
            
            neighbors = []
            for offset in [-1, 0, 1]:
                # Create a new list for the next recursive call
                new_coords = current_coords[:]
                new_coords[dimensions] = coords[dimensions] + offset
                # Recursive call
                results = generate_neighbors(new_coords, dimensions + 1)
                neighbors.extend(results)
            
            return neighbors

        # Start recursion with a copy of coordinates
        all_neighbors = generate_neighbors(coords[:])
        return [n for n in all_neighbors if self.is_in_bounds(n)]

    def is_victory(self): 
            """Returns whether there is a victory in the game.

            A victory occurs when all non-bomb squares have been revealed.
            (Optional) Implement this method to properly check for victory in an N-Dimensional board.

            Returns:
                boolean: True if there is a victory and False otherwise
            """
            
            def check_squares(board, mask):
                if not isinstance(board, list):
                    return not ((board == '.' and mask) or (board != '.' and not mask))
                
                return all(check_squares(b, m) for b, m in zip(board, mask))
            
            return check_squares(self.board, self.mask)


    def dig(self, coords):
        """Recursively dig up square at coords and neighboring squares.

        Update the mask to reveal square at coords; then recursively reveal its
        neighbors, as long as coords does not contain and is not adjacent to a
        bomb.  Return a number indicating how many squares were revealed.  No
        action should be taken and 0 returned if the incoming state of the game
        is not "ongoing".

        The updated state is "defeat" when at least one bomb is visible on the
        board after digging, "victory" when all safe squares (squares that do
        not contain a bomb) and no bombs are visible, and "ongoing" otherwise.

        Args:
           coords (list): Where to start digging

        Returns:
           int: number of squares revealed

        >>> g = HyperMinesGame.from_dict({"dimensions": [2, 4, 2],
        ...         "board": [[[3, '.'], [3, 3], [1, 1], [0, 0]],
        ...                   [['.', 3], [3, '.'], [1, 1], [0, 0]]],
        ...         "mask": [[[False, False], [False, True], [False, False], [False, False]],
        ...                  [[False, False], [False, False], [False, False], [False, False]]],
        ...         "state": "ongoing"})
        >>> g.dig([0, 3, 0])
        8
        >>> g.dump()
        dimensions: [2, 4, 2]
        board: [[3, '.'], [3, 3], [1, 1], [0, 0]]
               [['.', 3], [3, '.'], [1, 1], [0, 0]]
        mask:  [[False, False], [False, True], [True, True], [True, True]]
               [[False, False], [False, False], [True, True], [True, True]]
        state: ongoing
        >>> g = HyperMinesGame.from_dict({"dimensions": [2, 4, 2],
        ...         "board": [[[3, '.'], [3, 3], [1, 1], [0, 0]],
        ...                   [['.', 3], [3, '.'], [1, 1], [0, 0]]],
        ...         "mask": [[[False, False], [False, True], [False, False], [False, False]],
        ...                  [[False, False], [False, False], [False, False], [False, False]]],
        ...         "state": "ongoing"})
        >>> g.dig([0, 0, 1])
        1
        >>> g.dump()
        dimensions: [2, 4, 2]
        board: [[3, '.'], [3, 3], [1, 1], [0, 0]]
               [['.', 3], [3, '.'], [1, 1], [0, 0]]
        mask:  [[False, True], [False, True], [False, False], [False, False]]
               [[False, False], [False, False], [False, False], [False, False]]
        state: defeat
        """
        
        def recurse_dig(coords, mask): 
            """Recursively dig cells around a zero cell
            Parameters:
               mask (list of lists): indicates whether the contents of square (row,col) are visible to the player
               coords (int): where to start digging
            return: 
               int: the number of new squares revealed 
            """
            neighbors = self.neighbors(coords)
            count = 1
            if self.get_item(coords, mask) == False:
                mask = self.set_item(coords,mask, True)
                if self.get_item(coords,self.board) == 0:
                    for nghb_coord in neighbors:
                        if self.get_item(nghb_coord,self.board) != '.':
                            count += recurse_dig(nghb_coord,mask)
                return count
            return 0
        
        # if this dig is trivial
        if self.state == "defeat" or self.state == "victory" or self.get_item(coords, self.mask):
            return 0
        
        # reveals a bomb
        if self.get_item(coords, self.board) == '.':           
            self.mask = self.set_item(coords, self.mask, True)
            self.state = 'defeat'
            return 1
        
        # reveals a nonzero cell
        count = 1
        mask = self.mask[:]
        if self.get_item(coords, self.board) != 0:
            self.mask = self.set_item(coords, mask, True)
        
        # reveals a zero cell
        else:                            
            neighbors = self.neighbors(coords)            
            count = recurse_dig(coords,mask)
            
        self.state = 'victory' if self.is_victory() else 'ongoing'
        return count


    def render(self, xray=False):
        """Prepare the game for display.

        Returns an N-dimensional array (nested lists) of "_" (hidden squares),
        "." (bombs), " " (empty squares), or "1", "2", etc. (squares
        neighboring bombs).  The mask indicates which squares should be
        visible.  If xray is True (the default is False), the mask is ignored
        and all cells are shown.

        Args:
        xray (bool): Whether to reveal all tiles or just the ones allowed by
                        the mask

        Returns:
        An n-dimensional array (nested lists)

        >>> g = HyperMinesGame.from_dict({"dimensions": [2, 4, 2],
        ...            "board": [[[3, '.'], [3, 3], [1, 1], [0, 0]],
        ...                      [['.', 3], [3, '.'], [1, 1], [0, 0]]],
        ...            "mask": [[[False, False], [False, True], [True, True], [True, True]],
        ...                     [[False, False], [False, False], [True, True], [True, True]]],
        ...            "state": "ongoing"})
        >>> g.render(False)
        [[['_', '_'], ['_', '3'], ['1', '1'], [' ', ' ']],
        [['_', '_'], ['_', '_'], ['1', '1'], [' ', ' ']]]

        >>> g.render(True)
        [[['3', '.'], ['3', '3'], ['1', '1'], [' ', ' ']],
        [['.', '3'], ['3', '.'], ['1', '1'], [' ', ' ']]]
        """
        render_board = self.init_N_dim_array(self.dimensions,0)
        dims = self.dimensions
        coords = self.get_all_coord(dims)
        for coord in coords:
            val = self.get_item(coord, self.board)
            if (not xray) and (not self.get_item(coord, self.mask)):
                new_val = '_'                
            else:
                if val == 0:
                    new_val = ' '
                else:
                    new_val = str(val)
            render_board = self.set_item(coord, render_board, new_val)    
        return render_board

    # ***Methods below this point are for testing and debugging purposes only. Do not modify anything here!***

    def dump(self):
        """Print a human-readable representation of this game."""
        lines = ["dimensions: %s" % (self.dimensions, ),
                 "board: %s" % ("\n       ".join(map(str, self.board)), ),
                 "mask:  %s" % ("\n       ".join(map(str, self.mask)), ),
                 "state: %s" % (self.state, )]
        print("\n".join(lines))

    @classmethod
    def from_dict(cls, d):
        """Create a new instance of the class with attributes initialized to
        match those in the given dictionary."""
        game = cls.__new__(cls)
        for i in ('dimensions', 'board', 'state', 'mask'):
            setattr(game, i, d[i])
        return game
