"""HTTP endpoints for managing notification digest preferences.

Users can opt in/out of daily or weekly digests and choose the
delivery hour. The digest dispatcher (in the worker service) reads
these rows to assemble batch emails.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.shared.database import get_db
from src.auth.service import get_current_user
from src.notifications.digest_models import DigestPreference


router = APIRouter()


class DigestPreferenceIn(BaseModel):
    cadence: str = Field(pattern="^(daily|weekly)$")
    enabled: bool = True
    delivery_hour_utc: int = Field(ge=0, le=23)


class DigestPreferenceOut(BaseModel):
    cadence: str
    enabled: bool
    delivery_hour_utc: int


@router.get("/digest", response_model=DigestPreferenceOut)
def get_digest_preference(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """Return the current user's digest preference, defaulting on miss."""
    pref = db.query(DigestPreference).filter_by(user_id=user.id).first()
    if pref is None:
        return DigestPreferenceOut(cadence="daily", enabled=True, delivery_hour_utc=9)
    return DigestPreferenceOut(
        cadence=pref.cadence,
        enabled=pref.enabled,
        delivery_hour_utc=pref.delivery_hour_utc,
    )


@router.put("/digest", response_model=DigestPreferenceOut)
def set_digest_preference(
    payload: DigestPreferenceIn,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """Upsert the current user's digest preference."""
    pref = db.query(DigestPreference).filter_by(user_id=user.id).first()
    if pref is None:
        pref = DigestPreference(user_id=user.id)
        db.add(pref)
    pref.cadence = payload.cadence
    pref.enabled = payload.enabled
    pref.delivery_hour_utc = payload.delivery_hour_utc
    db.commit()
    db.refresh(pref)
    return DigestPreferenceOut(
        cadence=pref.cadence,
        enabled=pref.enabled,
        delivery_hour_utc=pref.delivery_hour_utc,
    )


@router.delete("/digest", status_code=204)
def disable_digest(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """Unsubscribe — equivalent to setting ``enabled=False`` and clearing the row."""
    pref = db.query(DigestPreference).filter_by(user_id=user.id).first()
    if pref is None:
        raise HTTPException(status_code=404, detail="No digest preference to disable")
    db.delete(pref)
    db.commit()
