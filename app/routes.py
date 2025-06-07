from app import app, db
from app.forms import UserForm
from flask import render_template, redirect, url_for, request, session, flash, abort
from app.models import Event, Registration, Category, User
from app.forms import EventForm, LoginForm
from datetime import date
from flask_login import login_user, logout_user, login_required, current_user

# @app.before_request
# def require_login():
#     allowed_routes = ['login', 'register_user', 'static']
#     if request.endpoint not in allowed_routes and 'username' not in session:
#         return redirect(url_for('login'))
    
# @app.context_processor
# def inject_username():
#     return dict(session_username=session.get('username'))

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('home'))
        flash('Invalid credentials', 'danger')
    return render_template('login.html', form=form, title="Login")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out.', 'info')
    return redirect(url_for('login'))


@app.route('/users')
@login_required
def user():
    selected_category = request.args.get('category', 'all')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    categories = Category.query.order_by(Category.name).all()

    # Start with all events or filter by category
    if selected_category == 'all':
        query = Event.query
    else:
        query = Event.query.filter_by(category_id=int(selected_category))

    # Filter by date range if provided
    if start_date:
        query = query.filter(Event.date >= start_date)
    if end_date:
        query = query.filter(Event.date <= end_date)

    events = query.order_by(Event.date, Event.name).all()
    registrations = {reg.event_id for reg in current_user.registrations}

    return render_template(
        'users.html',
        user=current_user,
        events=events,
        registrations=registrations,
        categories=categories,
        selected_category=selected_category
    )

# @app.route('/register', methods=['GET', 'POST'])
# def register_user():
#     form = UserForm()
#     if form.validate_on_submit():
#         user = User(
#             username=form.username.data,
#             firstname=form.firstname.data,
#             lastname=form.lastname.data,
#             email=form.email.data
#         )
#         user.set_password(form.password.data)  # <-- Hash the password
#         db.session.add(user)
#         db.session.commit()
#         flash('Registration successful! Please log in.', 'success')
#         return redirect(url_for('login'))
#     return render_template('user_form.html', form=form, title="Register")

@app.route('/register', methods=['GET', 'POST'])
def register_user():
    form = UserForm()
    if form.validate_on_submit():
        # Check if username or email already exists
        existing_user = User.query.filter(
            (User.username == form.username.data) | (User.email == form.email.data)
        ).first()
        if existing_user:
            flash('Username or email already exists. Please choose another.', 'danger')
            return render_template('user_form.html', form=form, title="Register")
        user = User(
            username=form.username.data,
            firstname=form.firstname.data,
            lastname=form.lastname.data,
            email=form.email.data
        )
        user.set_password(form.password.data)  # <-- Hash the password
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('user_form.html', form=form, title="Register")

@app.route('/attendance/<int:event_id>')
@login_required
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
@login_required
def admin_page():
    if not current_user.is_admin:
        abort(403)
    users = User.query.all()
    return render_template('admin.html', users=users)

@app.route('/admin/add', methods=['GET', 'POST'])
@login_required
def add_user():
    if not current_user.is_admin:
        abort(403)
    form = UserForm()
    if form.validate_on_submit():
        new_user = User(username=form.username.data, email=form.email.data, firstname=form.firstname.data, lastname=form.lastname.data)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('admin_page'))
    return render_template('user_form.html', form=form, title="Add User")

@app.route('/admin/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if not current_user.is_admin:
        abort(403)
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
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        abort(403)
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('admin_page'))

@app.route('/events')
@login_required
def events():
    events = Event.query.all()
    return render_template('events.html', events=events)

@app.route('/events/add', methods=['GET', 'POST'])
@login_required
def add_event():
    if not current_user.is_admin:
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
@login_required
def edit_event(event_id):
    if not current_user.is_admin:
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
@login_required
def delete_event(event_id):
    if not current_user.is_admin:
        abort(403)
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    return redirect(url_for('events'))

# @app.route('/logout')
# @login_required
# def logout():
#     session.clear()
#     flash('You have been logged out.', 'info')
#     return redirect(url_for('login'))

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     form = LoginForm()
#     if form.validate_on_submit():
#         user = User.query.filter_by(username=form.username.data).first()
#         if user and user.check_password(form.password.data):
#             session['username'] = user.username
#             session['is_admin'] = user.is_admin
#             flash('Logged in successfully!', 'success')
#             return redirect(url_for('home'))
#         else:
#             flash('Invalid username or password.', 'danger')
#     return render_template('login.html', form=form, title="Login")




@app.route('/register_event/<int:event_id>', methods=['POST'])
@login_required
def register_event(event_id):
    if not Registration.query.filter_by(user_id=current_user.id, event_id=event_id).first():
        reg = Registration(user_id=current_user.id, event_id=event_id)
        db.session.add(reg)
        db.session.commit()
        flash('Registered for event!', 'success')
    return redirect(url_for('user'))

@app.route('/unregister_event/<int:event_id>', methods=['POST'])
@login_required
def unregister_event(event_id):
    reg = Registration.query.filter_by(user_id=current_user.id, event_id=event_id).first()
    if reg:
        db.session.delete(reg)
        db.session.commit()
        flash('Unregistered from event.', 'info')
    return redirect(url_for('user'))

@app.route('/attendance_all')
@login_required
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
@login_required
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

@app.route('/events_calendar')
@login_required
def events_calendar():
    events = Event.query.all()
    return render_template('events_calendar.html', events=events)