from app import app, db
from app.forms import UserForm
from flask import render_template, redirect, url_for, request, session, flash, abort
from app.models import Event, Registration, Category, User
from app.forms import EventForm, LoginForm
from datetime import date

@app.before_request
def require_login():
    allowed_routes = ['login', 'register_user', 'static']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect(url_for('login'))
    
@app.context_processor
def inject_username():
    return dict(session_username=session.get('username'))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/users')
def user():
    if 'username' not in session:
        flash('Please log in to view events.', 'warning')
        return redirect(url_for('login'))
    user = User.query.filter_by(username=session['username']).first()
    selected_category = request.args.get('category', 'all')
    categories = Category.query.order_by(Category.name).all()
    if selected_category == 'all':
        events = Event.query.order_by(Event.date, Event.name).all()
    else:
        events = Event.query.filter_by(category_id=int(selected_category)).order_by(Event.date, Event.name).all()
    registrations = {reg.event_id for reg in user.registrations}
    return render_template(
        'users.html',
        events=events,
        registrations=registrations,
        categories=categories,
        selected_category=selected_category
    )

@app.route('/register', methods=['GET', 'POST'])
def register_user():
    form = UserForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            firstname=form.firstname.data,
            lastname=form.lastname.data,
            email=form.email.data
        )
        db.session.add(user)
        db.session.commit()
        flash('Account created! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('user_form.html', form=form, title="Register")

@app.route('/attendance/<int:event_id>')
def get_attendance(event_id):
    event = Event.query.get_or_404(event_id)
    registrations = Registration.query.filter_by(event_id=event_id).all()
    attendees = [User.query.get(reg.user_id) for reg in registrations]
    total_attendance = len(attendees)
    return render_template(
        'attendance.html',
        event=event,
        attendees=attendees,
        total_attendance=total_attendance
    )

@app.route('/admin')
def admin_page():
    users = User.query.all()
    return render_template('admin.html', users=users)

@app.route('/admin/add', methods=['GET', 'POST'])
def add_user():
    form = UserForm()
    if form.validate_on_submit():
        new_user = User(username=form.username.data, email=form.email.data, firstname=form.firstname.data, lastname=form.lastname.data)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('admin_page'))
    return render_template('user_form.html', form=form, title="Add User")

@app.route('/admin/edit/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = UserForm(obj=user)
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.firstname = form.firstname.data
        user.lastname = form.lastname.data
  # Consider using hashing!
        db.session.commit()
        return redirect(url_for('admin_page'))
    return render_template('user_form.html', form=form, title="Edit User")

@app.route('/admin/delete/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('admin_page'))

@app.route('/events')
def events():
    events = Event.query.all()
    return render_template('events.html', events=events)

@app.route('/events/add', methods=['GET', 'POST'])
def add_event():
    if not session.get('is_admin'):
        abort(403)
    form = EventForm()
    # Populate category choices
    form.category_id.choices = [(c.id, c.name) for c in Category.query.order_by(Category.name).all()]
    if form.validate_on_submit():
        event = Event(
            name=form.name.data,
            date=form.date.data,
            location=form.location.data,
            description=form.description.data,
            category_id=form.category_id.data
        )
        db.session.add(event)
        db.session.commit()
        return redirect(url_for('events'))
    return render_template('event_form.html', form=form, title="Add Event")

@app.route('/events/edit/<int:event_id>', methods=['GET', 'POST'])
def edit_event(event_id):
    if not session.get('is_admin'):
        abort(403)
    event = Event.query.get_or_404(event_id)
    form = EventForm(obj=event)
    # Populate category choices
    form.category_id.choices = [(c.id, c.name) for c in Category.query.order_by(Category.name).all()]
    if form.validate_on_submit():
        event.name = form.name.data
        event.date = form.date.data
        event.location = form.location.data
        event.description = form.description.data
        event.category_id = form.category_id.data
        db.session.commit()
        return redirect(url_for('events'))
    return render_template('event_form.html', form=form, title="Edit Event")

@app.route('/events/delete/<int:event_id>', methods=['POST'])
def delete_event(event_id):
    if not session.get('is_admin'):
        abort(403)
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    return redirect(url_for('events'))

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            session['username'] = user.username
            session['is_admin'] = user.is_admin  # Add this line
            flash('Login successful!', 'success')
            return redirect(url_for('user'))
        else:
            flash('Username not found.', 'danger')
    return render_template('login.html', form=form, title="Login")

@app.route('/register_event/<int:event_id>', methods=['POST'])
def register_event(event_id):
    if 'username' not in session:
        flash('Please log in to register for events.', 'warning')
        return redirect(url_for('login'))
    user = User.query.filter_by(username=session['username']).first()
    if not Registration.query.filter_by(user_id=user.id, event_id=event_id).first():
        reg = Registration(user_id=user.id, event_id=event_id)
        db.session.add(reg)
        db.session.commit()
        flash('Registered for event!', 'success')
    return redirect(url_for('user'))

@app.route('/unregister_event/<int:event_id>', methods=['POST'])
def unregister_event(event_id):
    if 'username' not in session:
        flash('Please log in to unregister from events.', 'warning')
        return redirect(url_for('login'))
    user = User.query.filter_by(username=session['username']).first()
    reg = Registration.query.filter_by(user_id=user.id, event_id=event_id).first()
    if reg:
        db.session.delete(reg)
        db.session.commit()
        flash('Unregistered from event.', 'info')
    return redirect(url_for('user'))

@app.route('/attendance_all')
def attendance_all():
    events = Event.query.all()
    event_attendance = []
    for event in events:
        registrations = Registration.query.filter_by(event_id=event.id).all()
        attendees = [User.query.get(reg.user_id) for reg in registrations]
        event_attendance.append({
            'event': event,
            'attendees': attendees,
            'total': len(attendees)
        })
    return render_template('attendance_all.html', event_attendance=event_attendance)

@app.route('/schema')
def schema():
    # Import models here to ensure latest definitions are used
    from app.models import User, Event, Registration, Category

    models = [User, Event, Registration, Category]
    schema_info = []

    for model in models:
        columns = []
        for col in model.__table__.columns:
            columns.append({
                'name': col.name,
                'type': str(col.type),
                'primary_key': col.primary_key,
                'nullable': col.nullable,
                'unique': col.unique,
            })
        # Gather relationships for this model
        rels = []
        for rel in model.__mapper__.relationships:
            rels.append({
                'name': rel.key,
                'target': rel.mapper.class_.__name__,
                'direction': str(rel.direction)
            })
        schema_info.append({
            'model': model.__name__,
            'columns': columns,
            'relationships': rels
        })
    return render_template('schema.html', schema_info=schema_info)