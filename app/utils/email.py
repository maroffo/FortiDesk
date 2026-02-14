# ABOUTME: Email utility functions for sending mail via Flask-Mail
# ABOUTME: Handles individual emails, announcements, and expiry reminder batches

from flask import current_app, render_template
from flask_mail import Message
from app import mail, db


def send_email(subject, recipients, html_body, text_body=None):
    """Send a single email via Flask-Mail."""
    msg = Message(
        subject=subject,
        recipients=recipients,
        html=html_body,
        body=text_body or '',
        sender=current_app.config.get('MAIL_DEFAULT_SENDER')
    )
    try:
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f'Failed to send email to {recipients}: {e}')
        return False


def send_announcement(announcement):
    """Send announcement email to relevant guardians/staff.

    If announcement.team_id is set, only send to guardians of athletes in that team
    and staff assigned to that team. Otherwise, send to all active guardians and staff.
    """
    from app.models import Athlete, Guardian, Staff, TeamStaffAssignment, Team
    from datetime import datetime

    recipients = set()

    if announcement.team_id:
        # Guardians of team athletes
        athletes = Athlete.query.filter_by(
            team_id=announcement.team_id, is_active=True
        ).all()
        for athlete in athletes:
            for guardian in athlete.guardians:
                if guardian.email and guardian.is_active:
                    recipients.add(guardian.email)
        # Staff assigned to team
        assignments = TeamStaffAssignment.query.filter_by(
            team_id=announcement.team_id, is_active=True
        ).all()
        for assignment in assignments:
            if assignment.staff and assignment.staff.email and assignment.staff.is_active:
                recipients.add(assignment.staff.email)
        # Head coach
        team = Team.query.get(announcement.team_id)
        if team and team.head_coach and team.head_coach.email:
            recipients.add(team.head_coach.email)
    else:
        # All guardians
        guardians = Guardian.query.filter_by(is_active=True).all()
        for g in guardians:
            if g.email:
                recipients.add(g.email)
        # All staff
        staff_members = Staff.query.filter_by(is_active=True).all()
        for s in staff_members:
            if s.email:
                recipients.add(s.email)

    if not recipients:
        current_app.logger.info(f'No recipients for announcement #{announcement.id}')
        return 0

    html_body = render_template('email/team_announcement.html',
                                announcement=announcement)
    sent_count = 0
    for recipient in recipients:
        if send_email(announcement.subject, [recipient], html_body):
            sent_count += 1

    announcement.email_sent_at = datetime.utcnow()
    announcement.recipient_count = sent_count
    db.session.commit()

    current_app.logger.info(
        f'Announcement #{announcement.id} sent to {sent_count}/{len(recipients)} recipients'
    )
    return sent_count


def send_expiry_reminders():
    """Send email reminders for documents expiring within 30 days.

    Sends to guardians for athlete documents, and directly to staff for staff documents.
    """
    from app.models import Document, Athlete, Staff
    from datetime import date, timedelta

    today = date.today()
    threshold = today + timedelta(days=30)

    expiring_docs = Document.query.filter(
        Document.is_active.is_(True),
        Document.expiry_date.isnot(None),
        Document.expiry_date <= threshold,
        Document.reminder_sent.is_(False),
    ).all()

    if not expiring_docs:
        current_app.logger.info('No expiring documents to send reminders for')
        return 0

    sent_count = 0
    for doc in expiring_docs:
        recipients = []
        entity_name = ''

        if doc.entity_type == 'athlete':
            athlete = Athlete.query.get(doc.entity_id)
            if athlete and athlete.is_active:
                entity_name = athlete.get_full_name()
                for guardian in athlete.guardians:
                    if guardian.email and guardian.is_active:
                        recipients.append(guardian.email)
        elif doc.entity_type == 'staff':
            staff = Staff.query.get(doc.entity_id)
            if staff and staff.is_active and staff.email:
                entity_name = staff.get_full_name()
                recipients.append(staff.email)

        if recipients:
            html_body = render_template('email/expiry_reminder.html',
                                        document=doc,
                                        entity_name=entity_name)
            for recipient in recipients:
                if send_email(
                    f'Document Expiry Reminder: {doc.title}',
                    [recipient],
                    html_body
                ):
                    sent_count += 1

            doc.reminder_sent = True

    db.session.commit()
    current_app.logger.info(f'Sent {sent_count} expiry reminder emails')
    return sent_count
