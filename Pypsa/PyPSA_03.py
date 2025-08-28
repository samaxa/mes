# Sie besitzen einen kleinen landwirtschaftlichen Betrieb mit Gewerbe und mehrere Wohneinheiten.
# Im Zuge Ihrer Bastelarbeiten konnten Sie eine alte Windturbine aus dem Jahr 1993 reaktivieren,
# eine Nordex N27 150 mit einer Nabenhöhe von 35 m. Diese wollen Sie neben dem Netzbezug zur Deckung
# der Stromlast nutzen. Darüber hinaus dürfen Sie ebenfalls mit einer Vergütung von 7,35 ct/kWh einspeisen.
# Ihre Wärmelast wird derzeit zentral mit einem Gaskessel gedeckt. Ermitteln Sie die mögliche Windeinspeisung
# an einem beliebigen Ort (z.B. Wohnort oder Geburtsort) und binden Sie diese Daten mit ein.

# Importieren Sie zunächst die notwendigen Bibliotheken
import pandas as pd
import pypsa
import matplotlib.pyplot as plt
import numpy as np

# Der Strom-, sowie der thermische Lastgang sind in der Datei "data_pypsa_03.csv" gespeichert. Lesen Sie diese mit pandas ein. Lesen Sie auch ihre Winddaten ein.
df_data = pd.read_csv('Input/data_pypsa_03.csv', sep=',', decimal='.')
df_wind = pd.read_csv('Input/wind_Nordex N27_150.csv', sep=',', decimal='.')

# # Plott erstellen mit matplotlib und anzeigen:
# plt.plot(df_data['electrical_load'], label = 'Electric Load')
# plt.plot(df_data['thermal_load'], label = 'Thermal Load')       # zeichnet nicht automatisch ein neues Diagramm, fügt in Diagramm ein.
# plt.plot(df_data['temperature'], label = 'Temperature')
# plt.legend()
# plt.show()

# oder direkt aus Pandas
df_data.plot()
plt.show()

# Basissystem erstellen
#Elektrisches System
wind_p_nom = 150 #kW - Nennleistung der Turbine - max el.leistung lieferbar
wind_p_pu = df_wind['electricity in kw'] / wind_p_nom # Lastgang in p.u. - per Unit = Leistung wird relativ zur Nennleistung angegeben

electricity_load    = df_data['electrical_load'] # Lastgang definiert aus csv.

# Parameter die gegeben sind
electricity_rate    =   0.409  #€/kWh
infeed_rate         =  -0.0735 #€/kWh Höchstwert für Windenergie-Anlagen bis 10kWp
grid_co2_emissions  =   0.380  #kg CO2_e/kWh # CO₂-Emissionsfaktor des Strommixes im Netz.

# Thermisches System
thermal_load = df_data['thermal_load']

boiler_p_nom = np.inf # Es gibt keine feste Obergrenze für die Leistung – der Boiler kann theoretisch beliebig viel liefern
boiler_eff = 0.95

thermal_store_e_nom = 200 #kWh (entsprich bei einer T-Spreizung von 45K ca. 3800L)
gas_rate = 0.123 #€/kWh_gas
gas_co2_emissions = 0.244 #kg CO2_e/kWh

# Netzwerk erstellen
network = pypsa.Network()
network.set_snapshots(range(8760))

#Elektrisches System
network.add('Bus', name = 'electricity_grid')
network.add('Bus', name = 'electricity_infeed')

network.add('Carrier', name = 'grid_electricity', co2_emissions = grid_co2_emissions)

network.add('Generator', name = 'Wind', bus = 'electricity_infeed',
            p_nom = wind_p_nom, p_max_pu = wind_p_pu)
network.add('Generator', name = 'Grid', bus = 'electricity_grid',
            p_nom = np.inf, marginal_cost = electricity_rate,
            carrier = 'grid_electricity')
network.add('Generator', name = 'Infeed', bus = 'electricity_infeed',
            p_nom = df_wind["electricity in kw"].max(), marginal_cost = infeed_rate, sign = -1)

network.add('Load', name = 'Electrical_Load', bus = 'electricity_grid',
            p_set = electricity_load)

network.add('Link', name = 'electricity_link', bus0 = 'electricity_infeed',
            bus1 = 'electricity_grid', p_nom = df_wind["electricity in kw"].max())

#Thermisches System

network.add('Bus', name = 'thermal')
network.add('Bus', name = 'gas_bus')

network.add('Carrier', name = 'gas', co2_emissions = gas_co2_emissions)

