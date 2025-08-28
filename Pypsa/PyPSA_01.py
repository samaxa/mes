# PyPSA Übung 1: Dynamischer Stromtarif mit Heimspeicher
# Da seit 2025 dynamische Stromtarife verpflichtend angeboten werden müssen, überlegen Sie ihren Tarif zu einen solchen zu wechseln.
# Um Ihren Verbrauch zu flexibilisieren wollen Sie sich einen Lithium-Ionen-Heimspeicher zulegen. Ihnen liegen die Strompreise für 2024
# stündlich aufgeschlüsselt, sowie der Stromverbrauch ihres Eigenheims vor. Bestimmen Sie die ökonomisch optimale Größe des Heimspeichers.
# Die Kosten für den Heimspeicher können mit 750 €/kWh angenommen werden. Die Lebenszeit beträgt 20 Jahre, # der Zinssatz kann mit 2%
# angenommen werden. Die round trip Effizienz beträgt 95%. Standverluste können vernachlässigt werden.

# Importiere zunächst notwendige Bibliotheken:
import pypsa                # Python for Power Systems Analysis (PyPSA)
import pandas as pd         # Pandas for data analysis,  pd = kurzname
import numpy as np          # NumPy for numerical computations, np = kurzname

# Lesen Sie die Strompreise sowie Netzlast ein ('PyPSA_01.csv'), df = Dataframe, pd.read_csv(...) = pandas Funktion um csv zu lesen, sep=',' sagt womit sich spalten trennen, decimal='.' sagt welchen Zeichen die Nachkommastellen trennt
df_data = pd.read_csv('Input/data_PyPSA_1.csv', sep=',', decimal='.')
# nimmt Spalte (Strompreis, Netzlast) aus Datafram. Ergebnis ist eine Series (einspaltige Tabelle mit Index)
df_Strompreis = df_data['Strompreis [Euro/kWh]']
df_Netzlast = df_data['Netzlast [kW]']

print(df_Netzlast)  # Pycharm mus man genau sagen printe das jetzt - Jupiter Notebook würde es ausgeben mit df_Netzlast

# Berechnen Sie die Stromkosten ohne Heimspeicher:
ref_kosten = sum(df_Strompreis*df_Netzlast)
print(f"Referenzkosten ohne Speicher: {ref_kosten:.2f} €")


# Bauen Sie ein Modell auf, welches die Problemstellung abbildet
# ParameterSet:
zinssatz = 0.02                 # Zinsen in pu, pu = (Prozentuale Unit)?, 0.02 = 2%
lebensdauer_batterie = 20       # Lebensdauer der Batterie in Jahren
roundtrip_eff_batterie = 0.95   # Roundtrip Effizienz der Batterie
invest_kosten_batterie = 750    # in Euro
#Annuitätsformel:
annuitaet_batterie = invest_kosten_batterie*((1+zinssatz)**lebensdauer_batterie)*zinssatz/((1+zinssatz)**lebensdauer_batterie-1)

#Pypsa Modell erstellen:
network = pypsa.Network()  # erzeugt ein leeres Energiesystem-Objekt
network.set_snapshots(range(8784)) # Schaltjahr, Zeitpunkte also Stunden im Jahr 2024 für die das Modell rechnet

#Bus - „Netzknoten“, an den Erzeuger, Verbraucher und Speicher angeschlossen werden.
network.add("Bus", name = 'electricity')

#Load - Verbraucher der am Bus angeschlossen ist - p_set = df_Netzlast: Zeitreihe der Last (kW) aus der csv.
network.add("Load", name = 'electricity_load', bus = 'electricity', p_set = df_Netzlast)

#Generator - Erzeuger der am Bus angeschlossen ist - p_nom = np.inf: keine Leistungsbergenzung, p_nom = maximale Nennleistung die der Generator liefern kann - hier das netz liefern kann,
network.add("Generator", name = 'grid_power', bus = 'electricity', p_nom = np.inf, marginal_cost = df_Strompreis)

#Speicher
network.add("StorageUnit", name = 'battery_store', bus = 'electricity',
            p_nom_extendable = True,                            #optimieren Lassen
            capital_cost = annuitaet_batterie,                  #fixed period costs of extending P_nom/ jährliche investkosten pro kW
            max_hours = 1,                                      #max. state of charge capacity in terms of hours at full output capacity p_nom/ std in Vollast
            efficiency_store = roundtrip_eff_batterie**0.5,     #Wirkungsgrad beim Laden- Wurzel aus Roundtrip Effizienz weil : n-store = n_dispatch = n_roundtrip**0.5
            efficiency_dispatch = roundtrip_eff_batterie**0.5)

# Löse das Modell:
network.optimize(solver_name = 'gurobi')

#Geben Sie sich die größe des Batteriespeichers, dessen Gesamtkosten und die Gesamtkosten (Zielfunktion) aus
kosten_mit_speicher = (network.generators_t.p * network.generators_t.marginal_cost).sum().sum()
print(f"Kosten ohne Speicher: {ref_kosten:.2f} €")
print(f"Kosten mit Speicher:  {kosten_mit_speicher:.2f} €")
print(f"Ersparnis:            {ref_kosten - kosten_mit_speicher:.2f} € "
      f"({(1 - kosten_mit_speicher/ref_kosten)*100:.2f} %)")
print(network.statistics())