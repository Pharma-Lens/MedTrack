"""
Seed script — loads realistic pilot data into MedTrack.
Simulates two health facilities in Uganda with common essential medicines.

Run: python scripts/seed.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal, Base, engine
from app.models.stock_event import StockEvent, EventType, QualityFlag
from datetime import datetime, timedelta
import random

Base.metadata.create_all(bind=engine)
db = SessionLocal()

random.seed(42)

FACILITIES = ["HC-MBARARA-01", "HC-KAMPALA-02"]
MEDICINES = [
    ("MED-AMOX", "Amoxicillin 500mg"),
    ("MED-COART", "Coartemether 20/120mg (ACT)"),
    ("MED-PARA", "Paracetamol 500mg"),
    ("MED-ORS", "ORS Sachets"),
    ("MED-DEPO", "Depo-Provera 150mg/ml"),
]

now = datetime.utcnow()

events = []

for fac in FACILITIES:
    for med_id, med_name in MEDICINES:
        # Receive stock
        received = random.randint(300, 800)
        events.append(StockEvent(
            facility_id=fac, medicine_id=med_id, medicine_name=med_name,
            batch_number=f"BATCH-{random.randint(1000,9999)}",
            event_type=EventType.RECEIVED, quantity=received,
            stock_on_hand_after=received, reorder_level=100,
            quality_flag=QualityFlag.PASS,
            created_at=now - timedelta(days=35),
        ))
        # Dispense over 30 days
        total_dispensed = 0
        for day in range(30):
            qty = random.randint(5, 25)
            total_dispensed += qty
            events.append(StockEvent(
                facility_id=fac, medicine_id=med_id, medicine_name=med_name,
                event_type=EventType.DISPENSED, quantity=qty,
                stock_on_hand_after=max(0, received - total_dispensed),
                expected_quantity=qty,
                created_at=now - timedelta(days=30 - day),
            ))

# Inject a quality failure
events.append(StockEvent(
    facility_id="HC-MBARARA-01",
    medicine_id="MED-COART",
    medicine_name="Coartemether 20/120mg (ACT)",
    batch_number=None,
    event_type=EventType.RECEIVED, quantity=200,
    quality_flag=QualityFlag.SUSPECT,
    quality_notes="Tablets discoloured and unusual smell. No batch number on packaging.",
    created_at=now - timedelta(days=5),
))

# Inject a diversion scenario: received 500 but only 300 accounted for
events.append(StockEvent(
    facility_id="HC-KAMPALA-02",
    medicine_id="MED-DEPO",
    medicine_name="Depo-Provera 150mg/ml",
    batch_number="BATCH-DIVTEST",
    event_type=EventType.RECEIVED, quantity=500,
    stock_on_hand_after=500,
    quality_flag=QualityFlag.PASS,
    created_at=now - timedelta(days=28),
))
for i in range(10):
    events.append(StockEvent(
        facility_id="HC-KAMPALA-02",
        medicine_id="MED-DEPO",
        medicine_name="Depo-Provera 150mg/ml",
        event_type=EventType.DISPENSED, quantity=10,
        created_at=now - timedelta(days=27 - i * 2),
    ))
# Only 100 of 500 accounted for → 40% diversion flag

db.bulk_save_objects(events)
db.commit()
db.close()

print(f"✓ Seeded {len(events)} events across {len(FACILITIES)} facilities, {len(MEDICINES)} medicines.")
print("  Includes 1 quality suspect event and 1 diversion scenario.")
