import pypsa
import pandas as pd
import matplotlib.pyplot as plt #Plot Befehle werden sonst nicht angezeigt

# Die Lastgänge Ihres Auftraggebers sind in der Datei 'data_PyPSA_02.csv' gespeichert, lesen Sie diese mit pandas ein.

df_data = pd.read_csv('Input/data_PyPSA_2.csv', sep=',', decimal='.')
print(df_data)

# Definieren Sie dann alle Variablen, die Sie benötigen um das System zu implementieren.
# Basissystem
pv_p_nom = 10 #in kWp
pv_p_pu = df_data['PV Erzeugung']/pv_p_nom

gas_price = 0.123 #in €/kWh
electricity_price = 0.409 # in €/kWh
electricty_import_p_nom = 20 # Leistung des Netzanschlusses in kW
boiler_eff = 0.99 #Effizienz des Gasboilers in pu
boiler_p_nom = 10 # Thermische Leistung des boilers in kW

thermal_storage_capacity = 10 # Kapazität des Speichers in kWh
thermal_storage_self_discharge = 0.005 # Selbstentladungsverluste in pu pro Stunde

#Erweiterung
heating_rod_capital_cost = 10 # Annuität, In Euro für 2 kW
heating_rod_eff = 0.99 # Effizienz des Heizstabes
heating_rod_p_nom = 3 #Leistung des Heizstabes in kW

# Fügen Sie ihrem Netzwerk mit der methode add() nun die Komponenten ihres Energiesystems hinzu.
# Hinweis: Wenn Sie darauf achten, dass Ihre Einheiten über alle Komponenten einheitlich sind, müssen Sie nicht in MW und € rechnen, sondern können auch ct oder kW nutzen.
network = pypsa.Network()
network.set_snapshots(range(8784))

network.add('Bus',name = 'electrical')
network.add('Bus', name = 'thermal')

network.add('Load', name = 'elekrische Last', bus = 'electrical',
            p_set = df_data['elektrische Last'])
network.add('Load', name = 'thermische Last', bus = 'thermal',
           p_set = df_data['Wärmelast'])

network.add('Generator', name = 'Netzbezug', bus = 'electrical',
            p_nom = electricty_import_p_nom, marginal_cost = electricity_price)
network.add('Generator', name = 'PV', bus = 'electrical',
           p_nom = pv_p_nom, p_max_pu = pv_p_pu)
network.add('Generator', name = 'Erdgaskessel',
           bus = 'thermal',
           p_nom = boiler_p_nom,
            marginal_cost = gas_price/boiler_eff)

network.add('Store', name = 'Warmwasserspeicher', bus = 'thermal',
            e_nom = thermal_storage_capacity,
            standing_loss = thermal_storage_self_discharge)

network.optimize(solver_name= 'gurobi')

#Plotten der Ergebnisse
network.loads_t.p.plot()            # network.loads_t ist ein Zeitreihen-DataFrame aus PyPSA mit allen Lastwerten im Netz über die Snapshots hinweg. .p ist die Leistung 𝑝 der Loads in kW (oder der Einheit, in der du alles angegeben hast). .plot() ist eine Pandas/Matplotlib-Funktion, die diese Zeitreihen als Diagramm zeichnet.
network.generators_t.p.plot()       # network.generators_t ist das analoge Zeitreihen-DataFrame für Erzeuger (PV, Netzbezug, Gasboiler usw.).
plt.show()                          # Öffnet das Plot-Fenster in einer nicht-Jupyter-Umgebung (z. B. PyCharm). sorgt dafür, dass Matplotlib das erstellte Diagramm anzeigt.

# Berechnen Sie die Kosten des Systems.
kapitalkosten_basissystem = 0
betriebskosten_basissystem = (network.generators_t.p.sum() *
                            network.generators.marginal_cost).sum()
gesamtkosten_basissystem = (kapitalkosten_basissystem +
                            betriebskosten_basissystem )
print(f"Gesamtkosten des Basissystems: {gesamtkosten_basissystem:.2f} €")   # f vor dem String f"..." bedeutet: Formatierungsstring, in {...} wird als Text in den String eingefügt. :.2f = Formatvorgabe: Fließkommazahl (Float) mit 2 Nachkommastellen.


# Erweitern Sie das System um den Heizstab und führen Sie die Schritte ab der Optimierung erneut durch.
network.add('Link', name = 'Heizstab', bus0 = 'electrical',
            bus1 = 'thermal', efficiency = heating_rod_eff, p_nom = heating_rod_p_nom)

network.optimize(solver_name = 'gurobi')

kapitalkosten_erweiterung1 = heating_rod_capital_cost #€ als Anuität
betriebskosten_erweiterung1 = (network.generators_t.p.sum() *
                            network.generators.marginal_cost).sum()
gesamtkosten_erweiterung1 = (kapitalkosten_erweiterung1 +
                            betriebskosten_erweiterung1 )
print(f"Gesamtkosten mit Erweiterung 1: {gesamtkosten_erweiterung1:.2f} €")

# Erweitern Sie das System nun um den elektrischen Speicher und führen Sie die restlichen Schritte erneut durch.
# Anschließend können Sie die Kosten der unterschiedlichen Systemkonfigurationen vergleichen

#Erweiterung 2
electrical_storage_capacity = 5.0 # SENEC.Home V3 hybrid
electricial_storage_charge_capacity = 1.25 # SENEC.Home V3 hybrid
electricial_storage_discharge_capacity = 2.5 # SENEC.Home V3 hybrid
electrical_storage_capital_cost = 500 # Annuität 20 Jahre, SENEC.Home V3 hybrid
electrical_storage_eff = 0.97 # SENEC.Home V3 hybrid

network.add('Bus', name = 'storage_bus')

network.add('Store', name = 'Stromspeicher', bus = 'storage_bus',
            e_nom = electrical_storage_capacity)

network.add('Link', name = 'charge', bus0 = 'electrical', bus1 = 'storage_bus',
           p_nom = electricial_storage_charge_capacity,
            efficiency = electrical_storage_eff**0.5)

network.add('Link', name = 'discharge', bus0 = 'storage_bus',
            bus1 = 'electrical',
            p_nom = electricial_storage_discharge_capacity/electrical_storage_eff**0.5,
            efficiency = electrical_storage_eff**0.5)

network.optimize(solver_name = 'gurobi')

kapitalkosten_erweiterung2 = heating_rod_capital_cost + electrical_storage_capital_cost #€ als Anuität
betriebskosten_erweiterung2 = (network.generators_t.p.sum() *
                            network.generators.marginal_cost).sum()
gesamtkosten_erweiterung2 = (kapitalkosten_erweiterung2 +
                            betriebskosten_erweiterung2 )
print(f"Gesamtkosten mit Erweiterung 2: {gesamtkosten_erweiterung2:.2f} €")

print("Kosten Basissystem  :", round(gesamtkosten_basissystem,2), "€")
print("Kosten Erweiterung 1:", round(gesamtkosten_erweiterung1,2), "€")
print("Kosten Erweiterung 2:", round(gesamtkosten_erweiterung2,2), "€")

# Ausgabe ist gleich, aber beim f-String sieht der Code oft kürzer und aufgeräumter aus.:
# # Ohne f-String
# print("Kosten Erweiterung 2:", round(1234.567, 2), "€")
#
# # Mit f-String
# print(f"Kosten Erweiterung 2: {1234.567:.2f} €")