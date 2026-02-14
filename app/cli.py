# ABOUTME: Flask CLI commands for scheduled tasks (cron-compatible)
# ABOUTME: Provides send-expiry-reminders command for document expiry notifications

import click
from flask.cli import with_appcontext


def register_commands(app):
    """Register CLI commands with the Flask app."""

    @app.cli.command('send-expiry-reminders')
    @with_appcontext
    def send_expiry_reminders_cmd():
        """Send email reminders for documents expiring within 30 days.

        Usage: flask send-expiry-reminders
        Designed to be run via cron, e.g.:
            0 8 * * * cd /app && flask send-expiry-reminders
        """
        from app.utils.email import send_expiry_reminders

        click.echo('Checking for expiring documents...')
        sent_count = send_expiry_reminders()
        click.echo(f'Done. Sent {sent_count} reminder email(s).')
