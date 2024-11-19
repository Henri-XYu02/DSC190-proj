import matplotlib.pyplot as plt
import numpy as np

def draw_board(board):

    # Define the size of the board
    board_size = len(board)

    # Initialize plot
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_xlim(-0, board_size - 1)
    ax.set_ylim(-0, board_size - 1)

    # Draw grid
    for i in range(board_size):
        ax.plot([i, i], [-0.5, board_size - 0.5], color='black', linewidth=0.5)
        ax.plot([-0.5, board_size - 0.5], [i, i], color='black', linewidth=0.5)

    # Place pieces on the board
    for y in range(board_size):
        for x in range(board_size):
            piece = board[y][x]
            if piece == 'b':
                ax.plot(x, board_size - 1 - y, 'o', color='black', markersize=12)  # black piece
            elif piece == 'w':
                ax.plot(x, board_size - 1 - y, 'o', color='white', markersize=12, markeredgecolor='black')  # white piece

    # Hide axis ticks
    ax.set_xticks([])
    ax.set_yticks([])

    # Show the plot
    plt.savefig("board.png")

#
# . . . . . . . . . . .
# . . . . . . . . . . .
# . . . . . . . . . . .
# . . . . w b . . . . .
# . . . . w w w . b . .
# . . . . w b w . . . .
# . . . . w b . . . . .
# . . . . w . w b b . .
# . . . . . b . . b . .
# . . . . . b . . . . .
# . . . . . . . . . . .

board = [
    [".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "."],
    [".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "."],
    [".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "."],
    [".", ".", ".", ".", "w", "b", ".", ".", ".", ".", "."],
    [".", ".", ".", ".", "w", "w", "w", ".", "b", ".", "."],
    [".", ".", ".", ".", "w", "b", "w", ".", ".", ".", "."],
    [".", ".", ".", ".", "w", "b", ".", ".", ".", ".", "."],
    [".", ".", ".", ".", "w", ".", "w", "b", "b", ".", "."],
    [".", ".", ".", ".", ".", "b", ".", ".", "b", ".", "."],
    [".", ".", ".", ".", ".", "b", ".", ".", ".", ".",  "."],
    [".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "."]
]
draw_board(board)