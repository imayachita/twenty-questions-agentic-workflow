""" Script to define agents states and functions
"""

import re
from typing import Dict, List, Any, TypedDict, Literal, Optional
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

MAX_TRIALS = 20
MAX_WORDS = 2 # define the max words of the secret object

llm = ChatOpenAI(model="gpt-4o", cache=False, temperature=1.0)

class AgentState(TypedDict):
    question_count: int
    current_question: str
    current_answer: str
    questions: List[Optional[str]]
    answers: List[Optional[str]]
    guesses: List[Optional[str]]
    guessed_object: str
    secret_object: str
    is_game_over: bool


def generate_question(state: AgentState) -> Dict[str, Any]:
    """ Agent function to generate question """
    prompt = ChatPromptTemplate.from_template(
        "You are an expert in reading someone's mind and you are playing {max_trials} questions now. "
        "You need to guess an object that is currently in my mind. You only have maximum {max_trials} trials."
        "You have a memory on what questions you have asked before and the corresponding answers. "
        "Use that knowledge to formulate the next question so that it helps you to guess the object in my mind. "
        "If any of the previous questions have 'yes' as the answer, it means you are closer to the correct answer. "
        "If any of the previous questions have 'no' as the answer, it means you are farther to the correct answer. "
        "The next question you ask has to narrow down the search space from the previous questions that have 'yes' answer. "
        "DO NOT ask the same question you have already asked!!!"
        "These are the previous questions and answers: {qa_history}\n"
        "You have asked {question_count} questions \n"
        "Next question:"
    )
    chain = prompt | llm
    current_question = chain.invoke({
        "max_trials": MAX_TRIALS,
        "question_count": state["question_count"],
        "qa_history": "\n".join([f"Q: {q}\nA: {a}" for q, a in zip(state["questions"], state["answers"])]),
    }).content
    state["questions"].append(current_question)
    return {"current_question": current_question}


def answer_question(state: AgentState) -> Dict[str, Any]:
    """ Agent function to answer a question with Yes or No """
    prompt = ChatPromptTemplate.from_template(
        "You are the host in a game of {max_trials} questions. You are currently thinking about: {secret_object}\n"
        "Your opponent asked this question: {question}\n"
        "Answer if the object you are currently thinking about fits the question. You can only answer Yes or No."
    )
    chain = prompt | llm
    current_answer = chain.invoke({
        "max_trials": MAX_TRIALS,
        "secret_object": state["secret_object"],
        "question": state["current_question"]
    }).content
    state["answers"].append(current_answer)
    return {"current_answer": current_answer}


def make_guess(state: AgentState) -> Dict[str, Any]:
    """ Agent function to make a guess based on Q&A history """
    prompt = ChatPromptTemplate.from_template(
        "You are an expert in reading someone's mind. "
        "You have a memory on what questions you have asked before and the corresponding answers. "
        "Use that knowledge to guess what object your opponent is currently thinking about."
        "DO NOT guess the same object you have already answered!! You have answered these: {previous_guesses}"
        "Your guess has to also fit the previous questions with 'yes' answers. "
        "Your guess MUST NOT fit the previous questions with 'no' answers. "
        "Your guess can consist of maximum {max_words} words. Please be as concise as possible."
        "These are the previous questions and answers: {qa_history}\n"
        "Your guess:"
    )
    chain = prompt | llm
    guessed_object = chain.invoke({
        "qa_history": "\n".join([f"Q: {q}\nA: {a}" for q, a in zip(state["questions"], state["answers"])]),
        "previous_guesses": [re.sub(r'([^a-zA-Z ]+?)', '', text) for text in state["guesses"]],
        "max_words": MAX_WORDS
    }).content
    state["guesses"].append(guessed_object)
    return {"guessed_object": guessed_object}


def create_secret_object(state: AgentState):
    """ Agent function to create a secret object """
    prompt = ChatPromptTemplate.from_template(
        "You are the host of {max_trials} questions game. "
        "You need to think about with a secret object that your opponent will try to guess."
        "The secret object has to consist of maximum {max_words} words. "
        "Please be as concise as possible. "
        "The secret object: "
    )
    chain = prompt | llm
    guessed_object = chain.invoke({
        "max_trials": MAX_TRIALS,
        "max_words": MAX_WORDS
    }).content
    state["secret_object"] = guessed_object
    return state


def checking(state: AgentState) -> AgentState:
    """ Agent function to check if the guess is correct or max trials is achieved """
    state["question_count"] += 1
    guessed_object = ''.join(e for e in state["guessed_object"].lower() if e.isalnum())
    secret_object = ''.join(e for e in state["secret_object"].lower() if e.isalnum())
    if state["question_count"] == MAX_TRIALS or guessed_object == secret_object:
        state["is_game_over"] = True
    return state


def check_end_condition(state: AgentState) -> Literal["end", "continue"]:
    """ Function to determine if the game should end or not """
    if state["is_game_over"]:
        guessed_object = ''.join(e for e in state["guessed_object"].lower() if e.isalnum())
        secret_object = ''.join(e for e in state["secret_object"].lower() if e.isalnum())
        if guessed_object == secret_object:
            print(f"Correct! Current guess: {state['guessed_object']}, correct answer: {state['secret_object']}")
        else:
            print(f"Game over! You run out of trials. The correct answer: {state['secret_object']}")

        return "end"
    else:
        print(f"Next round! Trials left: {MAX_TRIALS - state['question_count']} \n\n")
        return "continue"
