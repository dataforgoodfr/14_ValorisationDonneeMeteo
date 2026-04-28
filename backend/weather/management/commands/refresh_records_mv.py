from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = (
        "Rafraîchit la vue matérialisée mv_records_battus et met à jour la cutoff_date"
    )

    def handle(self, *args, **options):
        self.stdout.write("Rafraîchissement de mv_records_battus...")
        with connection.cursor() as cur:
            cur.execute("REFRESH MATERIALIZED VIEW public.mv_records_battus")
        self.stdout.write(self.style.SUCCESS("mv_records_battus rafraîchie."))

        self.stdout.write("Mise à jour de la cutoff_date...")
        with connection.cursor() as cur:
            cur.execute("TRUNCATE public.mv_records_battus_meta;")
            cur.execute("""
                INSERT INTO public.mv_records_battus_meta (cutoff_date)
                SELECT MAX("AAAAMMJJ")::date FROM public."Quotidienne";
            """)
        self.stdout.write(self.style.SUCCESS("cutoff_date mise à jour."))