network.add('Generator', name = 'Gas', bus = 'gas_bus', p_nom = np.inf,
            marginal_cost = gas_rate, carrier = 'gas')

network.add('Load', name = 'Thermal_Load', bus = 'thermal', p_set = thermal_load)

network.add('Link', name = 'boiler', bus0 = 'gas_bus', bus1 = 'thermal',
            p_nom = boiler_p_nom, efficiency = boiler_eff)

#Solven: threads = wie viele CPU Kerne der Solver gleichzeitig nutzen darf; method = Steuert, welcher Algorithmus in Gurobi verwendet,  um das lineare Problem (LP) oder gemischt-ganzzahlige Problem (MIP) zu lösen. 0 - Primal Simplex, 1 - Dual Simplex, 2 - barrier, 3 - Gurobi entscheidet
network.optimize(solver_name = 'gurobi', threads = 1, method = 1)


# Lassen Sie sich mittels .statistics() die jährlichen Kosten ausgeben. und ermitteln Sie die THG-Emissionen.
operational_cost_1 = network.statistics()["Operational Expenditure"].sum()
print("Jährliche Betriebskosten:", round(operational_cost_1,2), "€/a")

co2_1 = network.generators_t.p.sum()["Grid"] * grid_co2_emissions + network.generators_t.p.sum()["Gas"] * gas_co2_emissions
print("THG-Emissionen:", round(co2_1/1000,2),"t")

# Nun wollen Sie prüfen, ob die Anschaffung eines BHKW‘s ökonomisch sinnvoll ist. Hierzu implementieren Sie auch das thermische System,
# welches aus einem Gasanschluss, einem Gaskessel, sowie der thermischen Last besteht. Ermitteln Sie die ökonomisch optimale Auslegung
# des BHKW‘s, sowie die jährlichen Strom- und Gaskosten.

# Erweitern Sie das System um das BHKW
# Parameter:
bhkw_eff_el = 0.35
bhkw_eff_th = 0.55

interest_rate = 0.02
bhkw_invest = 1000 * bhkw_eff_el  # €/kW_el * (kW_el/kW_gas) =  €/kW_gas
bhkw_lifespan = 20  # Jahre
bhkw_annuity = bhkw_invest * ((1 + interest_rate) ** bhkw_lifespan) * interest_rate / (
            (1 + interest_rate) ** bhkw_lifespan - 1)

# Add ins Netzwerk
network.add('Link', name = 'bhkw', bus0 = 'gas_bus', bus1 = 'electricity_grid',
            bus2 = 'thermal', p_nom_extendable = True, capital_cost = bhkw_annuity,
            efficiency = bhkw_eff_el, efficiency2 = bhkw_eff_th)

network.optimize(solver_name='gurobi', method = 1, threads =1)

# Lassen Sie sich die Größe des BHKWs ausgeben und berechnen Sie dessen Investitionskosten
bhkw_p_nom_opt = network.links.p_nom_opt.bhkw
bhkw_costs = bhkw_p_nom_opt * bhkw_annuity * bhkw_lifespan
print("BHKW:")
print("Optimale Leistung:", round(bhkw_p_nom_opt,2), "kW")
print("Gesamtkapitalkosten:", round(bhkw_costs,2),"€")

# Berechnen Sie erneut die jährlichen Kosten. Zudem berechnen Sie die Ersparnis gegenüber dem Basissystem und die Amortisationszeit des BHKWs
operational_cost_2 = network.statistics()["Operational Expenditure"].sum() + network.statistics()["Capital Expenditure"].sum()
print("Jährliche Kosten:", round(operational_cost_2,2), "€/a")

ersparnis = operational_cost_1 - operational_cost_2
print("Ersparnis:", round(ersparnis,2),"€")
print("Armotisationszeit:", round(bhkw_costs/ersparnis,2),"Jahre")

#Sie wollen die Eigenverbrauchsquote ihrere Windenergieanlage erhöhen und wollen daher eine Wärmepumpe in ihr Energiesystem integrieren
# um auch die Wärmelast über den durch Wind erzeugten Strom bedienen zu können. Implementieren Sie hierzu eine Wärmepumpe.
# Beachten Sie die Temperaturabhängigkeit des COPs, sowie der elektrischen Leistungsaufnahme einer Wärmepumpe.
# Im Folgenden wird anhand des Datenblatts der Wärmepumpe die Leistungszahl (COP) und die elektrische Leistungsaufnahme in Abhängikeit
# der Außentemperatur interpoliert. Die Daten für die Wärmepumpe basieren auf der Viessmann VITOCAL 252-A (Typ AWOT-E-AC-AF 251.A13)
# mit einer elektrischen Nennleistung nach DIN 14511 (A7/W35) von 1,56 kW.
# Quelle: https://community.viessmann.de/viessmann/attachments/viessmann/customers-heatpump-hybrid/109104/1/pa-viessmann-Vitocal-250-A-252-A-Monoblock-2,6-bis-13,4kW-2%20(1).pdf

