#Erstellung einer Custom Constraint (Beispiel)
...
network.optimize(solver_name="gurobi") #wichtig: netzwerk muss schon einmal optimiert worden sein


dachflaeche = 20 #m^2
kollektor_p_pro_flaeche = 0.805 #kWp/m^2
pv_p_pro_flaeche = 0.2 #kWp/m^2

model = network.optimize.create_model()

model_pv_nom = model.variables["Generator-p_nom"].at["PV"]
model_kollektor_nom = model.variables["Generator-p_nom"].at["Kollektor"]

constraint_expression = model_pv_nom/pv_p_pro_flaeche + model_kollektor_nom/kollektor_p_pro_flaeche <= dachflaeche

model.add_constraints(constraint_expression, name = "Flächenbegrenzung")

network.optimize.solve_model(solver_name="gurobi")
