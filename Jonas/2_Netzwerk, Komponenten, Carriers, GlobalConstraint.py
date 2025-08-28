# Importieren aller notwendigen Bibliotheken
import pypsa
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Initialisierung des PyPSA-Netzwerks
network = pypsa.Network()
network.set_snapshots(df_data.index)
# oder network.set_snapshots(range(len(df_data)))

#Carrier hinzufügen
network.add("Carrier", name="grid_electricity", co2_emissions = grid_co2)
network.add("Generator", name = "grid", bus = "electricity", carrier = "grid_electricity", marginal_cost = df_strompreis, p_nom = np.inf)

# Bus hinzufügen
network.add("Bus", name = "electricity")

# Last hinzufügen
network.add("Load", name = "electrical_load", bus = "electricity", p_set = df_last)

# Generator hinzufügen
df_strompreis = df_data["Strompreis [Euro/kWh]"]
network.add("Generator", name = "grid", bus = "electricity", marginal_cost = df_strompreis, p_nom = np.inf)

# Speicher hinzufügen
# entweder als StorageUnit (mit Leistung und Energie) oder als Store (nur Energie)
network.add("StorageUnit", name = "battery_store", bus = "electricity", max_hours = 1, p_nom_extendable = True, capital_cost = annuitaet_batterie, efficiency_store = roundtrip_eff_batterie**0.5, efficiency_dispatch = roundtrip_eff_batterie**0.5) #Max_hours = 2 halbiert die Lade- und Entladeleistung
# oder
network.add("Store", name = "battery_store", bus = "electricity", e_nom_extendable = True, standing_loss = 0.005, capital_cost = annuitaet_batterie, efficiency = rountrip_eff_batterie**0.5)

# Link hinzufügen
network.add("Link", name = "battery_link", bus0 = "electricity", bus1 = "#zweiter bus", p_nom_extendable = True, capital_cost = annuitaet_batterie, efficiency = rountrip_eff_batterie**0.5)

#Global Constraint hinzufügen
network.add('GlobalConstraint', name = 'co2-limt', carrier_attribute = 'co2_emissions', sense = '<=', overwrite=True, constant =  co2_case1 * 0.5) #letzter Parameter gibt Vergleichswert an z.B. 0

# Optimierung des Netzwerks
network.optimize(solver_name = "gurobi")