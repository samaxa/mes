# Erzeugungsprofil normieren wenn p_nom bekannt
df_pv = df_data["PV Erzeugung"]
pv_p_nom = 10 #kw

pv_pu = df_pv / pv_p_nom

#PV-Anlage mit Einspeisemöglichkeit
network.add("Bus", name = "electrical")
network.add("Bus", name = "PV")

network.add("Generator", name="PV",bus="PV", p_nom=pv_p_nom, p_max_pu=df_pv/pv_p_nom)
network.add("Generator", name="PV_infeed",bus="PV", p_nom=df_pv.max(), marginal_cost = einspeise_preis, sign = -1)

network.add("Link", name="electrical_link", bus0="PV", bus1="electrical", p_nom=df_pv.max())


#Wind-Anlage mit Einspeisemöglichkeit
network.add("Bus", name = "electrical")
network.add("Bus", name = "Wind")

network.add("Generator", name="Wind",bus="Wind", p_nom=wind_p_nom, p_max_pu=df_wind/wind_p_nom)
network.add("Generator", name="Wind_infeed",bus="Wind", p_nom=df_wind.max(), marginal_cost = einspeise_preis, sign = -1)

network.add("Link", name="electrical_link", bus0="Wind", bus1="electrical", p_nom=df_wind.max())


#Heizstab
network.add("Link", name = "Heizstab", bus0 = "electricity", bus1 = "thermal", p_nom = p_nom_heizstab, efficiency = eff_kessel)


#BHKW erstellen
bhkw_eff_el = 0.35
bhkw_eff_th = 0.55

zinssatz = 0.02
bhkw_invest = 1000 * bhkw_eff_el #da €/kW_el * (kW_el/kW_gas) = €/kW_gas ist
bhkw_lebensdauer = 20
bhkw_annuitaet = bhkw_invest*((1+zinssatz)**bhkw_lebensdauer)*zinssatz/((1+zinssatz)**bhkw_lebensdauer-1)

network.add("Bus", name = "electrical")
network.add("Bus", name = "thermal")
network.add("Bus", name = "gas")

network.add("Generator", name="gas_grid", bus="gas", p_nom=np.inf, marginal_cost = kosten_gas)

network.add("Link", name ="Kessel", bus0 = "gas", bus1= "thermal", p_nom= np.inf, efficiency = eff_kessel)
network.add("Link", name ="bhkw", bus0 = "gas", bus1 = "electrical", bus2 = "thermal", p_nom_extendable = True, efficiency = bhkw_eff_el, efficiency2 = bhkw_eff_th, capital_cost = bhkw_annuitaet)



#Wärmepumpe
T_VL        =   55 #°C
temp        =   [ -20, -15, -10,  -7,   2,   7,  10,  20,  30,  35] #°C
el_power    =   [3.87,4.20,4.45,4.60,2.25,2.23,2.27,2.33,2.27,2.27] #kW
cop         =   [1.81,1.98,2.18,2.30,2.83,3.40,3.66,4.80,6.37,6.37]
hp_p_nom    =   1.56 #kW

df_data['COP_interp'] = np.interp(df_data['temperature'], temp, cop) #Interpolation
df_data["el_p_pu"]  = (np.interp(df_data['temperature'],temp,el_power))/hp_p_nom 

heatpump_eff        = df_data["COP_interp"] 
heatpump_p_max_pu   = df_data["el_p_pu"] 
heatpump_invest = 960 #€/kWel
heatpump_lifespan = 20 #Jahre
heatpump_annuity    = heatpump_invest*((1+interest_rate)**heatpump_lifespan)*interest_rate/((1+interest_rate)**heatpump_lifespan-1)

network.add("Link", name="heatpump", bus0="electrical", bus1="thermal", p_nom_extendable=True, capital_cost=heatpump_annuity, p_max_pu=heatpump_p_max_pu, efficiency=heatpump_eff) 



