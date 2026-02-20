import sys
import os
sys.path.append(os.getcwd())

from app.database import engine
from app.models import Base
from sqlalchemy import text

def recreate_risk_table():
    with engine.connect() as conn:
        print("Dropping risk_scores table...")
        conn.execute(text("DROP TABLE IF EXISTS risk_scores CASCADE"))
        conn.commit()
        print("Dropped risk_scores table.")

    print("Recreating tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables recreated.")

if __name__ == "__main__":
    recreate_risk_table()
