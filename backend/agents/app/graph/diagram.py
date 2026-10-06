"""Print the resume-tailoring workflow as a diagram.

Run from `backend/agents/`:
    python -m app.graph.diagram            # Mermaid text (paste into https://mermaid.live or a Markdown ```mermaid block)
    python -m app.graph.diagram --ascii    # terminal drawing (needs `pip install grandalf`)
    python -m app.graph.diagram --png [path]  # PNG file, default workflow.png (rendered by mermaid.ink, needs internet)
"""
import sys

from langchain_core.language_models.fake_chat_models import FakeListChatModel

from app.graph.workflow import build_workflow


def _graph():
    return build_workflow({}, FakeListChatModel(responses=[""])).get_graph()


def workflow_diagram(ascii_art: bool = False) -> str:
    """The workflow graph as Mermaid text, or as a terminal drawing. No model is called."""
    graph = _graph()
    return graph.draw_ascii() if ascii_art else graph.draw_mermaid()


def save_workflow_png(path: str = "workflow.png") -> None:
    """Render the workflow to a PNG. The Mermaid text is sent to mermaid.ink, so this needs internet."""
    with open(path, "wb") as f:
        f.write(_graph().draw_mermaid_png())


def print_workflow_diagram(ascii_art: bool = False) -> None:
    print(workflow_diagram(ascii_art))


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--png" in args:
        rest = args[args.index("--png") + 1:]
        save_workflow_png(rest[0] if rest and not rest[0].startswith("--") else "workflow.png")
    else:
        print_workflow_diagram("--ascii" in args)
