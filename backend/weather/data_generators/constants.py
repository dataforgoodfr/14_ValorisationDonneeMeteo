"""
Constants for weather data generation.
Contains station definitions and reproducibility settings.
"""

# Random seeds for reproducibility
RANDOM_SEED = 42
NUMPY_SEED = 42

# Default data generation parameters
DEFAULT_DAYS = 30
DEFAULT_BATCH_SIZE = 1000

# French weather stations with realistic coordinates
# Format: (code, name, lat, lon, alt, dept, type_poste, poste_public, poste_ouvert)
STATIONS = [
    ("75114001", "Paris-Montsouris", 48.8217, 2.3378, 75, 75, 0, True, True),
    ("69123001", "Lyon-Bron", 45.7272, 4.9444, 200, 69, 0, True, True),
    ("13055001", "Marseille-Marignane", 43.4356, 5.2148, 25, 13, 0, True, True),
    ("33063001", "Bordeaux-Mérignac", 44.8344, -0.6953, 47, 33, 0, True, True),
    ("59343001", "Lille-Lesquin", 50.5706, 3.0994, 47, 59, 0, True, True),
    ("31555001", "Toulouse-Blagnac", 43.6289, 1.3678, 151, 31, 0, True, True),
    ("44109001", "Nantes-Bouguenais", 47.1531, -1.6106, 26, 44, 0, True, True),
    ("67482001", "Strasbourg-Entzheim", 48.5439, 7.6281, 150, 67, 0, True, True),
    ("29075001", "Brest-Guipavas", 48.4478, -4.4186, 94, 29, 0, True, True),
    ("06088001", "Nice-Côte d'Azur", 43.6584, 7.2158, 4, 6, 0, True, True),
    ("74010001", "Chamonix", 45.9236, 6.8714, 1042, 74, 0, True, True),
    ("34172001", "Montpellier-Fréjorgues", 43.5761, 3.9631, 2, 34, 0, True, True),
    ("35238001", "Rennes-Saint-Jacques", 48.0697, -1.7339, 36, 35, 0, True, True),
    ("21231001", "Dijon-Longvic", 47.2681, 5.0900, 219, 21, 0, True, True),
    ("64445001", "Pau-Uzein", 43.3803, -0.4186, 183, 64, 0, True, True),
]
