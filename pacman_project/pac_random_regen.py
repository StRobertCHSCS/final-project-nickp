"""
Name: pacman.py
Purpose: To play the original pacman arcade game being coded with slight modifications to the original game

Author: Palmar.N

Created: 09/06/2019
"""

# import libraries
import arcade
import random

WIDTH = 1240
HEIGHT = 680

# tile dimension; wall fits to tile
tile_width = 40
tile_height = 40

# pellet dimension
pellet_dim = 10
super_pellet_dim = 20
super_pellet_capture = [False]*4

# create grid variables
pac_grid = []
row_count = 15
column_count = 31
grid_draw = 0

# pacman variables
pac_x = 620
pac_y = 60
pac_rad = 20
init_arc_angle = 0
final_arc_angle = 360
pac_skin = 0

# arrow key variables
up_pressed = False
down_pressed = False
left_pressed = False
right_pressed = False
pac_speed_x = 0
pac_speed_y = 0

# time variable
time_1 = 0
time_2 = 0
time_bar_width = 240
time_bar_height = 40
chase_time = 8
init_time_bar_width = 240

#  score variables
score = 0

# ghost variables
ghost_x1 = 780
ghost_y1 = 220
ghost_x2 = 780
ghost_y2 = 420
ghost_x3 = 540
ghost_y3 = 420
ghost_speeds = [[0, 0], [0, 0], [0, 0]]
ghost_change_skin = False
ghost_rand_x = [500, 740]
ghost_rand_y = [180, 300, 420]

# play status variables
lose = False
win = False


def on_update(delta_time):
    """ Update any logical this in the code here; continous loop

    :param delta_time: time which starts counting when the program starts
    :return: none
    """
    global pac_x, pac_y, time_1, pac_speed_x, pac_speed_y, ghost_x1, ghost_y1, ghost_x2, ghost_y2, time_2
    global ghost_change_skin, ghost_x3, ghost_y3, chase_time, time_bar_width

    wall_touch_pac = wall_collision(pac_x, pac_y)
    pac_move(wall_touch_pac)
    pac_object_detection(pac_x, pac_y)
    pac_win_lose(pac_x, pac_y)

    # check the walls the ghosts are in contact with
    wall_touch_ghost1 = wall_collision(ghost_x1, ghost_y1)
    wall_touch_ghost2 = wall_collision(ghost_x2, ghost_y2)
    wall_touch_ghost3 = wall_collision(ghost_x3, ghost_y3)

    # random ghost 2 motion; unable to go through walls
    ghost_chase_rand2(wall_touch_ghost2)

    if ghost_change_skin == False:
        # control ghost 1 motion; super ghost can move through walls
        ghost_chase1(wall_touch_ghost1)
        # random ghost 3 motion; unable to go through walls, slight attraction to pacman
        ghost_chase_rand3(wall_touch_ghost3)
        time_bar_width = init_time_bar_width

    else:
        # if pacman had super coin, move away
        ghost_x1, ghost_y1 = ghost_repel(0, ghost_x1, ghost_y1, wall_touch_ghost1)
        ghost_x3, ghost_y3 = ghost_repel(2, ghost_x3, ghost_y3, wall_touch_ghost3)

    # open and close pac mans mouth; flash super pellets
    time_1 += delta_time
    if time_1 >= 0.075:
        change_skin()
        flash_super_pellet()
        time_1 = 0

    # change ghosts back to blue
    if ghost_change_skin == True:
        time_2 += delta_time
        if time_2 >= chase_time:
            ghost_change_skin = False
            time_2 = 0


