import openai
import os

api_key = "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"

import openai

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

def ask_gpt_for_move(player, board_text, prompt_template="Suggest the best next move (row, col) for {player} in Gomoku.\n\nCurrent board:\n{board_text}\n\nMove:"):
    """
    Prompt GPT-3.5 to suggest the next move.
    """
    prompt = prompt_template.format(player=player, board_text=board_text)
    client = openai.OpenAI(
        api_key = api_key
    )
    chat_completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    move = chat_completion.choices[0].message.content.strip()
    # move is in the format "row, col"
    return move

