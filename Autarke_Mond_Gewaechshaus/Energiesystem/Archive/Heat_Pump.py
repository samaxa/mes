import pypsa
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

temp_profile = pd.read_csv("Input/ninja_temp_greenland.csv",skiprows=3, index_col=0, parse_dates=True)["t2m"]
temp_profile_K = temp_profile + 273.15  # Umwandlung in Kelvin

plt.figure(figsize=(15,5))
plt.plot(temp_profile_K.index, temp_profile_K.values, color='blue', linewidth=1)
plt.title("Temperaturverlauf in K")
plt.xlabel("Datum")
plt.ylabel("Temperatur [K]")
plt.grid(True)
plt.tight_layout()
plt.show()

# Parameter

temp_innen = 22 + 273.15     # Innentemperatur [K]
U = 0.15     # Wärmedurchgangskoeffizient [W/m²K]   ->  Polyurethan-Isolierung
A = 200      # Größe des Gewächshauses [m²]  -> Fläche von Dach und allen Wänden (Außenfläche)

# Wärmebedarf berechnen

Wärmebedarf = U * A * (temp_innen - temp_profile_K)  # [W]
Wärmebedarf [Wärmebedarf < 0] = 0  # Negativer Wärmebedarf wird auf 0 gesetzt



# COP Berechnung

effizienz = 0.5  # Effizienz der Wärmepumpe in Bezug auf Carnot Prozess
Vorlauftemperatur = 35 + 273.15  # Vorlauftemperatur [K]

COP_Carnot = Vorlauftemperatur / (Vorlauftemperatur - temp_profile_K)  # Carnot COP
realer_COP = COP_Carnot * effizienz  # Realer COP


df_results = pd.DataFrame({
    "Heizbedarf [W]": Wärmebedarf,
    "Realer COP": realer_COP,
    "Außentemperatur [C]": temp_profile,
    })

plt.figure(figsize=(15,4))
plt.plot(df_results.index, df_results["Heizbedarf [W]"], color="red")
plt.title("Wärmebedarf über das Jahr")
plt.xlabel("Datum")
plt.ylabel("Wärmebedarf [W]")
plt.grid(True)
plt.tight_layout()
plt.show()

plt.figure(figsize=(15,4))
plt.plot(df_results.index, df_results["Realer COP"], color="green")
plt.title("Realer COP der Wärmepumpe über das Jahr")
plt.xlabel("Datum")
plt.ylabel("COP")
plt.grid(True)
plt.tight_layout()
plt.show()

# Stromverbrauch der Wärmepumpe berechnen
df_results["stromverbrauch [W]"] = df_results["Heizbedarf [W]"] / df_results["Realer COP"]  # [W]



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



 

  