def on_draw():
    """ Draw everything here; continous loop

    :return: none
    """
    global pac_grid, row_count, column_count, tile_width, tile_height, pac_x, pac_y, score, time_2
    global ghost_x1, ghost_y1, ghost_x2, ghost_y2, ghost_x3, ghost_y3, WIDTH, HEIGHT, ghost_change_skin
    global lose, win

    arcade.start_render()
    draw_maze()

    # draw pacman
    draw_pac(pac_x, pac_y)

    # draw ghosts
    if ghost_change_skin == False:
        draw_ghost(ghost_x1, ghost_y1)
        draw_ghost(ghost_x2, ghost_y2)
        draw_ghost(ghost_x3, ghost_y3)
        # draw the time number as the chase time
        draw_time_num(chase_time)
    else:
        # if super pellet, change color
        change_ghost(ghost_x1, ghost_y1)
        change_ghost(ghost_x2, ghost_y2)
        change_ghost(ghost_x3, ghost_y3)
        # draw the time number
        draw_time_num(chase_time-time_2)

    # draw the score
    write_score(score)

    # write the ghost chase message
    write_ghost_chase("Ghost Chase Time: ")

    # if player loses, display message
    if lose == True:
        arcade.draw_text("YOU LOSE", WIDTH//2 - (7*tile_width), HEIGHT//2 - (2*tile_width), arcade.color.RED_DEVIL, 100)
    elif win == True:
        arcade.draw_text("YOU WIN", WIDTH//2 - (7*tile_width), HEIGHT//2 - (2*tile_width), arcade.color.SKY_BLUE, 100)


def change_ghost(x, y):
    """ When the super pellet is collected, change the ghost's skin/costume

    :param x: x position of ghost
    :param y: y position of ghost
    :return: none
    """
    global tile_width, tile_height, texture_ghost_change
    arcade.draw_texture_rectangle(x, y, tile_width, tile_height, texture_ghost_change, 0)


def draw_time_num(time):
    """ Write how long is left for the chase

    :param time: Time to output
    :return: none
    """
    # writ the time slightly moved over from the time message
    round_time = round(time, 2)
    arcade.draw_text(str(round_time), 975, 630, arcade.color.ORANGE, 20)


def write_ghost_chase(message):
    """ Add the caption to the time bar

    :param message: String message to be outputted to the screen
    :return: nothing
    """
    # display the message
    x = 760
    y = 630
    arcade.draw_text(message, x, y, arcade.color.WHITE, 20)


def draw_ghost(x, y):
    """ Draw a ghost to the screen

    :param x: x position of ghost
    :param y: y position of ghost
    :return: none
    """
    global tile_width, tile_height, texture_ghost
    arcade.draw_texture_rectangle(x, y, tile_width, tile_height, texture_ghost, 0)


def draw_maze():
    """ Draw the maze to the screen depending on the status of pac_grid

    :return: none
    """
    global tile_width, tile_height, pac_grid, grid_draw, super_pellet_capture

    # draw out the current grid
    for row in range(row_count):
        for column in range(column_count):
            # calculate tile position
            tile_centre_x = (column + 1) * tile_width - 20
            tile_centre_y = (row + 1) * tile_height - 20
            # check if wall
            if pac_grid[row][column] == 0:
                draw_wall_tile(tile_centre_x, tile_centre_y)
            # check if pellet
            elif pac_grid[row][column] == 1:
                draw_pellet(tile_centre_x, tile_centre_y)
            # check if super pellet
            elif pac_grid[row][column] == 3:
                if row == 1 and column == 1 and super_pellet_capture[0] == False:
                    draw_super_pellet(tile_centre_x, tile_centre_y)
                elif row == 13 and column == 1 and super_pellet_capture[2] == False:
                    draw_super_pellet(tile_centre_x, tile_centre_y)
                elif row == 13 and column == 29 and super_pellet_capture[3] == False:
                    draw_super_pellet(tile_centre_x, tile_centre_y)
                elif row == 1 and column == 29 and super_pellet_capture[1] == False:
                    draw_super_pellet(tile_centre_x, tile_centre_y)


def write_score(score):
    """ Output (write) the current score to the screen

    :param score: current score as in integer value; multiple of 10
    :return: none
    """
    arcade.draw_text(str(score), 40, 640, arcade.color.WHITE, 40)


def change_skin():
    """ Change pacman's skin status from 1 to 0 (and vice versa)

    :return: none
    """
    # change pacman from open to close mouth
    global pac_skin
    if pac_skin == 1:
        pac_skin = 0
    else:
        pac_skin = 1


def draw_pac(x, y):
    """ Depending on the current pacman skin (closed or open), change/draw pacman

    :param x: x position of pacman
    :param y: y position of pacman
    :return: none
    """
    global pac_skin
    # open mouth
    if pac_skin == 0:
        draw_pacman_open(x, y)
    # close mouth
    else:
        draw_pacman_closed(x, y)


def wall_collision(x, y):
    """ Check which walls character is currently in contact with

    :param x: x position of character
    :param y: y position of character
    :return: list of walls character is in contact with (or null if character is mid tile)
    """
    global tile_height, tile_width, pac_grid, row_count, column_count, WIDTH, HEIGHT
    # check if pacman/ghost is in the middle of a tile
    if x <= WIDTH//2:
        check_x = (x + (tile_width//2)) % tile_width
    else:
        check_x = (x - (tile_width//2)) % tile_width

    if y <= HEIGHT//2:
        check_y = (y + (tile_width // 2)) % tile_width
    else:
        check_y = (y - (tile_width // 2)) % tile_width

    # in the middle of a tile
    if check_x == 0 and check_y == 0:
        # calculate pacman tile
        pac_column = int(((x + 20) // 40) - 1)
        pac_row = int(((y + 20) // 40) - 1)

        # calculte rows and columns adjectent to pacman
        row_above = pac_row + 1
        row_below = pac_row - 1
        column_left = pac_column - 1
        column_right = pac_column + 1

        wall_touch = []

        # check if adjacent tiles are walls or not
        if pac_grid[row_above][pac_column] == 0:
            wall_touch.append("up")
        if pac_grid[row_below][pac_column] == 0:
            wall_touch.append("down")
        if pac_grid[pac_row][column_left] == 0:
            wall_touch.append("left")
        if pac_grid[pac_row][column_right] == 0:
            wall_touch.append("right")

        return wall_touch

    # not in mid tile
    else:
        return "null"


def ghost_repel(g_num, g_x, g_y, walls):
    """ Make the ghosts repel when pacman has the super pellet

    :param g_num: ghost number (related to ghost_speeds, which starts at 0)
    :param g_x: x position of ghost
    :param g_y: y position of ghost
    :param walls: list of walls ghost is in contact with
    :return: g_x, new x position of ghost with speed applied; g_y, new y position of ghost with speed applied
    """
    global ghost_speeds, pac_x, pac_y

    # create an empty list of speeds
    ghost_poss_speeds = [5, -5, -5, 5]

    # check if ghost is midtile
    if walls != "null":
        # set possible speeds in wall touch direction to zero
        for wall in walls:
            if wall == "up":
                ghost_poss_speeds[0] = 0
                ghost_speeds[g_num][1] = 0
            elif wall == "down":
                ghost_poss_speeds[1] = 0
                ghost_speeds[g_num][1] = 0
            if wall == "left":
                ghost_poss_speeds[2] = 0
                ghost_speeds[g_num][0] = 0
            elif wall == "right":
                ghost_poss_speeds[3] = 0
                ghost_speeds[g_num][0] = 0

        # calculate the x and y differences between pac and ghost
        x_distance = g_x - pac_x
        y_distance = g_y - pac_y

        # closer in the y than in the x; move in the y to move further
        if abs(x_distance) >= abs(y_distance):
            if y_distance >= 0 and ghost_poss_speeds[0] != 0:
                # ghost ontop of pac; try to move up
                ghost_speeds[g_num][1] = ghost_poss_speeds[0]
                ghost_speeds[g_num][0] = 0
            elif y_distance < 0 and ghost_poss_speeds[1] != 0:
                # ghost under pac; try to move down
                ghost_speeds[g_num][1] = ghost_poss_speeds[1]
                ghost_speeds[g_num][0] = 0
            else:
                if x_distance >= 0 and ghost_poss_speeds[3] != 0:
                    # cant move up or down, move right if further to the right
                    ghost_speeds[g_num][0] = ghost_poss_speeds[3]
                    ghost_speeds[g_num][1] = 0
                else:
                    # ghost is left, continue to move left
                    ghost_speeds[g_num][0] = ghost_poss_speeds[2]
                    ghost_speeds[g_num][1] = 0
        # ghost closer in the x direction; move in the x
        else:
            if x_distance >= 0 and ghost_poss_speeds[3] != 0:
                # ghost to the right of pacman, conitnue moving right
                ghost_speeds[g_num][0] = ghost_poss_speeds[3]
                ghost_speeds[g_num][1] = 0
            elif x_distance < 0 and ghost_poss_speeds[2] != 0:
                # ghost to the left of pacman, continue to go left
                ghost_speeds[g_num][0] = ghost_poss_speeds[2]
                ghost_speeds[g_num][1] = 0
            else:
                # ghost cannot move left or right; move up or down
                if y_distance >= 0 and ghost_poss_speeds[0] != 0:
                    # move up
                    ghost_speeds[g_num][1] = ghost_poss_speeds[0]
                    ghost_speeds[g_num][0] = 0
                else:
                    # move down in everything fails
                    ghost_speeds[g_num][1] = ghost_poss_speeds[1]
                    ghost_speeds[g_num][0] = 0

    # move the ghost
    g_x += ghost_speeds[g_num][0]
    g_y += ghost_speeds[g_num][1]

    # return the position values to move the ghost
    return g_x, g_y


def ghost_chase_rand2(walls):
    """ Move ghost 2 randomly prohibiting movement through walls

    :param ghostx: the x positon of a ghost
    :param ghosty: the y position of a ghost
    :param wall: the walls the ghost is currently in contct with
    :return: none
    """
    global ghost_speeds, ghost_x2, ghost_y2

    # create an empty list of ghost 2 possible speeds
    ghost2_poss_speeds = [20, -20, -20, 20]

    # check if ghost is midtile
    if walls != "null":
        # set possible speeds in wall touch direction to zero
        for wall in walls:
            if wall == "up":
                ghost2_poss_speeds[0] = 0
                ghost_speeds[1][1] = 0
            elif wall == "down":
                ghost2_poss_speeds[1] = 0
                ghost_speeds[1][1] = 0
            if wall == "left":
                ghost2_poss_speeds[2] = 0
                ghost_speeds[1][0] = 0
            elif wall == "right":
                ghost2_poss_speeds[3] = 0
                ghost_speeds[1][0] = 0

        # check if ghost in currently in motion
        if ghost_speeds[1][0] == 0 and ghost_speeds[1][1] == 0:
            rand_move = random.randint(0, 3)
            while ghost2_poss_speeds[rand_move] == 0:
                rand_move = random.randint(0, 3)
            if rand_move == 0:
                ghost_speeds[1][1] = ghost2_poss_speeds[0]
            elif rand_move == 1:
                ghost_speeds[1][1] = ghost2_poss_speeds[1]
            elif rand_move == 2:
                ghost_speeds[1][0] = ghost2_poss_speeds[2]
            elif rand_move == 3:
                ghost_speeds[1][0] = ghost2_poss_speeds[3]
        else:
            if ghost_speeds[1][0] > 0 and ghost2_poss_speeds[3] != 0:
                ghost_speeds[1][0] = ghost2_poss_speeds[3]
            elif ghost_speeds[1][0] < 0 and ghost2_poss_speeds[2] != 0:
                ghost_speeds[1][0] = ghost2_poss_speeds[2]
            elif ghost_speeds[1][1] > 0 and ghost2_poss_speeds[0] != 0:
                ghost_speeds[1][1] = ghost2_poss_speeds[0]
            elif ghost_speeds[1][1] < 0 and ghost2_poss_speeds[1] != 0:
                ghost_speeds[1][1] = ghost2_poss_speeds[1]

    # move the ghost
    # print(ghost2_poss_speeds)
    ghost_x2 += ghost_speeds[1][0]
    ghost_y2 += ghost_speeds[1][1]


def ghost_chase_rand3(walls):
    """ Move ghost 3 with slight attraction to pacman without going through walls

    :param walls: List of walls ghost 3 is currently in contact with or null
    :return: none
    """
    global ghost_speeds, ghost_x3, ghost_y3, pac_x, pac_y

    # create an empty list of ghost 2 possible speeds
    ghost3_poss_speeds = [10, -10, -10, 10]

    # check if ghost is midtile
    if walls != "null":
        # set possible speeds in wall touch direction to zero
        for wall in walls:
            if wall == "up":
                ghost3_poss_speeds[0] = 0
                ghost_speeds[2][1] = 0
            elif wall == "down":
                ghost3_poss_speeds[1] = 0
                ghost_speeds[2][1] = 0

            if wall == "left":
                ghost3_poss_speeds[2] = 0
                ghost_speeds[2][0] = 0
            elif wall == "right":
                ghost3_poss_speeds[3] = 0
                ghost_speeds[2][0] = 0
        # calculate the x and y differences between pac and ghost
        x_distance = ghost_x3 - pac_x
        y_distance = ghost_y3 - pac_y

        # print(x_distance, y_distance)
        # check if ghost in currently in motion or not
        if ghost_speeds[2][0] == 0 and ghost_speeds[2][1] == 0:
            # check if pacman is closer in x direction and try to send ghost that way
            if abs(x_distance) >= abs(y_distance):
                # ghost is on the right of pacman; go left
                if x_distance > 0 and ghost3_poss_speeds[2] != 0:
                    ghost_speeds[2][0] = ghost3_poss_speeds[2]
                    ghost_speeds[2][1] = 0
                # ghost is on the left of pacman; go right
                elif x_distance <= 0 and ghost3_poss_speeds[3] != 0:
                    ghost_speeds[2][0] = ghost3_poss_speeds[3]
                    ghost_speeds[2][1] = 0
                # ghost is cutoff left and right, go up or down(random)
                else:
                    rand_y_move = random.randint(0, 1)
                    while ghost3_poss_speeds[rand_y_move] == 0:
                        rand_y_move = random.randint(0, 1)
                    # move ghost up
                    if rand_y_move == 0:
                        ghost_speeds[2][1] = ghost3_poss_speeds[0]
                    # move ghost down
                    else:
                        ghost_speeds[2][1] = ghost3_poss_speeds[1]

            # ghost is closer in the y direction
            else:
                # ghost is on the ontop of pacman; go down
                if y_distance > 0 and ghost3_poss_speeds[1] != 0:
                    ghost_speeds[2][1] = ghost3_poss_speeds[1]
                    ghost_speeds[2][0] = 0
                # ghost is on the bottom of pacman; go up
                elif y_distance <= 0 and ghost3_poss_speeds[0] != 0:
                    ghost_speeds[2][1] = ghost3_poss_speeds[0]
                    ghost_speeds[2][0] = 0
                # ghost is cutoff top and bottom, go left or right(random)
                else:
                    rand_x_move = random.randint(2, 3)
                    while ghost3_poss_speeds[rand_x_move] == 0:
                        rand_x_move = random.randint(2, 3)
                    # move ghost up
                    if rand_x_move == 2:
                        ghost_speeds[2][0] = ghost3_poss_speeds[2]
                    # move ghost down
                    else:
                        ghost_speeds[2][0] = ghost3_poss_speeds[3]
        # ghost is currently in motion
        else:
            if abs(x_distance) >= abs(y_distance):
                # try to move left or right constantly
                if x_distance > 0 and ghost3_poss_speeds[2] != 0:
                    ghost_speeds[2][0] = ghost3_poss_speeds[2]
                    ghost_speeds[2][1] = 0

                elif x_distance <= 0 and ghost3_poss_speeds[3] != 0:
                    ghost_speeds[2][0] = ghost3_poss_speeds[3]
                    ghost_speeds[2][1] = 0

                else:
                    rand_y_move = random.randint(0, 1)
                    while ghost3_poss_speeds[rand_y_move] == 0:
                        rand_y_move = random.randint(0, 1)
                    # move ghost up
                    if rand_y_move == 0:
                        ghost_speeds[2][1] = ghost3_poss_speeds[0]
                    # move ghost down
                    else:
                        ghost_speeds[2][1] = ghost3_poss_speeds[1]

            else:
                # try to move up or down constantly
                if ghost3_poss_speeds[0] != 0 and y_distance <= 0:
                    ghost_speeds[2][1] = ghost3_poss_speeds[0]
                    ghost_speeds[2][0] = 0
                elif ghost3_poss_speeds[1] != 0 and y_distance > 0:
                    ghost_speeds[2][1] = ghost3_poss_speeds[1]
                    ghost_speeds[2][0] = 0
                    # ghost is cutoff top and bottom, go left or right(random)
                else:
                    rand_x_move = random.randint(2, 3)
                    while ghost3_poss_speeds[rand_x_move] == 0:
                        rand_x_move = random.randint(2, 3)
                    # move ghost up
                    if rand_x_move == 2:
                        ghost_speeds[2][0] = ghost3_poss_speeds[2]
                    # move ghost down
                    else:
                        ghost_speeds[2][0] = ghost3_poss_speeds[3]

    # move the ghost
    # print(ghost_speeds[2])
    ghost_x3 += ghost_speeds[2][0]
    ghost_y3 += ghost_speeds[2][1]


def ghost_chase1(walls):
    """ Move ghost 3 with slight attraction to pacman without going through walls

     :param walls: List of walls ghost 3 is currently in contact with or null
     :return: none
     """
    global ghost_speeds, ghost_x1, ghost_y1
    # create an empty list of ghost 2 possible speeds
    ghost1_poss_speeds = [10, -10, -10, 10]

    # check if ghost is midtile
    if walls != "null":
        # set possible speeds in wall touch direction to zero
        for wall in walls:
            if wall == "up":
                ghost1_poss_speeds[0] = 0
                ghost_speeds[0][1] = 0
            elif wall == "down":
                ghost1_poss_speeds[1] = 0
                ghost_speeds[0][1] = 0

            if wall == "left":
                ghost1_poss_speeds[2] = 0
                ghost_speeds[0][0] = 0
            elif wall == "right":
                ghost1_poss_speeds[3] = 0
                ghost_speeds[0][0] = 0
        # calculate the x and y differences between pac and ghost
        x_distance = ghost_x1 - pac_x
        y_distance = ghost_y1 - pac_y

        # print(x_distance, y_distance)
        # check if ghost in currently in motion or not
        if ghost_speeds[0][0] == 0 and ghost_speeds[0][1] == 0:
            # check if pacman is closer in x direction and try to send ghost that way
            if abs(x_distance) >= abs(y_distance):
                # ghost is on the right of pacman; go left
                if x_distance > 0 and ghost1_poss_speeds[2] != 0:
                    ghost_speeds[0][0] = ghost1_poss_speeds[2]
                    ghost_speeds[0][1] = 0
                # ghost is on the left of pacman; go right
                elif x_distance <= 0 and ghost1_poss_speeds[3] != 0:
                    ghost_speeds[0][0] = ghost1_poss_speeds[3]
                    ghost_speeds[0][1] = 0
                # ghost is cutoff left and right, go up or down(random)
                else:
                    rand_y_move = random.randint(0, 1)
                    while ghost1_poss_speeds[rand_y_move] == 0:
                        rand_y_move = random.randint(0, 1)
                    # move ghost up
                    if rand_y_move == 0:
                        ghost_speeds[0][1] = ghost1_poss_speeds[0]
                    # move ghost down
                    else:
                        ghost_speeds[0][1] = ghost1_poss_speeds[1]

            # ghost is closer in the y direction
            else:
                # ghost is on the ontop of pacman; go down
                if y_distance > 0 and ghost1_poss_speeds[1] != 0:
                    ghost_speeds[0][1] = ghost1_poss_speeds[1]
                    ghost_speeds[0][0] = 0
                # ghost is on the bottom of pacman; go up
                elif y_distance <= 0 and ghost1_poss_speeds[0] != 0:
                    ghost_speeds[0][1] = ghost1_poss_speeds[0]
                    ghost_speeds[0][0] = 0
                # ghost is cutoff top and bottom, go left or right(random)
                else:
                    rand_x_move = random.randint(2, 3)
                    while ghost1_poss_speeds[rand_x_move] == 0:
                        rand_x_move = random.randint(2, 3)
                    # move ghost up
                    if rand_x_move == 2:
                        ghost_speeds[0][0] = ghost1_poss_speeds[2]
                    # move ghost down
                    else:
                        ghost_speeds[0][0] = ghost1_poss_speeds[3]
        # ghost is currently in motion
        else:
            if abs(x_distance) >= abs(y_distance):
                # try to move left or right constantly
                if x_distance > 0 and ghost1_poss_speeds[2] != 0:
                    ghost_speeds[0][0] = ghost1_poss_speeds[2]
                    ghost_speeds[0][1] = 0

                elif x_distance <= 0 and ghost1_poss_speeds[3] != 0:
                    ghost_speeds[0][0] = ghost1_poss_speeds[3]
                    ghost_speeds[0][1] = 0

                else:
                    rand_y_move = random.randint(0, 1)
                    while ghost1_poss_speeds[rand_y_move] == 0:
                        rand_y_move = random.randint(0, 1)
                    # move ghost up
                    if rand_y_move == 0:
                        ghost_speeds[0][1] = ghost1_poss_speeds[0]
                    # move ghost down
                    else:
                        ghost_speeds[0][1] = ghost1_poss_speeds[1]

            else:
                # try to move up or down constantly
                if ghost1_poss_speeds[0] != 0 and y_distance <= 0:
                    ghost_speeds[0][1] = ghost1_poss_speeds[0]
                    ghost_speeds[0][0] = 0
                elif ghost1_poss_speeds[1] != 0 and y_distance > 0:
                    ghost_speeds[0][1] = ghost1_poss_speeds[1]
                    ghost_speeds[0][0] = 0
                    # ghost is cutoff top and bottom, go left or right(random)
                else:
                    rand_x_move = random.randint(2, 3)
                    while ghost1_poss_speeds[rand_x_move] == 0:
                        rand_x_move = random.randint(2, 3)
                    # move ghost up
                    if rand_x_move == 2:
                        ghost_speeds[0][0] = ghost1_poss_speeds[2]
                    # move ghost down
                    else:
                        ghost_speeds[0][0] = ghost1_poss_speeds[3]

    # move the ghost
    # print(ghost_speeds[2])
    ghost_x1 += ghost_speeds[0][0]
    ghost_y1 += ghost_speeds[0][1]


def pac_move(wall_touch):
    """ move pacman making sure it can't go through walls

    :param wall_touch: list of walls pacman is currently in contct with
    :return: none
    """
    global pac_speed_x, pac_speed_y, up_pressed, down_pressed, left_pressed, right_pressed, pac_x, pac_y
    global init_arc_angle, final_arc_angle, lose, win

    # make sure that if pacman loses, he can't move (even if in mid tile)
    if lose == False and win == False:
        # check if mid-tile, check wall collision
        if wall_touch != "null":
            # pacman motion depending on key pressed
            if up_pressed:
                pac_speed_y = 10
                pac_speed_x = 0
                init_arc_angle = 135
                final_arc_angle = 405
            elif down_pressed:
                pac_speed_y = -10
                pac_speed_x = 0
                init_arc_angle = 315
                final_arc_angle = 585
            elif left_pressed:
                pac_speed_x = -10
                pac_speed_y = 0
                init_arc_angle = 225
                final_arc_angle = 495
            elif right_pressed:
                pac_speed_x = 10
                pac_speed_y = 0
                init_arc_angle = 45
                final_arc_angle = 315

            # loop through the walls that are touching, restrict motion in certain directions
            for wall in wall_touch:
                # restrict up motion
                if wall == "up" and pac_speed_y > 0:
                    pac_speed_y = 0
                    init_arc_angle = 0
                    final_arc_angle = 360
                # restrict down motion
                if wall == "down" and pac_speed_y < 0:
                    pac_speed_y = 0
                    init_arc_angle = 0
                    final_arc_angle = 360
                # restict left motion
                if wall == "left" and pac_speed_x < 0:
                    pac_speed_x = 0
                    init_arc_angle = 0
                    final_arc_angle = 360
                # restrict right motion
                if wall == "right" and pac_speed_x > 0:
                    pac_speed_x = 0
                    init_arc_angle = 0
                    final_arc_angle = 360

        # move pacman
        pac_x += pac_speed_x
        pac_y += pac_speed_y


def flash_super_pellet():
    """ Make the super pellets flash

    :return: none
    """
    global pac_grid, super_pellet_capture
    # make pellets flash if not caught
    for i in range(len(super_pellet_capture)):
        if super_pellet_capture[i] == False:
            # check each pellet
            if i == 0:
                if pac_grid[1][1] == 3:
                    pac_grid[1][1] = 2
                elif pac_grid[1][1] == 2:
                    pac_grid[1][1] = 3
            elif i == 1:
                if pac_grid[1][29] == 3:
                    pac_grid[1][29] = 2
                elif pac_grid[1][29] == 2:
                    pac_grid[1][29] = 3
            elif i == 2:
                if pac_grid[13][1] == 3:
                    pac_grid[13][1] = 2
                elif pac_grid[13][1] == 2:
                    pac_grid[13][1] = 3
            elif i == 3:
                if pac_grid[13][29] == 3:
                    pac_grid[13][29] = 2
                elif pac_grid[13][29] == 2:
                    pac_grid[13][29] = 3


def pac_object_detection(x, y):
    """ Check any objects (other than walls) which pacman is in contact with

    :param x: x position of pacman
    :param y: y position of pacman
    :return: none
    """
    global tile_width, pac_rad, pac_grid, row_count, column_count, score, lose, pac_speed_x, pac_speed_y
    global ghost_x1, ghost_y1, ghost_x2, ghost_y2, ghost_x3, ghost_y3, ghost_speeds, init_arc_angle
    global final_arc_angle, super_pellet_capture, ghost_change_skin, ghost_rand_x, ghost_rand_y, win
    # check if pacman is in the middle of a tile (for pellet detection)
    check_x = (x - (tile_width // 2)) % tile_width
    check_y = (y - (tile_width // 2)) % tile_width

    # calculate pacman row/column
    pac_column = int(((x + 20) // 40) - 1)
    pac_row = int(((y + 20) // 40) - 1)

    # in the middle of a tile
    if check_x == 0 and check_y == 0 and lose == False and win == False:
        # check if pacman is on a pellet
        if pac_grid[pac_row][pac_column] == 1:
            # change status to nothing
            pac_grid[pac_row][pac_column] = 2
            score += 10
    # check if pacman is on the super pellet (3 or 2 when flashing)
    if pac_grid[pac_row][pac_column] == 3:
        # check which super pellet is caught and turn off it's status
        if pac_row == 1 and pac_column == 1 and super_pellet_capture[0] != True:
            super_pellet_capture[0] = True
            pac_grid[1][1] = 2
        elif pac_row == 13 and pac_column == 1 and super_pellet_capture[2] != True:
            super_pellet_capture[2] = True
            pac_grid[13][1] = 2
        elif pac_row == 13 and pac_column == 29 and super_pellet_capture[3] != True:
            super_pellet_capture[3] = True
            pac_grid[13][29] = 2
        elif pac_row == 1 and pac_column == 29 and super_pellet_capture[1] != True:
            super_pellet_capture[1] = True
            pac_grid[1][29] = 2

        ghost_change_skin = True

    # check if pacman is in contact with any ghost
    distance1 = ((ghost_x1-x)**2 + (ghost_y1-y)**2) ** (1/2)
    distance2 = ((ghost_x2-x)**2 + (ghost_y2-y)**2) ** (1/2)
    distance3 = ((ghost_x3-x)**2 + (ghost_y3-y)**2) ** (1/2)

    # pacman in contact with ghost; gain points
    if ghost_change_skin == True:
        if distance1 < tile_width:
            score += 200
            # change ghost to random position near the middle
            ghost_x1 = ghost_rand_x[random.randint(0, 1)]
            ghost_y1 = ghost_rand_y[random.randint(0, 2)]
        if distance2 < tile_width:
            score += 200
            # change ghost to random position near the middle
            ghost_x2 = ghost_rand_x[random.randint(0, 1)]
            ghost_y2 = ghost_rand_y[random.randint(0, 2)]
        if distance3 < tile_width:
            score += 200
            # change ghost to random position near the middle
            ghost_x3 = ghost_rand_x[random.randint(0, 1)]
            ghost_y3 = ghost_rand_y[random.randint(0, 2)]


def pac_win_lose(x, y):
    """ Check if pacman has won or lost the game

    :param x: pacman x position
    :param y: pacman y position
    :return: none
    """
    global pac_speed_x, pac_speed_y, init_arc_angle, final_arc_angle, ghost_speeds, win, lose, tile_width
    # check if pacman is in contact with any ghost
    distance1 = ((ghost_x1 - x) ** 2 + (ghost_y1 - y) ** 2) ** (1 / 2)
    distance2 = ((ghost_x2 - x) ** 2 + (ghost_y2 - y) ** 2) ** (1 / 2)
    distance3 = ((ghost_x3 - x) ** 2 + (ghost_y3 - y) ** 2) ** (1 / 2)

    # check if pacman is in contact with a ghost
    if (distance1 < tile_width or distance2 < tile_width or distance3 < tile_width) and ghost_change_skin == False:
        lose = True

    # check if pacman has won; stop the game
    total_pellets = 0
    for r in range(row_count):
        for c in range(column_count):
            if pac_grid[r][c] == 1:
                total_pellets += 1
    # check if there are any pellets
    if total_pellets == 0:
        win = True

    # stop the game if pacman wins or loses
    if win == True or lose == True:
        # make pacman stop
        pac_speed_x = 0
        pac_speed_y = 0
        init_arc_angle = 0
        final_arc_angle = 360

        # stop the ghosts
        for speedx in range(len(ghost_speeds)):
            for speedy in range(len(ghost_speeds[speedx])):
                ghost_speeds[speedx][speedy] = 0


def draw_wall_tile(x, y):
    """ Draw a wall tile

    :param x: x position of wall tile
    :param y: y position of wall tile
    :return: none
    """
    global tile_height, tile_width, texture_tile
    # display fire image on screen
    arcade.draw_texture_rectangle(x, y, tile_width, tile_height, texture_tile, 0)


def draw_pacman_closed(x, y):
    """ Draw pacman with his mouth closed

    :param x: x position of pacman
    :param y: y position of pacmam
    :return: none
    """
    global pac_rad
    arcade.draw_circle_filled(x, y, pac_rad, arcade.color.YELLOW)


def draw_pacman_open(x, y):
    """ Draw pacman with his mouth open

    :param x: pacman x position
    :param y: pacman y position
    :return: none
    """
    global pac_rad, init_arc_angle, final_arc_angle
    arcade.draw_arc_filled(x, y, pac_rad, pac_rad, arcade.color.YELLOW, init_arc_angle, final_arc_angle)


def draw_super_pellet(x, y):
    """ Draw the super pellet on the screen

    :param x: x position of super pellet
    :param y: y position of super pellet
    :return: none
    """
    global super_pellet_dim, texture_pellet
    # draw the super pellet
    arcade.draw_texture_rectangle(x, y, super_pellet_dim, super_pellet_dim, texture_pellet, 0)


def draw_pellet(x, y):
    """ Draw the pellets in the maze

    :param x: x position of the pellet
    :param y: y position of the pellet
    :return: none
    """
    global pellet_dim, texture_pellet
    # arcade.draw_circle_filled(x, y, pellet_dim, arcade.color.ORANGE_PEEL)
    arcade.draw_texture_rectangle(x, y, pellet_dim, pellet_dim, texture_pellet, 0)


def on_key_press(key, modifiers):
    """ Check which key is pressed and turn all other off

    :param key: key on the keyboard which is pressed
    :param modifiers: no modifiers
    :return: none
    """
    global up_pressed, down_pressed, left_pressed, right_pressed, lose
    # create a key list
    key_pressed_list = [0] * 4
    # only run if pacman hasnt lost
    if lose == False:
        # check if any key is pressed, if it is set that direction to true (move in 1 direction)
        if key == arcade.key.UP:
            up_pressed = True
            key_pressed_list[0] = 1
        elif key == arcade.key.DOWN:
            down_pressed = True
            key_pressed_list[1] = 1
        elif key == arcade.key.LEFT:
            left_pressed = True
            key_pressed_list[2] = 1
        elif key == arcade.key.RIGHT:
            right_pressed = True
            key_pressed_list[3] = 1
        key_pressed_boolean = [up_pressed, down_pressed, left_pressed, right_pressed]

        # turn off all keys which are not pressed, account for no on key released
        for i in range(len(key_pressed_list)):
            if key_pressed_list[i] == 0:
                key_pressed_boolean[i] = False
        up_pressed = key_pressed_boolean[0]
        down_pressed = key_pressed_boolean[1]
        left_pressed = key_pressed_boolean[2]
        right_pressed = key_pressed_boolean[3]

#
# def on_key_release(key, modifiers):
#     pass
#
#
# def on_mouse_press(x, y, button, modifiers):
#     pass


def setup():
    """ Runs once once the program is starting up to load inital values for the program

    :return: none
    """
    global pac_grid, row_count, column_count, texture_tile, texture_pellet, texture_ghost, texture_ghost_change
    global pac_grid, row_count, column_count, tile_width, tile_height, pac_x, pac_y, score
    arcade.open_window(WIDTH, HEIGHT, "My Arcade Game")
    arcade.set_background_color(arcade.color.BLACK)
    arcade.schedule(on_update, 1/60)

    # Override arcade window methods
    window = arcade.get_window()
    window.on_draw = on_draw
    window.on_key_press = on_key_press
    # window.on_key_release = on_key_release
    # window.on_mouse_press = on_mouse_press

    # load images in setup
    texture_tile = arcade.load_texture("pacific-blue-high-sheen-merola-tile-mosaic-tile-fyfl1spa-64_1000.jpg")
    texture_pellet = arcade.load_texture("Gold_Coin_PNG_Clipart-663.png")
    texture_ghost_change = arcade.load_texture("Pac-Man-Ghost-PNG-Image.png")
    texture_ghost = arcade.load_texture("Download-Pac-Man-Ghost-PNG-Transparent-Image.png")

    # create the pacman grid
    for row in range(row_count):
        # open a list for the first row
        pac_grid.append([])
        for column in range(column_count):
            # if on the outside, make tile a wall
            if row == 0 or column == 0 or row == 14 or column == 30:
                pac_grid[row].append(0)
            # draw wall tiles from column to column
            elif (2 <= row <= 5 or row == 7 or 9 <= row <= 12) and column == 2:
                pac_grid[row].append(0)
            elif row == 7 and column == 3:
                pac_grid[row].append(0)
            elif (row == 2 or 4 <= row <= 5 or row == 7 or 9 <= row <= 10 or row == 12) and column == 4:
                pac_grid[row].append(0)
            elif (row == 2 or 9 <= row <= 10 or row == 12) and column == 5:
                pac_grid[row].append(0)
            elif (row == 2 or 4 <= row <= 5 or row == 7) and column == 6:
                pac_grid[row].append(0)
            elif (row == 2 or 4 <= row <= 5 or row == 7 or row == 9 or row == 12) and column == 7:
                pac_grid[row].append(0)
            elif (row == 7 or 11 <= row <= 12) and column == 8:
                pac_grid[row].append(0)
            elif (row == 1 or 3 <= row <= 5 or 10 <= row <= 11) and column == 9:
                pac_grid[row].append(0)
            elif (row == 7 or row == 10 or row == 13) and column == 10:
                pac_grid[row].append(0)
            elif (2 <= row <= 3 or 7 <= row <= 8 or row == 10) and column == 11:
                pac_grid[row].append(0)
            elif (row == 3 or 5 <= row <= 9 or row == 11 or row == 13) and column == 13:
                pac_grid[row].append(0)
            elif (2 <= row <= 3 or row == 5 or row == 9 or row == 11) and column == 14:
                pac_grid[row].append(0)
            elif (2 <= row <= 3 or row == 5 or row == 9 or 11 <= row <= 12) and column == 15:
                pac_grid[row].append(0)
            elif (row == 3 or row == 5 or row == 9 or 11 <= row <= 12) and column == 16:
                pac_grid[row].append(0)
            elif (row == 1 or row == 3 or 5 <= row <= 9 or row == 11) and column == 17:
                pac_grid[row].append(0)
            elif (row == 4 or 6 <= row <= 7 or 11 <= row <= 12) and column == 19:
                pac_grid[row].append(0)
            elif (row == 1 or row == 4 or row == 7) and column == 20:
                pac_grid[row].append(0)
            elif (3 <= row <= 4 or 9 <= row <= 10 or row == 13) and column == 21:
                pac_grid[row].append(0)
            elif (2 <= row <= 3 or row == 7) and column == 22:
                pac_grid[row].append(0)
            elif (row == 2 or row == 5 or row == 7 or 9 <= row <= 10 or row == 12) and column == 23:
                pac_grid[row].append(0)
            elif (row == 7 or 9 <= row <= 10 or row == 12) and column == 24:
                pac_grid[row].append(0)
            elif (row == 2 or 4 <= row <= 5 or row == 12) and column == 25:
                pac_grid[row].append(0)
            elif (row == 2 or 4 <= row <= 5 or row == 7 or 9 <= row <= 10 or row == 12) and column == 26:
                pac_grid[row].append(0)
            elif row == 7 and column == 27:
                pac_grid[row].append(0)
            elif (2 <= row <= 5 or row == 7 or 9 <= row <= 12) and column == 28:
                pac_grid[row].append(0)

            # add 4 super pellets
            elif (column == 1 or column == 29) and (row == 1 or row == 13):
                # 3 means super pellet
                pac_grid[row].append(3)

            # append nothing
            elif 6 <= row <= 8 and 14 <= column <= 16:
                pac_grid[row].append(2)
            # # if not a wall tile or nothing, pellet tile
            elif (1 <= column <= 29) and (1 <= row <= 13):
                pac_grid[row].append(1)

    arcade.run()


if __name__ == '__main__':
    setup()
