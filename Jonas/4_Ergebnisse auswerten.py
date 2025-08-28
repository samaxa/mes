# Allgemeine Übersicht
network.statistics()

#Betriebskosten ausgeben
operational_cost = network.statistics()["Operational Expenditure"].sum()

#Annuität ausgeben
annual_capital_cost = network.statistics()["Capital Expenditure"].sum()

# Übersicht einer Komponentengruppe
network.buses
network.loads
network.generators
network.storage_units
network.stores
network.links

# Übersicht einzelner Komponenten
network.storage_units, "name der Komponente"


#Systemkosten berechnen
kapitalkosten = (network.generators_t.p.sum() * network.generators.capital_cost).sum()
betriebskosten = (network.generators_t.p.sum() * network.generators.marginal_cost).sum()
gesamktkosten = kapitalkosten + betriebskosten

#Runden und mit string ausgeben
print ("Kosten System :", round(gesamtkosten,2), " €")


# Einzelne Werteserien plotten lassen
#Beispiel 1 (Serien)
network.loads_t.p.plot()                        #es werden alle Lastprofile in einem Diagramm gezeigt 
network.loads_t.p["elektrische Last"].plot()    #es wird nur das ausgewählte Lastprofil angezeigt
plt.tight_layout()
plt.show()  # wichtig!

#Beispiel 2 (einzelne Werte aus Serien)
network.loads_t.p.sum() #Summe der Leistungen

#Beispiel 3 (einzelne Werte)
networks.links.p_nom_opt.name

