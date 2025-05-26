from app import app, db
from app.models import User, Event, Category
#from app.models import User Event, Registration

def seed_db_if_empty():
    # Seed categories
    if Category.query.count() == 0:
        categories = [
            Category(name="Sports"),
            Category(name="Music"),
            Category(name="Technology"),
            Category(name="Art"),
            Category(name="Education")
        ]
        db.session.add_all(categories)
        db.session.commit()
    categories = Category.query.all()

    # Seed users
    if User.query.count() == 0:
        users = [
            User(username="admin", firstname="Admin", lastname="User", email="admin@example.com"),
            User(username="alice", firstname="Alice", lastname="Smith", email="alice@example.com"),
            User(username="bob", firstname="Bob", lastname="Jones", email="bob@example.com"),
            User(username="carol", firstname="Carol", lastname="Lee", email="carol@example.com"),
            User(username="dave", firstname="Dave", lastname="Kim", email="dave@example.com"),
        ]
        db.session.add_all(users)
        db.session.commit()

    # Seed events
    if Event.query.count() == 0:
        from datetime import date, timedelta
        cat_list = Category.query.all()
        events = []
        for i in range(20):
            cat = cat_list[i % len(cat_list)]
            events.append(Event(
                name=f"Event {i+1}",
                date=date.today() + timedelta(days=i),
                location=f"Location {i+1}",
                description=f"Description for event {i+1}",
                category_id=cat.id
            ))
        db.session.add_all(events)
        db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_db_if_empty()
    app.run(debug=True)