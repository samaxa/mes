import pypsa
import pandas as pd
import matplotlib.pyplot as plt

# ---- Beispiel-Daten laden ----
load_profile = pd.read_csv("Input/gesamt_lastprofil.csv", index_col=0, parse_dates=True)["Last [kW]"]
load_profile.index = pd.to_datetime("2019-" + load_profile.index, format="%Y-%d-%m %H:%M")


load_profile = load_profile * 0.1 / 1000

plt.figure(figsize=(15,5))
plt.plot(load_profile.index, load_profile.values, color='blue', linewidth=1)
plt.title("Stromverbrauch über ein Jahr")
plt.xlabel("Datum")
plt.ylabel("Leistung [kW]")
plt.grid(True)
plt.tight_layout()
plt.show()

pv_profile = pd.read_csv("Input/ninja_pv_germany.csv",sep=",", index_col=0, parse_dates=True, skiprows=3)["electricity"]
wind_profile = pd.read_csv("Input/ninja_wind_germany.csv",sep=",", index_col=0, parse_dates=True, skiprows=3)["electricity"]






# ---- Netz aufsetzen ----
network = pypsa.Network()
network.set_snapshots(range(8760))

load_profile.index = network.snapshots
pv_profile.index = network.snapshots
wind_profile.index = network.snapshots


network.add("Carrier","solar")
network.add("Carrier","wind")  
network.add("Carrier","battery")  
network.add("Carrier","electricity")
# Bus
network.add("Bus", "Stromnetz", carrier="electricity")


# Last
network.add("Load","Verbrauch ",
            bus="Stromnetz",
            p_set=load_profile)

# PV-Generator
network.add("Generator","pv",
            bus="Stromnetz",
            p_max_pu=pv_profile,
            capital_cost=33000,     # €/MW
            marginal_cost=0,
            carrier="solar",
            p_nom_extendable=True)

# Wind-Generator
network.add("Generator","wind",
            bus="Stromnetz",
            p_max_pu=wind_profile,
            capital_cost=150000,    # €/MW
            marginal_cost=0,
            carrier="wind",
            p_nom_extendable=True)

# Speicher-Energie (MWh) → Store
network.add("Store",
            "battery",
            bus="Stromnetz",
            e_cyclic=True,               # Anfang = Ende
            e_nom_extendable=True,       # Energiespeichergröße [MWh]
            capital_cost=33000,       
            marginal_cost=0,
            carrier="battery",
            efficiency_store=0.9,
            efficiency_dispatch=0.9)


# ---- Optimierung ausführen ----

network.optimize()


# Verlauf des Ladezustandes der Batterie über das Jahr
battery_soc = network.stores_t.e["battery"]  # e = Energiemenge im Speicher über die Zeit

# Plot erstellen
plt.figure(figsize=(15,5))
plt.plot(battery_soc.index, battery_soc.values, color='orange', linewidth=1)
plt.title("Ladezustand des Batteriespeichers über das Jahr")
plt.xlabel("Datum")
plt.ylabel("Energie im Speicher [MWh]")
plt.grid(True)
plt.tight_layout()
plt.show()

# ---- Ergebnisse ----
print("Optimale PV-Leistung [MW]:", round(network.generators.p_nom_opt["pv"], 2))
print("Optimale Wind-Leistung [MW]:", round(network.generators.p_nom_opt["wind"], 2))
print("Speicher-Kapazität [MWh]:", round(network.stores.e_nom_opt["battery"], 2))
print("Gesamtkosten [€]:", round(network.objective, 2))

# Zeitreihen exportieren
#network.generators_t.p.to_csv("generator_output.csv")
#network.stores_t.e.to_csv("storage_energy.csv")
