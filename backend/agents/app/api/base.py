"""Base class for the API route classes: it creates the router, each subclass adds its endpoints."""
from fastapi import APIRouter


class BaseRoutes:
    """Subclass it, set `prefix` and `tag`, and add the endpoints in `register`. Mount `.router` in main.py."""

    prefix = ""
    tag = ""

    def __init__(self) -> None:
        self.router = APIRouter(prefix=self.prefix, tags=[self.tag])
        self.register()

    def register(self) -> None:
        raise NotImplementedError
