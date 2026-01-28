from django.contrib import admin

from .models import HoraireTempsReel, Quotidienne, Station


@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    list_display = ["code", "nom", "departement", "lat", "lon", "alt"]
    list_filter = ["departement", "poste_ouvert", "poste_public"]
    search_fields = ["code", "nom"]
    ordering = ["nom"]


@admin.register(HoraireTempsReel)
class HoraireTempsReelAdmin(admin.ModelAdmin):
    list_display = ["station", "validity_time", "t", "u", "ff", "rr1"]
    list_filter = ["station"]
    ordering = ["-validity_time"]


@admin.register(Quotidienne)
class QuotidienneAdmin(admin.ModelAdmin):
    list_display = ["station", "nom_usuel", "date", "tn", "tx", "rr"]
    list_filter = ["station"]
    ordering = ["-date"]
