from lookup_loader import FloatLookupLoader

bp_discharge_lookup = FloatLookupLoader("bp_discharge_20deg.csv")

bp_voltage = 7.19
bp_energy = bp_discharge_lookup.to_wh(bp_voltage)
print(str(bp_voltage) + "V -> " + str(bp_energy) + " Wh")