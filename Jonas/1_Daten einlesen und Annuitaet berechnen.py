# Importieren aller notwendigen Bibliotheken
import pypsa
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Importieren von .csv-Dateien und abspeichern in DataFrames
df_data = pd.read_csv("Data/data_PyPSA_1.csv")
df_wind = pd.read_csv("wind_Nordex N27_150.csv", sep = ",", decimal = ".", usecols = ["electricity in kw"]) #Einlesen von Winddaten

#Einlesen einzelner Spalten im DataFrame
df_strompreis = df_data["Strompreis [Euro/kWh]"]            
df_last = df_data["Netzlast [kW]"]

# Berechnung der Jährlichen Stromkosten
ref_kosten = sum(df_last * df_strompreis)

# Berechnung der Annuität einer Investition
zinssatz = 0.02      
lebensdauer_batterie = 20     # Jahre
invest_kosten_batterie = 750  # Euro

annuitaet_batterie = invest_kosten_batterie*((1+zinssatz)**lebensdauer_batterie)*zinssatz/((1+zinssatz)**lebensdauer_batterie-1)



