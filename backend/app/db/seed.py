from sqlmodel import Session, select
from app.db.session import engine
from app.db.models import User, Organization
from app.services.auth import hash_password


def seed():
    with Session(engine) as session:
        org = session.exec(
            select(Organization).where(Organization.name == "Demo Bank")
        ).first()

        if not org:
            org = Organization(name="Demo Bank")
            session.add(org)
            session.commit()
            session.refresh(org)

        user = session.exec(
            select(User).where(User.email == "admin@bank.com")
        ).first()

        if not user:
            user = User(
                email="admin@bank.com",
                hashed_password=hash_password("admin123"),
                organization_id=org.id,
            )
            session.add(user)
            session.commit()

        print("Seed completed successfully")


if __name__ == "__main__":
    seed()
