import openai
import os
from http import HTTPStatus
import dashscope
from dashscope import MultiModalConversation
import re
import base64
dashscope.base_http_api_url = 'https://dashscope-intl.aliyuncs.com/api/v1'

with open("gomoku/openai_api_key.txt", "r") as f:
    # first line is the api key for gpt
    # second line is the api key for qwen
    OPENAI_API_KEY = f.readline().strip()
    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
    QWEN_API_KEY = f.readline().strip()
    # export export DASHSCOPE_API_KEY=QWEN_API_KEY
    os.environ["DASHSCOPE_API_KEY"] = QWEN_API_KEY
    dashscope.api_key = QWEN_API_KEY

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

def is_valid_move(board, row, col, available_moves):

    if (row, col) in available_moves:
        return True, None
    else:
        if row < 0 or row >= len(board) or col < 0 or col >= len(board[0]):
            print(f"Row {row} Col {col} is out of bounds.")
            message = f"({row}, {col}) is out of bounds. Suggest a new move."
            message = message.format(row=row, col=col)
        elif board[row][col] != ".":
            player = board[row][col]
            print(f"Position {row}, {col} is already taken by {player}.")
            message = f"({row}, {col}) is already taken by {player}. Suggest a new move."
            message = message.format(row=row, col=col, player=player)
        else:
            print(f"Position {row}, {col} is not available.")
            message = f"({row}, {col}) is not among the given list of moves. Suggest a new move."
            message = message.format(row=row, col=col)
        return False, message

def generate_data_url(image_path):
    # Read the image file in binary mode
    with open(image_path, "rb") as image_file:
        # Encode the image in base64
        base64_image = base64.b64encode(image_file.read()).decode("utf-8")
    
    # Format as data URL
    data_url = f"data:image/png;base64,{base64_image}"
    
    return data_url

def ask_gpt_for_move(player, board, available_moves, specify_rules=False):
    """
    Prompt GPT-3.5 to suggest the next move.
    """
    # available_moves is a list of tuples
    str_moves = ", ".join([f"({r}, {c})" for r, c in available_moves])
    prompt_template = "Select the best next move in format: (row, col) from the list: [{str_moves}] for {player} in Gomoku.\n\nCurrent board:\n{board_text}\n\n Note: The board is 0-indexed and the player who first gets 5 in a row wins."
    got_answer = False
    board_text = board_to_text(board)
    prompt = prompt_template.format(player=player, board_text=board_text, str_moves=str_moves)
    print("Prompt:", prompt)
    client = openai.OpenAI(
        api_key = os.getenv("OPENAI_API_KEY")
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

        valid, feedback = is_valid_move(board, r, c, available_moves)
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

def ask_qwenvl_for_move(player, board, available_moves):
    """
    Prompt QwenVL to suggest the next move.
    """
    got_answer = False
    prompt_template = "Select the best next move in format: (row, col) from the list: [{str_moves}] for {player} in Gomoku.\n\nCurrent board is given in the image\n\n Note: The board is 0-indexed and the player who first gets 5 in a row wins."
    str_moves = ", ".join([f"({r}, {c})" for r, c in available_moves])
    prompt = prompt_template.format(player=player, str_moves=str_moves)
    image_url = generate_data_url("board.png")
    messages = [
        {"role": "user", "content": [
            {"image": image_url, "type": "image"}, {"text": prompt, "type": "text"}
        ]}
    ]
    
    while not got_answer:
        response = MultiModalConversation.call(model='qwen-vl-plus', messages=messages)
        move = response.output.choices[0].message.content.strip()
        print("QwenVL move:", move)
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
            with open("qwen_error_log.txt", "a") as f:
                f.write("Valid Move\n")
            got_answer = True
        else:
            print("Invalid move:", move)
            with open("qwen_error_log.txt", "a") as f:
                f.write(feedback + "\n")
            messages.append({"role": "user", "content": feedback})

    return r, c
