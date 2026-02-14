# ABOUTME: Document management views for uploading, viewing, and tracking document expiry
# ABOUTME: Supports file upload/download for athlete and staff documents

import os
from datetime import date, timedelta

from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file, jsonify
from flask_login import login_required, current_user
from flask_babel import gettext as _

from app import db
from app.models import Document, Athlete, Staff
from app.forms.document_forms import DocumentUploadForm, DocumentSearchForm
from app.utils.uploads import save_upload, delete_upload

documents_bp = Blueprint('documents', __name__, url_prefix='/documents')


def _batch_resolve_entity_names(documents):
    """Batch-resolve entity names to avoid N+1 queries."""
    athlete_ids = {d.entity_id for d in documents if d.entity_type == 'athlete'}
    staff_ids = {d.entity_id for d in documents if d.entity_type == 'staff'}

    athlete_map = {}
    if athlete_ids:
        athletes = Athlete.query.filter(Athlete.id.in_(athlete_ids)).all()
        athlete_map = {a.id: a.get_full_name() for a in athletes}

    staff_map = {}
    if staff_ids:
        staff_members = Staff.query.filter(Staff.id.in_(staff_ids)).all()
        staff_map = {s.id: s.get_full_name() for s in staff_members}

    entity_names = {}
    for doc in documents:
        if doc.entity_type == 'athlete':
            entity_names[doc.id] = athlete_map.get(doc.entity_id, _('Unknown'))
        else:
            entity_names[doc.id] = staff_map.get(doc.entity_id, _('Unknown'))
    return entity_names


