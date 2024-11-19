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

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def ask_gpt_for_move(player, board, available_moves, specify_rules=False):
    """
    Prompt GPT-3.5 to suggest the next move.
    """
    # available_moves is a list of tuples
    str_moves = ", ".join([f"({r}, {c})" for r, c in available_moves])
    if specify_rules:
        prompt_template = "Select the best next move in format: (row, col) from the list: [{str_moves}] for {player} in Gomoku.\n\nCurrent board:\n{board_text}\n\n Note: The board is 0-indexed and the player who first gets 5 in a row wins."
    else:
        prompt_template = "Select the best next move in format: (row, col) from the list: [{str_moves}] for {player} in Gomoku.\n\nCurrent board:\n{board_text}\n\n Note: The board is 0-indexed."
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
        with open("logs/response_gpt.txt", "a") as f:
            f.write(move + "\n")
        # move is in the format "row, col"
        # find the first and second number in move string to handle unexpected output
        matches = re.findall(r'\d+', move)
        if len(matches) < 2:
            print("Invalid move:", move)
            messages.append({"role": "user", "content": "Can't find row and col. Suggest a new move. Please only provide the row and column numbers. No other text is allowed."})
            continue
        else:
            r, c =  map(int, matches[:2])

        valid, feedback = is_valid_move(board, r, c, available_moves)
        if valid:
            with open("logs/error_log_gpt.txt", "a") as f:
                f.write("Valid Move\n")
            got_answer = True
        else:
            print("Invalid move:", move)
            with open("logs/error_log_gpt.txt", "a") as f:
                f.write(feedback + "\n")
            feedback += "Please only provide the row and column numbers. No other text is allowed."
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
    base64_image = encode_image("gomoku/board.png")
    messages = [
        {"role": "user", "content": [
            {"image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}, "type": "image_url"}, {"text": prompt, "type": "text"}
        ]}
    ]
    client = openai.OpenAI(
        api_key = os.getenv("DASHSCOPE_API_KEY"),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
    
    
    while not got_answer:
        # response = MultiModalConversation.call(model='qwen-vl-plus', messages=messages)
        response =client.chat.completions.create(
            model="qwen-vl-plus",
            messages=messages
        )
        move = response.choices[0].message.content.strip()
        with open("logs/response_qwen.txt", "a") as f:
            f.write(move + "\n")
        print("QwenVL move:", move)
        # move is in the format "row, col"
        # find the first and second number in move string to handle unexpected output
        matches = re.findall(r'\d+', move)
        if len(matches) < 2:
            print("Invalid move:", move)
            messages.append({"role": "user", "content": "Can't find required two numbers. Suggest a new move. Please only provide the row and column numbers. No other text is allowed."})
            continue
        else:
            r, c =  map(int, matches[:2])

        valid, feedback = is_valid_move(board, r, c, available_moves)
        if valid:
            with open("logs/qwen_error_log.txt", "a") as f:
                f.write("Valid Move\n")
            got_answer = True
        else:
            print("Invalid move:", move)
            with open("logs/qwen_error_log.txt", "a") as f:
                f.write(feedback + "\n")
            feedback += "Please only provide the row and column numbers. No other text is allowed."
            messages.append({"role": "user", "content": feedback})

    return r, c
