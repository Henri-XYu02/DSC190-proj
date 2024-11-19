# NOTE: do not modify this file
from game import Game, WHITE, BLACK
from ai import AI
from llm import ask_gpt_for_move, board_to_text, ask_qwenvl_for_move
from draw_board import draw_board

TOL = 0.01

def load_UCB_arr(text):
    action_win_UCB_sol = {}
    for line in text.split("\n"):
        tokens = line.strip().split(" ")
        action_win_UCB_sol[(int(tokens[0]), int(tokens[1]))] = float(tokens[2])
    return action_win_UCB_sol


def deterministic_test():
    sols = []
    states = []

    with open("test_sols") as file:
        text = file.read()

        sols_text = text.split("\n\n")[:-1]
        
        for sol_text in sols_text:
            sols.append(load_UCB_arr(sol_text))
            
    with open("test_states") as file:
        states = file.readlines()

    states = [state[:-1] for state in states]

    assert(len(states) == len(sols))
    num_tests = len(states)
    test_num = 1
    for state, sol in zip(states, sols):
        print("test {}/{}".format(test_num, num_tests))
        game = Game()
        game.load_state_text(state)

        ai_player = AI(game.state())
        _, UCBs = ai_player.mcts_search()

        incorrect_cnt = 0
        for key in sol:
            if (UCBs[key] - sol[key] <= TOL and 
                UCBs[key] - sol[key] >= -TOL):
                pass
            else:
                print("Incorrect UCB for action:", key)
                print("yours/correct: {}/{}".format(UCBs[key], sol[key]))
                incorrect_cnt += 1

        print()
        if incorrect_cnt == 0:
            print("PASSED")
        else:
            print("FAILED")
        print()

        test_num += 1



def win_test():
    simulator = Game()
    wins = 0
    for play_i in range(NUM_PLAYS):
        print("play {}/{}".format(play_i + 1, NUM_PLAYS))
        simulator.reset(BLACK)
        ai_play = False
        while not simulator.game_over:
            if ai_play:
                ai_player = AI(simulator.state())
                (r,c), _ = ai_player.mcts_search()
            else:
                (r,c) = simulator.rand_move()

            simulator.place(r, c)
            ai_play = not ai_play

        if simulator.winner == WHITE:
            print("AI won.")
            wins += 1
        else:
            print("Random player won.")
        print()

    if wins < MIN_WINS:
        print("FAILED")
    else:
        print("PASSED")


MIN_WINS = 9
NUM_PLAYS = 10

def llm_test(specify_rules=True):
    simulator = Game()
    wins = 0
    move_count = 0
    if specify_rules:
        string = "_with_rules"
    else:
        string = "_without_rules"
    for play_i in range(NUM_PLAYS):
        print("play {}/{}".format(play_i + 1, NUM_PLAYS))
        with open(f"logs/match_gpt{string}.txt", "a") as f:
            f.write(f"play {play_i + 1}/{NUM_PLAYS}\n")

        # black goes first
        simulator.reset(BLACK)
        ai_play = False
        
        while not simulator.game_over:
            print(f"board:\n{simulator.state()[1]}")
            if ai_play:
                player, board = simulator.state()
                r, c = ask_gpt_for_move(player, board, simulator.get_actions(), specify_rules=specify_rules)
                print("GPT-3.5 move:", r, c)
            else:
                (r,c) = simulator.rand_move()
                print("Random player move:", r, c)

            simulator.place(r, c)
            ai_play = not ai_play
            move_count += 1
            with open(f"logs/match_gpt{string}.txt", "a") as f:
                f.write("Player: " + str(simulator.state()[0]) + "\n")
                f.write(board_to_text(simulator.state()[1]) + "\n")

        if simulator.winner == WHITE:
            print("AI won.")
            with open(f"logs/result_gpt{string}.txt", "a") as f:
                f.write("AI won\n")
                f.write(board_to_text(simulator.state()[1]) + "\n")
            wins += 1
        else:
            print("Random player won.")
            with open(f"logs/result_gpt{string}.txt", "a") as f:
                f.write("Random player won\n")
                f.write(board_to_text(simulator.state()[1]) + "\n")
            
    print(f"GPT-3.5 win rate:{wins/NUM_PLAYS}")
    with open(f"logs/result_gpt{string}.txt", "a") as f:
        f.write(f"GPT-3.5 win rate:{wins/NUM_PLAYS}\n")
        f.write(f"Average moves(GL): {move_count/NUM_PLAYS}\n")

    print(f"Average moves: {move_count/NUM_PLAYS}")
        
def vl_test():
    simulator = Game()
    wins = 0
    moves = 0
    for play_i in range(NUM_PLAYS):
        with open("logs/match_vl.txt", "a") as f:
            f.write(f"play {play_i + 1}/{NUM_PLAYS}\n")
        print("play {}/{}".format(play_i + 1, NUM_PLAYS))
        # black goes first
        simulator.reset(BLACK)
        ai_play = False
        
        while not simulator.game_over:
            print(f"board:\n{simulator.state()[1]}")

            if ai_play:
                player, board = simulator.state()
                draw_board(board)
                r, c = ask_qwenvl_for_move(player, board, simulator.get_actions())
                print("QwenVL move:", r, c)
            else:
                (r,c) = simulator.rand_move()
                print("Random player move:", r, c)
            simulator.place(r, c)
            ai_play = not ai_play
            moves += 1
            
            with open("logs/match_vl.txt", "a") as f:
                f.write("Player: " + str(simulator.state()[0]) + "\n")
                f.write(board_to_text(simulator.state()[1]) + "\n")

        if simulator.winner == WHITE:
            print("AI won.")
            with open("logs/result_vl.txt", "a") as f:
                f.write("VL won\n")
                f.write(board_to_text(simulator.state()[1]) + "\n")
            wins += 1
        else:
            print("Random player won.")
            with open("logs/result_vl.txt", "a") as f:
                f.write("Random player won\n")
                f.write(board_to_text(simulator.state()[1]) + "\n")
            
    print(f"QwenVL win rate:{wins/NUM_PLAYS}")
    with open("logs/result_vl.txt", "a") as f:
        f.write(f"QwenVL win rate:{wins/NUM_PLAYS}\n")
        f.write(f"Average moves(GE): {moves/NUM_PLAYS}\n")


def adversarial_test():
    # let MCTS play against gpt-3.5
    simulator = Game()
    wins = 0
    for play_i in range(NUM_PLAYS):
        print("play {}/{}".format(play_i + 1, NUM_PLAYS))
        simulator.reset(BLACK)
        
        if play_i % 2 == 0:
            # GPT-3.5 plays first -> BLACK
            mcts_play = False
        else:
            # MCTS plays first -> BLACK
            mcts_play = True
        
        while not simulator.game_over:
            print(f"board:\n{simulator.state()[1]}")
            if mcts_play:
                ai_player = AI(simulator.state())
                (r,c), _ = ai_player.mcts_search()
            else:
                player, board = simulator.state()
                r, c = ask_gpt_for_move(player, board)
                print("GPT-3.5 move:", r, c)
                if board[r][c] != '.':
                    raise Exception("GPT-3.5 made an invalid move.")

            simulator.place(r, c)
            mcts_play = not mcts_play
        
        if simulator.winner == BLACK and play_i % 2 == 0:
            print("GPT-3.5 won.")
            wins += 1
        elif simulator.winner == WHITE and play_i % 2 == 1:
            print("GPT-3.5 won.")
            wins += 1
        else:
            print("MCTS won.")
        
    print(f"GPT-3.5 win rate:{wins/NUM_PLAYS}")