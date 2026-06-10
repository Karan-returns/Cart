from django.core.management.base import BaseCommand

from store.repositories.mongo import get_client, get_db


class Command(BaseCommand):
    help = "Verify MongoDB Atlas connection and show database name."

    def handle(self, *args, **options):
        client = get_client()
        client.admin.command("ping")
        db_name = get_db().name
        self.stdout.write(self.style.SUCCESS(f"Connected to MongoDB Atlas (database: {db_name})"))
