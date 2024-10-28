""" Main script to run the game on agentic workflow
"""

from agents import AgentState, MAX_TRIALS
from graph import create_graph

if __name__ == "__main__":
    initial_state = AgentState(
        question_count=0,
        current_question="",
        questions=[],
        answers=[],
        guesses=[],
        guessed_object="",
        secret_object="",
        is_game_over=False
    )

    game = create_graph()
    for output in game.stream(initial_state, {"recursion_limit": MAX_TRIALS*5}):
        if "generate_question" in output:
            print(f"Question: {output['generate_question']['current_question']}")
        elif "answer_question" in output:
            print(f"Answer: {output['answer_question']['current_answer']}")
        elif "make_guess" in output:
            print(f"Guess: {output['make_guess']['guessed_object']}")
