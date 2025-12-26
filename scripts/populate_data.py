"""
Populate database with realistic Tunisian farm data.

Run with: python manage.py shell < scripts/populate_data.py
Or: python manage.py runscript populate_data (if django-extensions is installed)
"""

import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal

import numpy as np
from faker import Faker

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crop_monitoring.settings')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from farms.models import FarmProfile, FieldPlot
from sensors.models import SensorReading

User = get_user_model()
fake = Faker()

# ============================================
# TUNISIAN FARM DATA
# ============================================

TUNISIAN_FARMERS = [
    {"username": "ahmed_benzarti", "email": "ahmed.benzarti@email.tn", "first_name": "Ahmed", "last_name": "Ben Zarti", "role": "farmer"},
    {"username": "fatma_trabelsi", "email": "fatma.trabelsi@email.tn", "first_name": "Fatma", "last_name": "Trabelsi", "role": "farmer"},
    {"username": "mohamed_hammami", "email": "mohamed.hammami@email.tn", "first_name": "Mohamed", "last_name": "Hammami", "role": "farmer"},
    {"username": "leila_bouazizi", "email": "leila.bouazizi@email.tn", "first_name": "Leila", "last_name": "Bouazizi", "role": "farmer"},
    {"username": "karim_mejri", "email": "karim.mejri@email.tn", "first_name": "Karim", "last_name": "Mejri", "role": "farmer"},
]

TUNISIAN_FARMS = [
    # Cap Bon region - citrus and vegetables
    {
        "name": "Ferme El Haouaria",
        "location": "El Haouaria, Cap Bon",
        "size_hectares": 45,
        "crop_type": "Citrus",
        "plots": [
            {"name": "Orangeraie Nord", "crop_variety": "Orange Malta", "area_hectares": 15},
            {"name": "Orangeraie Sud", "crop_variety": "Orange Thomson", "area_hectares": 12},
            {"name": "Citronniers", "crop_variety": "Citron Beldi", "area_hectares": 8},
            {"name": "Mandariniers", "crop_variety": "Mandarine Clémentine", "area_hectares": 10},
        ]
    },
    # Sfax region - olives
    {
        "name": "Domaine Oléicole Sfax",
        "location": "Sfax, Gouvernorat de Sfax",
        "size_hectares": 120,
        "crop_type": "Olives",
        "plots": [
            {"name": "Oliveraie Chemlali", "crop_variety": "Chemlali de Sfax", "area_hectares": 50},
            {"name": "Oliveraie Chetoui", "crop_variety": "Chetoui", "area_hectares": 40},
            {"name": "Jeunes Oliviers", "crop_variety": "Koroneiki", "area_hectares": 30},
        ]
    },
    # Kairouan region - cereals
    {
        "name": "Exploitation Céréalière Kairouan",
        "location": "Kairouan, Centre-Ouest",
        "size_hectares": 200,
        "crop_type": "Cereals",
        "plots": [
            {"name": "Champ de Blé A", "crop_variety": "Blé dur Karim", "area_hectares": 80},
            {"name": "Champ de Blé B", "crop_variety": "Blé dur Maali", "area_hectares": 60},
            {"name": "Orge", "crop_variety": "Orge Manel", "area_hectares": 40},
            {"name": "Avoine", "crop_variety": "Avoine locale", "area_hectares": 20},
        ]
    },
    # Sidi Bouzid - vegetables
    {
        "name": "Ferme Maraîchère Sidi Bouzid",
        "location": "Sidi Bouzid, Centre",
        "size_hectares": 35,
        "crop_type": "Vegetables",
        "plots": [
            {"name": "Tomates Serre 1", "crop_variety": "Tomate Rio Grande", "area_hectares": 5},
            {"name": "Tomates Plein Champ", "crop_variety": "Tomate Marmande", "area_hectares": 8},
            {"name": "Piments", "crop_variety": "Piment Baklouti", "area_hectares": 6},
            {"name": "Poivrons", "crop_variety": "Poivron Marconi", "area_hectares": 4},
            {"name": "Oignons", "crop_variety": "Oignon Rouge de Tropea", "area_hectares": 7},
            {"name": "Pommes de Terre", "crop_variety": "Spunta", "area_hectares": 5},
        ]
    },
    # Tozeur - dates
    {
        "name": "Oasis Deglet Nour Tozeur",
        "location": "Tozeur, Sud-Ouest",
        "size_hectares": 25,
        "crop_type": "Dates",
        "plots": [
            {"name": "Palmeraie Principale", "crop_variety": "Deglet Nour", "area_hectares": 15},
            {"name": "Palmeraie Allig", "crop_variety": "Allig", "area_hectares": 5},
            {"name": "Palmeraie Khouat", "crop_variety": "Khouat Allig", "area_hectares": 5},
        ]
    },
    # Bizerte - cereals and livestock fodder
    {
        "name": "Domaine Agricole Bizerte",
        "location": "Bizerte, Nord",
        "size_hectares": 150,
        "crop_type": "Mixed Cereals",
        "plots": [
            {"name": "Blé Tendre", "crop_variety": "Blé tendre Salambo", "area_hectares": 50},
            {"name": "Blé Dur", "crop_variety": "Blé dur Khiar", "area_hectares": 40},
            {"name": "Triticale", "crop_variety": "Triticale Tcl2", "area_hectares": 30},
            {"name": "Fourrage", "crop_variety": "Luzerne", "area_hectares": 30},
        ]
    },
    # Nabeul - strawberries and early vegetables
    {
        "name": "Ferme Primeurs Nabeul",
        "location": "Nabeul, Cap Bon",
        "size_hectares": 20,
        "crop_type": "Early Vegetables",
        "plots": [
            {"name": "Fraises Sous Serre", "crop_variety": "Fraise Camarosa", "area_hectares": 4},
            {"name": "Fraises Festival", "crop_variety": "Fraise Festival", "area_hectares": 3},
            {"name": "Concombres", "crop_variety": "Concombre Alpha", "area_hectares": 5},
            {"name": "Courgettes", "crop_variety": "Courgette Diamant", "area_hectares": 4},
            {"name": "Haricots Verts", "crop_variety": "Haricot Contender", "area_hectares": 4},
        ]
    },
]

