"""Search request / response shapes for the cross-domain search endpoint."""

from pydantic import BaseModel


class SearchQuery(BaseModel):
    """Free-text search query plus optional facets.

    The search service treats ``q`` as a substring match across task
    titles, descriptions, and comments. ``assignee`` restricts the
    result set to a specific user; ``status`` to a specific lifecycle
    state. Both facets are optional.
    """

    q: str
    assignee: str | None = None
    status: str | None = None
    limit: int = 20


class SearchHit(BaseModel):
    """One row in the search-result list.

    ``kind`` distinguishes between task / comment hits — the UI uses
    it to render different cards and route deep-links to the right
    detail page.
    """

    kind: str
    id: str
    title: str
    snippet: str
    score: float
