from datetime import datetime

from app import create_app
from app.config import TestingConfig
from app.extensions import db
from app.models import User


def test_admin_user_listing_displays_registration_details():
    app = create_app(TestingConfig)
    app.config["SECRET_KEY"] = "test-secret"
    with app.app_context():
        db.create_all()
        admin = User(name="Admin", email="admin@example.com", role="admin")
        admin.set_password("a-secure-password")
        user = User(
            name="Registered User",
            email="registered@example.com",
            role="learner",
            created_at=datetime(2026, 9, 17, 10, 35, 42),
        )
        user.set_password("a-secure-password")
        db.session.add_all([admin, user])
        db.session.commit()
        admin_id = admin.id

    client = app.test_client()
    with client.session_transaction() as session:
        session["_user_id"] = str(admin_id)
        session["_fresh"] = True
    response = client.get("/admin")
    assert response.status_code == 200
    assert b"Registered On" in response.data
    assert b"17 September 2026" in response.data
    assert b"04:05 PM IST" in response.data

    with app.app_context():
        db.session.remove()
        db.drop_all()