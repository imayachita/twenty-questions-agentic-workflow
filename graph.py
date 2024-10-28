""" Script to define the agents graph
"""
from langgraph.graph import StateGraph, END, START
from agents import generate_question, answer_question, make_guess, checking, check_end_condition, create_secret_object, AgentState

def create_graph():
    """ Define the nodes in the agents graph and the connectivity """
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("create_secret_object", create_secret_object)
    workflow.add_node("generate_question", generate_question)
    workflow.add_node("answer_question", answer_question)
    workflow.add_node("make_guess", make_guess)
    workflow.add_node("check_end", checking)

    # Add edges
    workflow.add_edge(START, "create_secret_object")
    workflow.add_edge("create_secret_object", "generate_question")
    workflow.add_edge("generate_question", "answer_question")
    workflow.add_edge("answer_question", "make_guess")
    workflow.add_edge("make_guess", "check_end")
    workflow.add_conditional_edges(
        "check_end",
        check_end_condition,
        {
            "continue": "generate_question",
            "end": END,
        },
    )
    workflow.set_entry_point("create_secret_object")
    return workflow.compile()
