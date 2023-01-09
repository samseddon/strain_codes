from pymeasure.instruments.keithley import Keithley2400    
keithley = Keithley2400("GPIB::24")#v_keithley(lockin)
keithley.enable_source()
print(keithley.source_voltage)
