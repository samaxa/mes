import pypsa
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


temp_profile = pd.read_csv('Input/ninja_temp_germany.csv', index_col=0, parse_dates=True)["t2m"]
temp_profile_K = temp_profile # Außentemp. Köln: Umwandlung in Kelvin

plt.figure(figsize=(15,5))
plt.plot(temp_profile.index, temp_profile.values, color='blue', linewidth=1)
plt.title("Stromverbrauch über ein Jahr")
plt.xlabel("Datum")
plt.ylabel("Temperatur [°C]")
plt.grid(True)
plt.tight_layout()
plt.show()

# Parameter
temp_innen = 35 # Innentemperatur [K]
U = 1.2     # Wärmedurchgangskoeffizient [W/m²K]
A = 50      # Größe des Gewächshauses [m²]

# Wärmebedarf berechnen

Wärmebedarf = U * A * (temp_innen - temp_profile_K)  # [W]
Wärmebedarf [Wärmebedarf < 0] = 0  # Negativer Wärmebedarf wird auf 0 gesetzt

# COP Berechnung
temp        =   [ -20, -15, -10,  -7,   2,   7,  10,  20,  30,  35] #°C
el_power    =   [3.87,4.20,4.45,4.60,2.25,2.23,2.27,2.33,2.27,2.27]
cop         =   [1.81,1.98,2.18,2.30,2.83,3.40,3.66,4.80,6.37,6.37]

df_HP = np.interp(temp_profile_K, temp, cop)

df_results = pd.DataFrame({
    "Wärmebedarf [W]": Wärmebedarf,
    "Außentemperatur [C]": temp_profile,
    "COP": df_HP,
    })

plt.figure(figsize=(15,4))
plt.plot(df_results.index, df_results["Wärmebedarf [W]"], color="red")
plt.title("Wärmebedarf über das Jahr")
plt.xlabel("Datum")
plt.ylabel("Wärmebedarf [W]")
plt.grid(True)
plt.tight_layout()
plt.show()

plt.figure(figsize=(15,4))
plt.plot(df_results.index, df_results["COP"], color="green")
plt.title("Realer COP der Wärmepumpe über das Jahr")
plt.xlabel("Datum")
plt.ylabel("COP [-]")
plt.grid(True)
plt.tight_layout()
plt.show()

# Stromverbrauch der Wärmepumpe berechnen
df_results["stromverbrauch [W]"] = df_results["Wärmebedarf [W]"] / df_results["COP"]  # [W]

plt.figure(figsize=(15,4))
plt.plot(df_results.index, df_results["stromverbrauch [W]"], color="green")
plt.title("Stromverbrauch der Wärmepumpe über das Jahr")
plt.xlabel("Datum")
plt.ylabel("W")
plt.grid(True)
plt.tight_layout()
plt.show()

jahresverbrauch_hp = df_results["stromverbrauch [W]"].sum() / 1000  # Umwandlung in kWh
print(f"Jahresverbrauch der Wärmepumpe: {jahresverbrauch_hp:.2f} kWh")
