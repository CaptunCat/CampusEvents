from app import app, db
from app.models import User, Event, Category

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
        # Set passwords
        for user in users:
            if user.username == "admin":
                user.set_password("admin")
            else:
                user.set_password("pass")
        db.session.add_all(users)
        db.session.commit()

    # Seed events
    if Event.query.count() == 0:
        from datetime import date, timedelta
        cat_list = Category.query.all()
        event_names = [
            "Campus Soccer Tournament",
            "Jazz Night Extravaganza",
            "Python Coding Bootcamp",
            "Modern Art Workshop",
            "STEM Career Fair",
            "Basketball Skills Clinic",
            "Classical Music Recital",
            "Robotics Expo",
            "Photography Masterclass",
            "Resume Building Seminar",
            "Volleyball Friendly",
            "Battle of the Bands",
            "AI in Everyday Life",
            "Watercolor Painting Day",
            "Internship Networking",
            "Track and Field Meet",
            "Open Mic Poetry",
            "Web Development Crash Course",
            "Sculpture in the Park",
            "Graduate School Info Session"
        ]
        event_descriptions = [
            "Join us for an exciting soccer tournament! Teams from across campus will compete for the championship. Bring your friends and cheer for your favorite team. Refreshments will be provided.",
            "Enjoy a night of smooth jazz performed by talented student musicians. The auditorium will be filled with soulful tunes and lively rhythms. Don't miss this musical celebration. Free entry for all students.",
            "Dive into Python programming with our hands-on bootcamp. No prior experience needed—just bring your laptop and enthusiasm. Learn the basics and build your first project. Certificates for all participants.",
            "Unleash your creativity at the Modern Art Workshop. Explore new techniques and express yourself through painting and sculpture. All materials are provided. Open to beginners and experienced artists.",
            "Meet top employers and explore STEM career opportunities at our annual fair. Network with professionals, attend workshops, and discover internships. Dress professionally and bring your resume.",
            "Sharpen your basketball skills with expert coaches. This clinic covers dribbling, shooting, and teamwork. All skill levels are welcome. Prizes for the most improved players.",
            "Experience the beauty of classical music at our recital. Talented students and faculty will perform pieces from renowned composers. A night of elegance and inspiration awaits.",
            "Discover the latest in robotics technology at our expo. See live demonstrations, interact with robots, and learn about the future of automation. Great for tech enthusiasts of all ages.",
            "Capture stunning images with tips from a professional photographer. This masterclass covers composition, lighting, and editing. Bring your camera or smartphone.",
            "Boost your job prospects with our resume building seminar. Learn how to craft a standout resume and cover letter. Get personalized feedback from career advisors.",
            "Join us for a friendly volleyball match on the campus courts. Teams will be formed on the spot, so everyone gets to play. Enjoy the sun, sand, and sportsmanship.",
            "Battle of the Bands returns! Watch student bands compete for the title and a cash prize. Vote for your favorite group and enjoy a night of great music and energy.",
            "Explore how artificial intelligence is changing our world. This talk covers AI basics, real-world applications, and ethical considerations. Q&A session to follow.",
            "Relax and paint in the park with fellow students. Watercolor supplies and snacks provided. No experience necessary—just a love for art and nature.",
            "Connect with employers offering internships in various fields. Practice your networking skills and learn about application processes. Bring copies of your resume.",
            "Show off your speed and strength at the track and field meet. Events include sprints, relays, and long jump. Medals for top performers.",
            "Share your poetry or enjoy listening at our open mic night. All styles and languages welcome. Coffee and pastries served.",
            "Learn the essentials of web development in this crash course. Build your own website from scratch and understand the basics of HTML, CSS, and JavaScript.",
            "Try your hand at sculpture in the park. Clay and tools provided. Take home your masterpiece at the end of the day.",
            "Thinking about grad school? Attend this info session to learn about programs, applications, and funding opportunities. Meet current grad students and faculty."
        ]
        event_locations = [
            "Main Soccer Field",
            "Campus Auditorium",
            "Computer Lab 1",
            "Art Studio A",
            "Conference Center",
            "Basketball Gym",
            "Music Hall",
            "Tech Expo Center",
            "Photography Studio",
            "Career Services Room",
            "Volleyball Court",
            "Student Union Ballroom",
            "Innovation Lab",
            "Central Park Lawn",
            "Internship Office",
            "Athletics Track",
            "Coffeehouse",
            "Web Lab",
            "Sculpture Garden",
            "Graduate Studies Office"
        ]
        events = []
        for i in range(20):
            cat = cat_list[i % len(cat_list)]
            events.append(Event(
                name=event_names[i],
                date=date.today() + timedelta(days=i),
                location=event_locations[i],
                description=event_descriptions[i],
                category_id=cat.id
            ))
        db.session.add_all(events)
        db.session.commit()
        
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_db_if_empty()
    app.run(debug=True)