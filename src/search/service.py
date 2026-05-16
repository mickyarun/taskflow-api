"""Cross-domain search service — substring match over tasks + comments."""

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from src.search.models import SearchHit, SearchQuery
from src.tasks.models import Task


def search_tasks(db: Session, query: SearchQuery) -> list[SearchHit]:
    """Run a substring search across task titles and descriptions.

    Returns at most ``query.limit`` rows, scored by a simple bias
    (title hit > description hit). Optional ``assignee`` and ``status``
    facets narrow the search. Comments are searched in a separate call
    so the two collections can be paginated independently.
    """
    pattern = f"%{query.q}%"
    stmt = select(Task).where(
        or_(Task.title.ilike(pattern), Task.description.ilike(pattern))
    )
    if query.assignee:
        stmt = stmt.where(Task.assignee_id == query.assignee)
    if query.status:
        stmt = stmt.where(Task.status == query.status)
    stmt = stmt.limit(query.limit)
    rows = db.execute(stmt).scalars().all()

    hits: list[SearchHit] = []
    for row in rows:
        title_match = query.q.lower() in (row.title or "").lower()
        score = 1.0 if title_match else 0.5
        snippet = (row.description or row.title or "")[:160]
        hits.append(
            SearchHit(
                kind="task",
                id=str(row.id),
                title=row.title,
                snippet=snippet,
                score=score,
            )
        )
    hits.sort(key=lambda h: h.score, reverse=True)
    return hits
