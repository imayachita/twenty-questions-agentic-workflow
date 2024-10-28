# LLM 20 questions game

This directory contains scripts to run 20 questions game with LLMs agentic workflow.

## Setup
If you are using MacBook, run `brew install graphviz`.
Run `poetry shell` then `poetry install` to install the required packages

## How to run
Run `python main.py`

# Explanation
The LLMs agentic workflow was built using LangGraph to allow flexibility in defining the agents and their connectivity.
Below is the diagram of the agents workflow:
![alt text](twenty_questions_agentic_workflow/graph_workflow.png)

The host agent is divided into "sub-agents" (represented as nodes in the graph):
- `create_secret_object`: come up with a secret object the opponent has to guess
- `answer_question`: answer the question asked by the opponent with "yes" if the secret object fits the question and "no" if it doesn't

The guesser agent is divided into "sub-agents":
- `generate_question`: ask question to help guess the secret object
- `make_guess`: guess the secret object

There is an extra agent to determine if we reached the end of the game (either maximum trials is achieved or the guesser guesses correctly), called `checking`.


# Observation
1. Initially the agents got stuck by guessing the same object or ask the same question all over again.
I fixed this by providing the list of previous questions and/or previous answers and did some prompt engineering
to ensure the agents didn't make the same mistakes. I also noticed that the agents could narrow down the search space better.

2. Sometimes the `generate_answer` agent didn't give correct answer, e.g. the secret object was "basketball" and it answered "Yes" on this question "Is the object you're thinking of something that is typically found indoors?". I think
it is a bit ambiguous that basketball might be commonly stored indoors but used outdoors. I would like to add confidence score to evaluate ambiguous situation if I had more time.

3. In the above example, even if the agent knew that the secret object was commonly found indoors, in the subsequent trials, it asked "Is the object you're thinking of typically used in outdoor recreational activities?". This contradicted
with the prior knowledge.

4. For some reason, there are objects that the guesser likes a lot, like "lamp", "television", "board game", even if I set LLM cache to False and temperature to be 1.

5. The guesser agents can't really learn from the previous Q&A even if they have access to it, e.g.
One of the previous Q&As
```
Question: Is the object you're thinking of something that is typically used for entertainment or recreation?
Answer: Yes.
```
After a few trials, the guesser guessed "coffee table". It was not a good guess because "coffee table" is not typically used for entertainment or recreation.

6. The agents will not accept guesses that are similar to the correct answer, e.g. "Chess set" is not the same with "chessboard".


# Potential Improvements
If I had more time, below are the things I would like to add:

1. Error handling, such as:
    -   Harmful responses
        We can have another agent to check if there is any harmful response. If yes, end the game directly
    -   The host agent can't come up with a secret object with short name
        There should be a quality checking on the secret object name, e.g. we don't want the secret object name to be "a blue-headed tiger" because it's too long and doesn't exist in reality.
        We can do handle this situation by having another agent as a quality checker and ask the host to re-generate a new secret object.


2. Evaluation
The evaluation can be divided into evaluating a single agent separately and treating the whole workflow as a black box.
Evaluation can be done using LangSmith
    -   Evaluating the whole workflow as a black box
        We can use below metrics:
            - Whether the guesser can make a correct guess
            - Number of rounds to get the correct answer
            - (When error handling is implemented) How many times the agents run into errors
            - Questions relevance with the Q&A history, e.g.:
                - How well each question narrows down the search space
                - How each question covers different aspects of the secret object
            - How creative the host can come up with a secret object
            - All of these metrics should be recorded across multiple games too. Ideally, we want improvements over time.

    -   Evaluating a single agent separately
        Record the prompt and the response for each agent and check the answers relevance and confidence.


3. Agent quality improvement
- Instead of using regex to check whether the guess is correct or not, we can use another agent to check the similarity between the guess and the correct answer.
- The agents need to learn from previous Q&As to ensure their next guess fits all the previous questions. It has done this to a certain extent, but sometimes still failed.
- The agents at the moment can't learn across multiple games to improve its performance over time. We can build a general memory or knowledge base and meta-learning agents that can learn from the previous games.
