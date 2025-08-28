import pandas as pd
import pypsa
import matplotlib.pyplot as plt
import os
import math
from tqdm import tqdm

#import pvlib
#from pvlib.pvsystem import PVSystem
# pvlib.location import Location
#from pvlib.modelchain import ModelChain


# 1. Netztopologie
snapshots = pd.date_range("2019-01-01 00:00", "2019-12-31 23:00", freq="H")
network = pypsa.Network()
network.set_snapshots(snapshots)

#2. Wetterdaten einlesen
    # Pfad zur CSV-Datei
pfad = r'C:\Users\sarah\Documents\GitHub\modellierung-energiesysteme\Input\ninja_pv_Köln.csv'

    # Metadaten-Zeilen überspringen
df = pd.read_csv(pfad, skiprows=3)

    # Zeitstempel setzen
df['local_time'] = pd.to_datetime(df['local_time'])
df.set_index('local_time', inplace=True)
# Fix: Doppelte Zeitstempel sicher entfernen
df = df[~df.index.duplicated(keep='first')]

# 3. PV-Zeitreihe exakt auf Snapshots bringen
pv_per_kwp = df['electricity'].reindex(snapshots).fillna(0)

# Plot erzeugen (Jahresverlauf, täglich aufsummiert)
pv_per_kwp.resample('D').sum().plot(figsize=(10, 4), title="Täglicher PV-Ertrag pro kWp")
plt.ylabel("kWh pro Tag")
plt.xlabel("Datum")
plt.tight_layout()
plt.show()


# 3. Lastprofil laden (haben wir noch nicht)
#last = pd.read_csv("lastgang.csv", index_col=0, parse_dates=True)
#load_series = last["load_kw"]  # z.. in kW

# 3. Dummy-Lastprofil erzeugen (temporär)
lastgang = pd.Series(0.3, index=snapshots) # z.B. 300 W Dauerverbrauch

# Plot für den Lastgang (täglich aufsummiert)
lastgang.resample('D').sum().plot(figsize=(10, 4), title="Täglicher Energiebedarf (Lastgang)")
plt.ylabel("kWh pro Tag")
plt.xlabel("Datum")
plt.tight_layout()
plt.show()


# 4. Komponenten hinzufügen

# Bus
network.add("Bus", name="electricity")

# Last
network.add("Load",
    name="demand",
    bus="electricity",
    p_set=lastgang  # hier eigentlich load_series verwenden wenn vorhanden
)

# PV-Generator
network.add("Generator",
    name="pv",
    bus="electricity",
    carrier="solar",
    p_nom_extendable=True,  # Optimierungsziel!
    p_max_pu=pv_per_kwp,    # Zeitreihe von pvlib
    capital_cost=950        # z.B. €/kWp ist ne Annahme!
)

# 5. Optimierung ausführen (alte Version)
network.optimize.create_model()
network.optimize.solve_model(solver_name='gurobi')

# 6. Ergebnis anzeigen
print(f"Optimale PV-Leistung: {network.generators.at['pv', 'p_nom']:.2f} kWp")