def create_farmers():
    """Create Tunisian farmer users."""
    print("\n🌾 Creating Tunisian farmers...")
    farmers = []
    
    for farmer_data in TUNISIAN_FARMERS:
        user, created = User.objects.get_or_create(
            username=farmer_data["username"],
            defaults={
                "email": farmer_data["email"],
                "first_name": farmer_data["first_name"],
                "last_name": farmer_data["last_name"],
                "role": farmer_data["role"],
            }
        )
        if created:
            user.set_password("farmer123")  # Default password for testing
            user.save()
            print(f"  ✅ Created farmer: {user.first_name} {user.last_name}")
        else:
            print(f"  ℹ️  Farmer exists: {user.first_name} {user.last_name}")
        farmers.append(user)
    
    return farmers


def create_farms_and_plots(farmers):
    """Create Tunisian farms and plots."""
    print("\n🏡 Creating Tunisian farms and plots...")
    all_plots = []
    
    for i, farm_data in enumerate(TUNISIAN_FARMS):
        # Assign to a farmer (cycle through farmers)
        owner = farmers[i % len(farmers)]
        
        farm, created = FarmProfile.objects.get_or_create(
            name=farm_data["name"],
            owner=owner,
            defaults={
                "location": farm_data["location"],
                "size_hectares": farm_data["size_hectares"],
                "crop_type": farm_data["crop_type"],
            }
        )
        
        if created:
            print(f"  ✅ Created farm: {farm.name} ({farm.location})")
        else:
            print(f"  ℹ️  Farm exists: {farm.name}")
        
        # Create plots for this farm
        for plot_data in farm_data["plots"]:
            plot, created = FieldPlot.objects.get_or_create(
                name=plot_data["name"],
                farm=farm,
                defaults={
                    "crop_variety": plot_data["crop_variety"],
                    "area_hectares": plot_data["area_hectares"],
                }
            )
            
            if created:
                print(f"    📍 Created plot: {plot.name} - {plot.crop_variety}")
            else:
                print(f"    ℹ️  Plot exists: {plot.name}")
            
            all_plots.append(plot)
    
    return all_plots


