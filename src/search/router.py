"""Search HTTP endpoints — POST /search."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.auth.permissions import get_current_user
from src.search.models import SearchHit, SearchQuery
from src.search.service import search_tasks
from src.shared.database import get_db

router = APIRouter()


@router.post("/", response_model=list[SearchHit])
def search(
    query: SearchQuery,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> list[SearchHit]:
    """Cross-domain search entry point.

    Currently searches tasks; future iterations will also search
    comments, notifications, and BUD documents. Results are ordered
    by relevance score (title hits before description hits).
    """
    return search_tasks(db, query)
