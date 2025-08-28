import pypsa
import pandas as pd


# ---- Beispiel-Daten laden ----
load_profile = pd.read_csv("../../Input/gesamt_lastprofil.csv", index_col=0, parse_dates=True)["Last [kW]"]
load_profile.index = pd.to_datetime("2019-" + load_profile.index, format="%Y-%d-%m %H:%M")

pv_profile = pd.read_csv("../../Input/Ninja/ninja_pv_germany.csv", sep=",", index_col=0, parse_dates=True, skiprows=3)["electricity"]
wind_profile = pd.read_csv("../../Input/Ninja/ninja_wind_germany.csv", sep=",", index_col=0, parse_dates=True, skiprows=3)["electricity"]

"""""
print("=== Load Profile ===")
print(load_profile.head())
print(load_profile.describe())

print("\n=== PV Profile ===")
print(pv_profile.head())
print(pv_profile.describe())

print("\n=== Wind Profile ===")
print(wind_profile.head())
print(wind_profile.describe())

# Prüfen, ob die Zeitindexlänge stimmt (8760 Stunden für ein Jahr)
print("\n=== Indexlängen ===")
print("Load profile:", len(load_profile))
print("PV profile:", len(pv_profile))
print("Wind profile:", len(wind_profile))
"""
network = pypsa.Network()
network.set_snapshots(range(8760))

network.add("Bus", "Stromnetz", carrier="electricity")
network.add("Bus", "battery_bus", carrier="battery")  # Speicher-Bus


network.add("Carrier","solar")
network.add("Carrier","wind")  
network.add("Carrier","battery")  
 
# Load
network.add("Load", "Verbrauch", bus="Stromnetz", p_set=load_profile)

# PV + Wind
network.add("Generator", "pv", bus="Stromnetz", p_nom_extendable=True, p_max_pu=pv_profile, capital_cost=0)
network.add("Generator", "wind", bus="Stromnetz", p_nom_extendable=True, p_max_pu=wind_profile, capital_cost=0)

# Batterie
network.add("Store", "battery", bus="battery_bus", e_nom_extendable=True, e_cyclic=True, capital_cost=0, efficiency_store=0.9, efficiency_dispatch=0.9)

# Lade-/Entlade-Links
network.add("Link", "charge", bus0="Stromnetz", bus1="battery_bus", p_nom_extendable=True, efficiency=0.95, capital_cost=0)
network.add("Link", "discharge", bus0="battery_bus", bus1="Stromnetz", p_nom_extendable=True, efficiency=0.95, capital_cost=0)

# Wichtiger Schritt: kein Slack-Bus → zwingt den Solver, PV/Wind/Batterie zu nutzen

network.optimize()

# ---- Ergebnisse ----
print("Optimale PV-Leistung [MW]:", network.generators.p_nom["pv"])
print("Optimale Wind-Leistung [MW]:", network.generators.p_nom["wind"])
print("Speicher-Kapazität [MWh]:", network.stores.e_nom["battery"])
print("Speicher-Ladeleistung [MW]:", network.links.p_nom["charge_link"])
print("Speicher-Entladeleistung [MW]:", network.links.p_nom["discharge_link"])
print("Gesamtkosten [€]:", network.objective)