"""Print the resume-tailoring workflow as a diagram.

Run from `backend/agents/`:
    python -m app.graph.diagram            # Mermaid text (paste into https://mermaid.live or a Markdown ```mermaid block)
    python -m app.graph.diagram --ascii    # terminal drawing (needs `pip install grandalf`)
    python -m app.graph.diagram --png [path]  # PNG file, default workflow.png (rendered by mermaid.ink, needs internet)
"""
import sys

from langchain_core.language_models.fake_chat_models import FakeListChatModel

from app.graph.workflow import ResumeWorkflow


class WorkflowDiagram:
    """Draws the workflow graph. No model is called: the graph is built with a fake one."""

    def __init__(self) -> None:
        self.graph = ResumeWorkflow({}, FakeListChatModel(responses=[""])).build().get_graph()

    def text(self, ascii_art: bool = False) -> str:
        """The graph as Mermaid text, or as a terminal drawing."""
        return self.graph.draw_ascii() if ascii_art else self.graph.draw_mermaid()

    def save_png(self, path: str = "workflow.png") -> None:
        """Render the graph to a PNG. The Mermaid text is sent to mermaid.ink, so this needs internet."""
        with open(path, "wb") as f:
            f.write(self.graph.draw_mermaid_png())

    def main(self, args: list[str]) -> None:
        if "--png" in args:
            rest = args[args.index("--png") + 1:]
            self.save_png(rest[0] if rest and not rest[0].startswith("--") else "workflow.png")
        else:
            print(self.text("--ascii" in args))


if __name__ == "__main__":
    WorkflowDiagram().main(sys.argv[1:])
