"""
Quality Verification Module
---------------------------
Verifies medicine authenticity and quality at point of dispensing.

Current approach: rule-based heuristics on batch metadata and reported flags.
Next iteration: integrate with WHO GTIN registry or local NDA database.
"""
from sqlalchemy.orm import Session
from app.models.stock_event import StockEvent, QualityFlag
from app.models.schemas import QualityVerificationResult
from typing import Optional


SUSPECT_KEYWORDS = [
    "counterfeit", "suspect", "substandard", "damaged", "discoloured",
    "unusual smell", "wrong packaging", "no batch"
]


def run_quality_check(event: StockEvent) -> QualityVerificationResult:
    """
    Applies heuristic quality checks to a stock event.
    Returns a QualityVerificationResult with a flag and confidence score.
    """
    notes = []
    confidence = 1.0
    flag = QualityFlag.PASS

    # Check 1: Missing batch number is a red flag
    if not event.batch_number:
        flag = QualityFlag.SUSPECT
        confidence -= 0.3
        notes.append("No batch number recorded.")

    # Check 2: Scan quality notes for suspect keywords
    if event.quality_notes:
        low = event.quality_notes.lower()
        hits = [kw for kw in SUSPECT_KEYWORDS if kw in low]
        if hits:
            flag = QualityFlag.FAIL
            confidence -= 0.4
            notes.append(f"Suspect keywords in notes: {', '.join(hits)}.")

    # Check 3: Negative or zero quantity is invalid
    if event.quantity <= 0:
        flag = QualityFlag.FAIL
        confidence = 0.0
        notes.append("Invalid quantity (zero or negative).")

    # Clamp confidence
    confidence = max(0.0, round(confidence, 2))

    if flag == QualityFlag.PASS and not notes:
        notes.append("All checks passed.")

    return QualityVerificationResult(
        event_id=event.id,
        medicine_name=event.medicine_name,
        batch_number=event.batch_number,
        quality_flag=flag,
        confidence=confidence,
        notes=" ".join(notes),
    )


def verify_and_save(db: Session, event_id: int) -> Optional[QualityVerificationResult]:
    event = db.query(StockEvent).filter(StockEvent.id == event_id).first()
    if not event:
        return None
    result = run_quality_check(event)
    event.quality_flag = result.quality_flag
    db.commit()
    return result