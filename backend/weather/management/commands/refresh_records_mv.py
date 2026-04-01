from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Rafraîchit la vue matérialisée mv_records_absolus"

    def handle(self, *args, **options):
        self.stdout.write("Rafraîchissement de mv_records_absolus...")
        with connection.cursor() as cur:
            cur.execute("REFRESH MATERIALIZED VIEW public.mv_records_absolus")
        self.stdout.write(self.style.SUCCESS("mv_records_absolus rafraîchie."))
