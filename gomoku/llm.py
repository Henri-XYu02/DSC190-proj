import openai
import os

import re
with open("openai_api_key.txt", "r") as f:
    os.environ["OPENAI_API_KEY"] = f.read().strip()


def board_to_text(board):
    """
    Convert the Gomoku as a list to a text format suitable for GPT-3.5.
    """
    board_text = ""
    for row in board:
        # row is a list as well
        row_text = " ".join(row)
        board_text += row_text + "\n"
    return board_text

def is_valid_move(board, row, col):

    if 0 <= row < len(board) and 0 <= col < len(board[0]) and board[row][col] == ".":
        return True, None
    else:
        if row < 0 or row >= len(board) or col < 0 or col >= len(board[0]):
            print(f"Row {row} Col {col} is out of bounds.")
            message = f"Row {row} Col {col} is out of bounds. Suggest a new move."
            message = message.format(row=row, col=col)
        elif board[row][col] != ".":
            player = board[row][col]
            print(f"Position {row}, {col} is already taken by {player}.")
            message = f"Position {row}, {col} is already taken by {player}. Suggest a new move."
            message = message.format(row=row, col=col, player=player)
        return False, message


def ask_gpt_for_move(player, board, prompt_template="Suggest the next move in format: (row, col) for {player} in Gomoku in range 0-10.\n\nCurrent board:\n{board_text}\n\nMove:"):
    """
    Prompt GPT-3.5 to suggest the next move.
    """
    got_answer = False
    board_text = board_to_text(board)
    prompt = prompt_template.format(player=player, board_text=board_text)
    client = openai.OpenAI(
        api_key = os.environ.get("OPENAI_API_KEY")
    )
    messages = [
        {"role": "user", "content": prompt}
    ]
    while not got_answer:
        chat_completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        move = chat_completion.choices[0].message.content.strip()
        print("GPT-3.5 move:", move)
        # move is in the format "row, col"
        # find the first and second number in move string to handle unexpected output
        matches = re.findall(r'\d+', move)
        if len(matches) == 0:
            print("Invalid move:", move)
            messages.append({"role": "user", "content": "Invalid format. Suggest a new move."})
            continue
        else:
            r, c =  map(int, matches[:2])

        valid, feedback = is_valid_move(board, r, c)
        if valid:
            with open("error_log.txt", "a") as f:
                f.write("Valid Move\n")
            got_answer = True
        else:
            print("Invalid move:", move)
            with open("error_log.txt", "a") as f:
                f.write(feedback + "\n")
            messages.append({"role": "user", "content": feedback})

    return r, c

