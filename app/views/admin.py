# ABOUTME: Admin panel blueprint for user management
# ABOUTME: CRUD operations for users, role assignment, account activation/deactivation

from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from flask_babel import gettext as _
from app import db
from app.models import User
from app.forms.admin_forms import UserForm

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f):
    """Decorator to require admin role."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin():
            flash(_('Access denied. Admin privileges required.'), 'danger')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/users')
@login_required
@admin_required
def users():
    """List all users with pagination."""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    role_filter = request.args.get('role', '')

    query = User.query

    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (User.username.ilike(search_filter)) |
            (User.first_name.ilike(search_filter)) |
            (User.last_name.ilike(search_filter)) |
            (User.email.ilike(search_filter))
        )

    if role_filter:
        query = query.filter_by(role=role_filter)

    pagination = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )

    return render_template('admin/users.html',
                         pagination=pagination,
                         users=pagination.items,
                         search=search,
                         role_filter=role_filter)


@admin_bp.route('/users/new', methods=['GET', 'POST'])
@login_required
@admin_required
def user_new():
    """Create a new user."""
    form = UserForm()

    if form.validate_on_submit():
        if not form.password.data:
            flash(_('Password is required for new users.'), 'danger')
            return render_template('admin/user_form.html', form=form,
                                 title=_('New User'))

        try:
            user = User(
                username=form.username.data.strip(),
                email=form.email.data.strip().lower(),
                first_name=form.first_name.data.strip(),
                last_name=form.last_name.data.strip(),
                role=form.role.data,
                is_active=True
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()

            flash(_('User %(name)s created successfully!',
                    name=user.get_full_name()), 'success')
            return redirect(url_for('admin.user_detail', id=user.id))

        except Exception as e:
            db.session.rollback()
            flash(_('Error saving data. Please try again.'), 'danger')
            current_app.logger.error(f'Admin user operation failed: {e}')

    return render_template('admin/user_form.html', form=form,
                         title=_('New User'))


@admin_bp.route('/users/<int:id>')
@login_required
@admin_required
def user_detail(id):
    """View user details."""
    user = User.query.get_or_404(id)
    return render_template('admin/user_detail.html', user=user)


@admin_bp.route('/users/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def user_edit(id):
    """Edit an existing user."""
    user = User.query.get_or_404(id)
    form = UserForm(
        original_username=user.username,
        original_email=user.email,
        obj=user
    )

    if form.validate_on_submit():
        try:
            user.username = form.username.data.strip()
            user.email = form.email.data.strip().lower()
            user.first_name = form.first_name.data.strip()
            user.last_name = form.last_name.data.strip()
            user.role = form.role.data
            if form.password.data:
                user.set_password(form.password.data)

            db.session.commit()

            flash(_('User %(name)s updated successfully!',
                    name=user.get_full_name()), 'success')
            return redirect(url_for('admin.user_detail', id=user.id))

        except Exception as e:
            db.session.rollback()
            flash(_('Error saving data. Please try again.'), 'danger')
            current_app.logger.error(f'Admin user operation failed: {e}')

    return render_template('admin/user_form.html', form=form,
                         title=_('Edit User'), user=user)


@admin_bp.route('/users/<int:id>/toggle-active', methods=['POST'])
@login_required
@admin_required
def user_toggle_active(id):
    """Activate or deactivate a user account."""
    user = User.query.get_or_404(id)

    if user.id == current_user.id:
        flash(_('You cannot deactivate your own account.'), 'danger')
        return redirect(url_for('admin.user_detail', id=user.id))

    try:
        user.is_active = not user.is_active
        db.session.commit()

        if user.is_active:
            flash(_('User %(name)s activated successfully.',
                    name=user.get_full_name()), 'success')
        else:
            flash(_('User %(name)s deactivated successfully.',
                    name=user.get_full_name()), 'success')

    except Exception as e:
        db.session.rollback()
        flash(_('Error saving data. Please try again.'), 'danger')
        print(f"Error: {e}")

    return redirect(url_for('admin.user_detail', id=user.id))
