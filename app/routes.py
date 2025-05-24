from app import app, db
from app.models import User
from app.forms import UserForm
from flask import render_template, redirect, url_for, request
#from flask_wtf.csrf import CSRFProtect



@app.route('/')
def home():
    return render_template('index.html')

@app.route('/users')
def user():
    return render_template('users.html')

@app.route('/register')
def register_user():
    return render_template('register.html')

#csrf = CSRFProtect(app)

# @app.before_request
# def disable_csrf_for_deletes():
#     """Allows delete requests without CSRF for specific routes."""
#     if request.endpoint in ['delete_user']:
#         #csrf._disable_on_request()

@app.route('/attendance/<event_id>')
def get_attendance(event_id):
    return render_template('attendance.html', event_id=event_id)

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
