########### this section for debug purposes only ###########
import sys

def print_even(maze_row, dir):
    for cell in maze_row:
        if cell[dir]:
            sys.stdout.write('+--')
        else:
            sys.stdout.write('+  ')
    print '+'

def print_odd(maze_row):
    for cell in maze_row:
        space = '   '
        if cell['Left']:
            space = '|  '
        if cell['visited']:
            space = space[0] + 'x '
        sys.stdout.write(space)
    if maze_row[-1]['Right']:
        print '|'
    else:
        print ''

# prints out the maze in the original ascii format,
# plus x-es for visited locatiions
def print_ascii_maze(maze):
    print_even(maze[0], 'Up')
    for row in maze:
        print_odd(row)
        print_even(row, 'Down')

######### start of actual solution ##############

# helper method to read in the odd rows (the ones representing actual cells)
def read_odd_row(line, maze_row):
    for i in xrange(len(line)/3 + 1):
        is_wall = line[i*3] == '|'
        if i < len(maze_row):
            maze_row[i]['Left'] = is_wall
        if i != 0:
            maze_row[i-1]['Right'] = is_wall
    return maze_row

# helper method to read in the even rows (the ones in-between cells)
def read_even_row(line, prev_maze_row):
    maze_row = []
    for i in xrange(len(line)/3):
        is_wall = (line[i*3+1] == '-')
        maze_row.append(create_maze_cell(is_wall))
        if prev_maze_row:
            prev_maze_row[i]['Down'] = is_wall
    return maze_row

# each cell has a boolean for whether there's a wall to the north, south, east,
# and west.  I used "up/down/left/right" for ease of converting it to the final
# output.
# True means there's a wall, false means no wall.
def create_maze_cell(up):
    return {
        'Up' : up,
        'Down' : False,
        'Right' : False,
        'Left' : False,
        'visited' : False
    }

# Read in the maze, a line at a time.
# Each time you're on a wall row, start a new row, filling in the correct values
# for everything other than up on later lines.  This does lead to the kludge-y
# issue of adding an extra row at the very end since I fill in the downs as I
# make the new up, but it's easily fixed by removing that last row when I'm done
def read_maze(filename):
    maze = []
    with open(filename) as fp:
        even_line = True
        prev_maze_row = None
        for line in iter(fp.readline, ''):
            if even_line:
                maze_row = read_even_row(line, prev_maze_row)
                maze.append(maze_row)
                prev_maze_row = maze_row
            else:
                prev_maze_row = read_odd_row(line, prev_maze_row)
            even_line = not even_line
    # remove spurious last row, created by read_even_row
    del maze[-1]
    return maze

# convenience dict to move in the right direction for each name
x_y_from_direction = {
    'Up' : {'x': 0, 'y': -1},
    'Down' : {'x': 0, 'y': 1},
    'Right' : {'x': 1, 'y': 0},
    'Left' : {'x': -1, 'y': 0}
}

# convenience method to check that if we go in the given direction, we'll still
# be in bounds and not covering old ground
def in_maze_unvisited(maze, x_y, r, c):
    new_r = r + x_y['y']
    new_c = c + x_y['x']
    if new_r < 0 or new_r >= len(maze) or new_c < 0 or new_c >= len(maze[0]):
        return False
    return not maze[new_r][new_c]['visited']

# make a deep copy of the path up til now (so that if we try multiple
# directions from a given location, they don't clobber each other)
def new_path_with_dir(path, dir):
    new_path = list(path)
    new_path.append(dir)
    return new_path

# recursively walk in every direction open to you from each point, marking your
# progress as you go and returning if you find yourself at the goal position
def solve_maze_rec(maze, r, c, path):
    if (r == len(maze) - 1) and (c == len(maze[0]) - 1):
        return path
    # we've been here, so mark it before moving on
    maze[r][c]['visited'] = True
    # try all the directions from here
    for key in x_y_from_direction:
        # make sure there's no wall
        if not maze[r][c][key]:
            x_y = x_y_from_direction[key]
            # make sure there's a valid cell that way
            if in_maze_unvisited(maze, x_y, r, c):
                # try going that way, adding the direction we went to the path!
                result = solve_maze_rec(maze, r + x_y['y'], c + x_y['x'],
                    new_path_with_dir(path, key))
                # if we got back a real path, pass it back up! if we fail, we'll
                # get None and this won't trigger
                if result:
                    return result

# the path we built up in the solve method goes through each individual step,
# and we want to combine multiple steps in the same direction
def condense_path(path):
    condensed_path = []
    prev = None
    count = 0
    # Keep track of what we saw most recently and how many times we saw it.
    # Once we see something different, print out the last thing.
    for direction in path:
        if prev == direction:
            count += 1
        else:
            # if we had seen something else before this, print it!
            if prev:
                condensed_path.append(prev + ' ' + str(count))
            prev = direction
            count = 1
    # add in the last one
    condensed_path.append(prev + ' ' + str(count))
    return condensed_path

# read in, solve, then pretty-print the solution
def main():
    maze = read_maze('maze.txt')
    # printed here to make it easier to trace and verify
    print_ascii_maze(maze)
    path = solve_maze_rec(maze, 0, 0, [])
    for step in condense_path(path):
        print step

if __name__ == "__main__":
    main()