def generate_sensor_readings(plots, days=7, readings_per_day=4):
    """Generate realistic sensor readings for all plots."""
    print(f"\n📊 Generating sensor readings ({days} days, {readings_per_day} readings/day)...")
    
    now = timezone.now()
    readings_created = 0
    
    for plot in plots:
        # Different baseline values based on crop type
        crop_variety = plot.crop_variety.lower()
        
        # Adjust baselines based on crop type
        if "olive" in crop_variety or "chemlali" in crop_variety or "chetoui" in crop_variety:
            moisture_base = 35  # Olives need less water
            temp_base = 25
        elif "tomate" in crop_variety or "piment" in crop_variety:
            moisture_base = 65  # Vegetables need more water
            temp_base = 22
        elif "fraise" in crop_variety:
            moisture_base = 70  # Strawberries need consistent moisture
            temp_base = 18
        elif "deglet" in crop_variety or "allig" in crop_variety:
            moisture_base = 30  # Dates are desert crops
            temp_base = 32
        elif "blé" in crop_variety or "orge" in crop_variety:
            moisture_base = 45  # Cereals moderate water
            temp_base = 20
        else:
            moisture_base = 55
            temp_base = 22
        
        for day in range(days):
            for reading_num in range(readings_per_day):
                hours_offset = day * 24 + (reading_num * 6)
                timestamp = now - timedelta(hours=hours_offset)
                
                hour = timestamp.hour
                if 6 <= hour < 12:
                    temp_modifier = 2
                elif 12 <= hour < 18:
                    temp_modifier = 5
                elif 18 <= hour < 22:
                    temp_modifier = 1
                else:
                    temp_modifier = -3
                
                moisture = moisture_base + np.random.normal(0, 10)
                temperature = temp_base + temp_modifier + np.random.normal(0, 2)
                humidity = 60 - (temperature - 20) * 1.5 + np.random.normal(0, 5)
                
                if np.random.random() < 0.05:
                    anomaly_type = np.random.choice(["low_moisture", "high_temp", "low_humidity"])
                    if anomaly_type == "low_moisture":
                        moisture = np.random.uniform(10, 30)
                    elif anomaly_type == "high_temp":
                        temperature = np.random.uniform(35, 42)
                    else:
                        humidity = np.random.uniform(15, 25)
                
                moisture = np.clip(moisture, 5, 95)
                temperature = np.clip(temperature, 5, 45)
                humidity = np.clip(humidity, 10, 95)
                
                # Create sensor readings
                for sensor_type, value in [
                    ("moisture", moisture),
                    ("temperature", temperature),
                    ("humidity", humidity),
                ]:
                    SensorReading.objects.create(
                        plot=plot,
                        timestamp=timestamp,
                        sensor_type=sensor_type,
                        value=Decimal(str(round(value, 2))),
                        source="simulator"
                    )
                    readings_created += 1
        
        print(f"  ✅ {plot.name}: {days * readings_per_day * 3} readings")
    
    print(f"\n📈 Total readings created: {readings_created}")
    return readings_created


def update_existing_data():
    """Update the existing Demo Farm with Tunisian data."""
    print("\n🔄 Updating existing demo data...")
    
    # Update existing farm if it exists
    try:
        demo_farm = FarmProfile.objects.get(name="Demo Farm")
        demo_farm.location = "Mornag, Ben Arous"
        demo_farm.crop_type = "Mixed Vegetables"
        demo_farm.size_hectares = 30
        demo_farm.save()
        print(f"  ✅ Updated Demo Farm to Tunisian location")
        
        # Update Plot 1
        try:
            plot1 = FieldPlot.objects.get(id=1)
            plot1.crop_variety = "Tomate Marmande"
            plot1.area_hectares = 8
            plot1.save()
            print(f"  ✅ Updated Plot 1 with Tunisian crop variety")
        except FieldPlot.DoesNotExist:
            pass
    except FarmProfile.DoesNotExist:
        print("  ℹ️  No Demo Farm to update")


def main():
    print("=" * 60)
    print("🇹🇳 POPULATING DATABASE WITH TUNISIAN FARM DATA")
    print("=" * 60)
    
    # Update existing data first
    update_existing_data()
    
    # Create farmers
    farmers = create_farmers()
    
    # Create farms and plots
    plots = create_farms_and_plots(farmers)
    
    # Generate sensor readings (7 days of data)
    generate_sensor_readings(plots, days=7, readings_per_day=4)
    
    print("\n" + "=" * 60)
    print("✅ DATABASE POPULATION COMPLETE!")
    print("=" * 60)
    print(f"\nSummary:")
    print(f"  👨‍🌾 Farmers: {User.objects.filter(role='farmer').count()}")
    print(f"  🏡 Farms: {FarmProfile.objects.count()}")
    print(f"  📍 Plots: {FieldPlot.objects.count()}")
    print(f"  📊 Sensor Readings: {SensorReading.objects.count()}")
    print(f"\nTest credentials:")
    print(f"  Admin: admin / admin")
    print(f"  Farmer: ahmed_benzarti / farmer123")
    print(f"  Farmer: fatma_trabelsi / farmer123")


if __name__ == "__main__":
    main()

