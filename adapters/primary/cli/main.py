import os
import sys
from email.policy import default

import click

from domain.models.ticket import Ticket, Status, Priority
from adapters.secondary.json_storage import JsonStorageAdapter

STATUS_CHOICES   = [s.value for s in Status]
PRIORITY_CHOICES = [p.value for p in Priority]

def get_storage() -> JsonStorageAdapter:
    filepath = os.environ.get("TICKETS_FILE", "tickets.json")
    storage = JsonStorageAdapter(filepath)
    return storage

def handle_error(message: str) -> None:
    click.echo(f"Error: {message}")
    sys.exit(1)

@click.group()
def cli():
    """Ticket Manager CLI"""
    pass

@cli.command()
@click.option("--title", required=True, help="Ticket title")
@click.option("--description", required=True, help="Ticket description")
@click.option("--priority", default="medium", type=click.Choice(PRIORITY_CHOICES))
@click.option("--tags", default="", help="Comma-seperated tags")
def create(title: str, description: str, priority: str, tags: str):
    """Create a new ticket"""
    try:
        tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
        ticket = Ticket(title=title, description=description, priority=Priority(priority), tags=tag_list)
        get_storage().save(ticket)
        click.echo("Ticket created")
        click.echo(f"Ticket ID: {ticket.id}")
    except ValueError as e:
        handle_error(e)

@cli.command(name='list')
@click.option("--status", default=None, type=click.Choice(STATUS_CHOICES))
@click.option("--priority", default=None, type=click.Choice(PRIORITY_CHOICES))
@click.option("--tag", default=None)
def list_tickets(status: str, priority: str, tag: str):
    """List all tickets"""
    tickets = get_storage().find_all(
        status=Status(status) if status else None,
        priority=Priority(priority) if priority else None,
        tag=tag
    )
    if not tickets:
        click.echo("No tickets found")
        return
    for ticket in tickets:
        click.echo(f"[{ticket.id}] {ticket.title} | {ticket.status} | {ticket.priority}")

@cli.command()
@click.argument("ticket_id")
def show(ticket_id):
    """Show ticket detail"""
    try:
        t = get_storage().find_by_id(ticket_id)
        click.echo(f"ID: {t.id}")
        click.echo(f"Title: {t.title}")
        click.echo(f"Description: {t.description}")
        click.echo(f"Status: {t.status.value}")
        click.echo(f"Priority: {t.priority.value}")
        click.echo(f"Tags: {', '.join(t.tags)}")
        click.echo(f"Created at: {t.created_at}")
    except KeyError:
        handle_error(f"ticket '{ticket_id}' not found")

@cli.command()
@click.argument("ticket_id", type=str)
@click.option("--status", required=True, type=click.Choice(["open", "in_progress", "done", "cancelled"]))
def update(ticket_id, status):
    """Update ticket status"""
    try:
        storage = get_storage()
        ticket = storage.find_by_id(ticket_id)
        ticket.status = Status(status)
        storage.update(ticket)
        click.echo(f"Ticket updated successfully")
        click.echo(f"Status: {ticket.status.value}")
    except KeyError:
        handle_error(f"ticket '{ticket_id}' not found")
    except ValueError as e:
        handle_error(e)