@documents_bp.route('/')
@login_required
def index():
    """List documents with filtering."""
    if not (current_user.is_admin() or current_user.is_coach()):
        flash(_('Permission denied.'), 'error')
        return redirect(url_for('main.dashboard'))

    page = request.args.get('page', 1, type=int)
    per_page = 20

    form = DocumentSearchForm(formdata=request.args)
    query = Document.query.filter_by(is_active=True)

    # Apply filters
    if form.document_type.data:
        query = query.filter(Document.document_type == form.document_type.data)

    if form.entity_type.data:
        query = query.filter(Document.entity_type == form.entity_type.data)

    if form.expiring_within.data:
        days = int(form.expiring_within.data)
        cutoff = date.today() + timedelta(days=days)
        query = query.filter(
            Document.expiry_date.isnot(None),
            Document.expiry_date <= cutoff
        )

    search = request.args.get('search', '')
    if search:
        query = query.filter(
            db.or_(
                Document.title.ilike(f'%{search}%'),
                Document.file_name.ilike(f'%{search}%'),
            )
        )

    pagination = query.order_by(Document.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    documents = pagination.items
    entity_names = _batch_resolve_entity_names(documents)

    return render_template('documents/index.html',
                           documents=documents,
                           pagination=pagination,
                           form=form,
                           search=search,
                           entity_names=entity_names)


@documents_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    """Upload a new document."""
    if not (current_user.is_admin() or current_user.is_coach()):
        flash(_('Permission denied.'), 'error')
        return redirect(url_for('documents.index'))

    form = DocumentUploadForm()

    # Populate entity_id choices with athletes by default
    athletes = Athlete.query.filter_by(is_active=True).order_by(Athlete.last_name).all()
    form.entity_id.choices = [(a.id, a.get_full_name()) for a in athletes]

    # If entity_type is staff (on POST or via query param), repopulate with staff
    if (request.method == 'POST' and form.entity_type.data == 'staff') or \
       request.args.get('entity_type') == 'staff':
        staff_members = Staff.query.filter_by(is_active=True).order_by(Staff.last_name).all()
        form.entity_id.choices = [(s.id, s.get_full_name()) for s in staff_members]

    if form.validate_on_submit():
        result = save_upload(form.file.data)
        if result is None:
            flash(_('File upload failed. Please check the file type and try again.'), 'error')
            return render_template('documents/upload.html', form=form)

        save_path, original_filename, file_size, mime_type = result

        document = Document(
            title=form.title.data,
            document_type=form.document_type.data,
            file_path=save_path,
            file_name=original_filename,
            file_size=file_size,
            mime_type=mime_type,
            entity_type=form.entity_type.data,
            entity_id=form.entity_id.data,
            expiry_date=form.expiry_date.data,
            notes=form.notes.data,
            created_by=current_user.id
        )

        db.session.add(document)
        db.session.commit()

        flash(_('Document uploaded successfully.'), 'success')
        return redirect(url_for('documents.view', id=document.id))

    return render_template('documents/upload.html', form=form)


@documents_bp.route('/api/entities/<entity_type>')
@login_required
def api_entities(entity_type):
    """Return JSON list of entities for dynamic form population."""
    if not (current_user.is_admin() or current_user.is_coach()):
        return jsonify([]), 403

    if entity_type == 'athlete':
        entities = Athlete.query.filter_by(is_active=True).order_by(Athlete.last_name).all()
        return jsonify([{'id': e.id, 'name': e.get_full_name()} for e in entities])
    elif entity_type == 'staff':
        entities = Staff.query.filter_by(is_active=True).order_by(Staff.last_name).all()
        return jsonify([{'id': e.id, 'name': e.get_full_name()} for e in entities])
    return jsonify([])


@documents_bp.route('/<int:id>')
@login_required
def view(id):
    """View document details."""
    if not (current_user.is_admin() or current_user.is_coach()):
        flash(_('Permission denied.'), 'error')
        return redirect(url_for('main.dashboard'))

    document = Document.query.get_or_404(id)
    if not document.is_active:
        flash(_('Document not found.'), 'error')
        return redirect(url_for('documents.index'))

    # Resolve entity
    if document.entity_type == 'athlete':
        entity = Athlete.query.get(document.entity_id)
    elif document.entity_type == 'staff':
        entity = Staff.query.get(document.entity_id)
    else:
        entity = None
    entity_name = entity.get_full_name() if entity else _('Unknown')

    return render_template('documents/view.html',
                           document=document,
                           entity=entity,
                           entity_name=entity_name)


@documents_bp.route('/<int:id>/download')
@login_required
def download(id):
    """Download the document file."""
    if not (current_user.is_admin() or current_user.is_coach()):
        flash(_('Permission denied.'), 'error')
        return redirect(url_for('main.dashboard'))

    document = Document.query.get_or_404(id)
    if not document.is_active:
        flash(_('Document not found.'), 'error')
        return redirect(url_for('documents.index'))

    if not os.path.exists(document.file_path):
        flash(_('File not found on server.'), 'error')
        return redirect(url_for('documents.view', id=document.id))

    return send_file(document.file_path, as_attachment=True, download_name=document.file_name)


@documents_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Soft delete a document and remove the file from disk."""
    if not current_user.is_admin():
        flash(_('Permission denied.'), 'error')
        return redirect(url_for('documents.index'))

    document = Document.query.get_or_404(id)
    document.is_active = False
    delete_upload(document.file_path)
    db.session.commit()

    flash(_('Document deleted.'), 'success')
    return redirect(url_for('documents.index'))


@documents_bp.route('/expiring')
@login_required
def expiring():
    """List documents expiring within N days."""
    if not (current_user.is_admin() or current_user.is_coach()):
        flash(_('Permission denied.'), 'error')
        return redirect(url_for('main.dashboard'))

    days = request.args.get('days', 30, type=int)
    entity_type = request.args.get('entity_type', '')

    cutoff = date.today() + timedelta(days=days)
    query = Document.query.filter(
        Document.is_active.is_(True),
        Document.expiry_date.isnot(None),
        Document.expiry_date <= cutoff
    )

    if entity_type:
        query = query.filter(Document.entity_type == entity_type)

    documents = query.order_by(Document.expiry_date.asc()).all()
    entity_names = _batch_resolve_entity_names(documents)

    return render_template('documents/expiring.html',
                           documents=documents,
                           entity_names=entity_names,
                           selected_days=days,
                           selected_entity_type=entity_type)
