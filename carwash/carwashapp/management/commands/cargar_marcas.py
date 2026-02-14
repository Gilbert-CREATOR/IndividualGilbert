from django.core.management.base import BaseCommand
from carwashapp.models import Marca, Modelo


class Command(BaseCommand):
    help = "Carga masiva de marcas y modelos de vehículos"

    def handle(self, *args, **options):

        data = {

            # ======================
            # JAPONESAS
            # ======================
            "Toyota": [
                "Corolla", "Camry", "Yaris", "Hilux", "RAV4",
                "Prado", "Land Cruiser", "Fortuner", "Tacoma"
            ],
            "Honda": [
                "Civic", "Accord", "Fit", "CR-V", "HR-V",
                "Pilot", "Ridgeline"
            ],
            "Nissan": [
                "Sentra", "Altima", "Versa", "X-Trail",
                "Rogue", "Frontier", "Navara", "Patrol"
            ],
            "Mazda": [
                "Mazda 2", "Mazda 3", "Mazda 6",
                "CX-3", "CX-5", "CX-9"
            ],
            "Mitsubishi": [
                "Lancer", "Outlander", "Montero",
                "ASX", "Eclipse Cross", "L200"
            ],
            "Subaru": [
                "Impreza", "Legacy", "Forester",
                "Outback", "XV"
            ],
            "Suzuki": [
                "Swift", "Vitara", "Jimny",
                "Baleno", "Celerio"
            ],

            # ======================
            # COREANAS
            # ======================
            "Hyundai": [
                "Accent", "Elantra", "Sonata",
                "Tucson", "Santa Fe", "Creta", "Kona"
            ],
            "Kia": [
                "Rio", "Cerato", "Optima",
                "Sportage", "Sorento", "Seltos", "Telluride"
            ],
            "Genesis": [
                "G70", "G80", "G90", "GV70", "GV80"
            ],

            # ======================
            # EUROPEAS
            # ======================
            "Volkswagen": [
                "Gol", "Polo", "Jetta", "Passat",
                "Tiguan", "Touareg", "Amarok"
            ],
            "Audi": [
                "A3", "A4", "A6", "A8",
                "Q3", "Q5", "Q7", "Q8"
            ],
            "BMW": [
                "Serie 1", "Serie 3", "Serie 5",
                "X1", "X3", "X5", "X6"
            ],
            "Mercedes-Benz": [
                "Clase A", "Clase C", "Clase E",
                "Clase S", "GLA", "GLC", "GLE"
            ],
            "Peugeot": [
                "208", "301", "308", "3008", "5008"
            ],
            "Renault": [
                "Clio", "Logan", "Sandero",
                "Duster", "Koleos", "Captur"
            ],
            "Citroën": [
                "C3", "C4", "C5 Aircross", "Berlingo"
            ],
            "Fiat": [
                "500", "Panda", "Argo", "Cronos",
                "Pulse", "Toro", "Strada"
            ],
            "Seat": [
                "Ibiza", "Leon", "Arona", "Ateca"
            ],
            "Skoda": [
                "Fabia", "Octavia", "Superb",
                "Karoq", "Kodiaq"
            ],
            "Volvo": [
                "S60", "S90", "XC40", "XC60", "XC90"
            ],

            # ======================
            # AMERICANAS
            # ======================
            "Ford": [
                "Fiesta", "Focus", "Fusion",
                "Escape", "Explorer", "Edge",
                "Ranger", "F-150", "Mustang"
            ],
            "Chevrolet": [
                "Spark", "Aveo", "Cruze", "Malibu",
                "Tracker", "Equinox", "Tahoe", "Silverado"
            ],
            "Dodge": [
                "Charger", "Challenger", "Durango", "Journey"
            ],
            "Jeep": [
                "Renegade", "Compass", "Cherokee",
                "Grand Cherokee", "Wrangler"
            ],
            "Ram": [
                "1500", "2500", "3500"
            ],

            # ======================
            # CHINAS
            # ======================
            "Chery": [
                "Tiggo 2", "Tiggo 4", "Tiggo 7", "Tiggo 8"
            ],
            "Geely": [
                "GX3", "Coolray", "Azkarra"
            ],
            "BYD": [
                "F3", "Song", "Tang", "Yuan Plus"
            ],
            "Great Wall": [
                "Wingle", "Poer", "Haval H6"
            ],
            "Haval": [
                "H2", "H6", "Jolion"
            ],
            "Zotye": [
                "Z100", "T600"
            ],
        }

        marcas_creadas = 0
        modelos_creados = 0

        for marca_nombre, modelos in data.items():
            marca, creada = Marca.objects.get_or_create(nombre=marca_nombre)
            if creada:
                marcas_creadas += 1

            for modelo_nombre in modelos:
                _, creada_modelo = Modelo.objects.get_or_create(
                    marca=marca,
                    nombre=modelo_nombre
                )
                if creada_modelo:
                    modelos_creados += 1

        self.stdout.write(self.style.SUCCESS("✅ Carga masiva completada"))
        self.stdout.write(f"Marcas creadas: {marcas_creadas}")
        self.stdout.write(f"Modelos creados: {modelos_creados}")