T_VL        =   55 #°C
temp        =   [ -20, -15, -10,  -7,   2,   7,  10,  20,  30,  35] #°C
el_power    =   [3.87,4.20,4.45,4.60,2.25,2.23,2.27,2.33,2.27,2.27] #kW
cop         =   [1.81,1.98,2.18,2.30,2.83,3.40,3.66,4.80,6.37,6.37]
hp_p_nom    =   1.56 #kW

# Berechnen Sie zunächst den COP in Abhängigkeit der Außentemperatur. Verwenden Sie als erste Näherung dazu die Formel für den idealen Carnot-Wirkungsgrad [1].
# Der COP soll als neue Spalte dem Dataframe mit den Lastgängen hinzugefügt werden.
# # [1] https://de.wikipedia.org/wiki/Carnot-Wirkungsgrad
# # Anschließend interpolieren Sie den COP aus der oben abgebildeten Tabelle linear. Sie können die numpy Methode np.interp dazu nutzen.
# Auch diese Berechnung soll dem Dataframe als Spalte hinzugefügt werden. Vergleichen Sie die beiden Spalten anschließend in einem Plot.
# Hierbei bietet es sich an die Werte über die Temperatur aufzutragen. Nutzen Sie hierzu '.sort_values(['temperature']).plot(x='temperature')'

df_data['COP_Carnot'] = (T_VL + 273.15)/((T_VL + 273.15) - (df_data['temperature'] + 273.15))
df_data['COP_interp'] = np.interp(df_data['temperature'], temp, cop)
df_data["el_p_pu"]  = (np.interp(df_data['temperature'],temp,el_power))/hp_p_nom

df_data.loc[:,["temperature","COP_Carnot","COP_interp"]].sort_values(['temperature']).plot(x = 'temperature')

# Implementieren Sie die Wärmepumpe
# Paramerter:
heatpump_eff        = df_data["COP_interp"]
heatpump_p_max_pu   = df_data["el_p_pu"]
heatpump_invest = 960 #€/kWel
heatpump_lifespan = 20 #Jahre
heatpump_annuity    = heatpump_invest*((1+interest_rate)**heatpump_lifespan)*interest_rate/((1+interest_rate)**heatpump_lifespan-1)
# Network add
network.add('Link', name = 'heatpump', bus0 = 'electricity_grid', bus1 = 'thermal',
            p_nom_extendable = True, capital_cost = heatpump_invest,
            p_max_pu = heatpump_p_max_pu, efficiency = heatpump_eff)

# Optimieren Sie das Netzwerk
network.optimize(solver_name = 'gurobi', method = 1, threads = 1)

# Geben Sie mit den folgenden Funktionen die optimale Größe des BHKWs und der Wärmepumpe aus:
network.links.p_nom_opt

# Bestimmen Sie erneut die jährlichen Kosten
operational_cost_3 = network.statistics()["Operational Expenditure"].sum() + network.statistics()["Capital Expenditure"].sum()
print("Jährliche Kosten:", round(operational_cost_3,2), "€/a")

heatpump_p_nom_opt = network.links.p_nom_opt.heatpump
heatpump_costs = heatpump_p_nom_opt * heatpump_annuity * heatpump_lifespan
print("Wärmepumpe")
print("Optimale Leistung:",round(heatpump_p_nom_opt,2),"kW")
print("Investitionskosten:", round(heatpump_costs,2),"€")

ersparnis_2 = operational_cost_2 - operational_cost_3
print("Ersparnis:", round(ersparnis_2,2),"€/a")
print("Armotisationszeit:", round(heatpump_costs/ersparnis_2,2),"Jahre")

# Wie viel THG-Emissionen kann gegenüber dem Basissystem eingespart werden?
co2_2 = network.generators_t.p.sum()["Grid"] * grid_co2_emissions + network.generators_t.p.sum()["Gas"] * gas_co2_emissions
co2_reduktion = co2_1 - co2_2
print("THG-Emissionen:", round(co2_2/1000,2),"t")
print("CO2-Reduktion:")
print(round(co2_reduktion/1000,2),"t")
print(round(co2_reduktion/co2_1*100,2),"%")
