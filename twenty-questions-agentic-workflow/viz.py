""" Script to generate the agents workflow visualization"""

from IPython.display import Image
from langchain_core.runnables.graph import MermaidDrawMethod
from graph import create_graph

graph_workflow = create_graph()
im = Image(
        graph_workflow.get_graph().draw_mermaid_png(
            draw_method=MermaidDrawMethod.API,
        )
    )

with open("graph_workflow.png", "wb") as f:
    f.write(im.data)
