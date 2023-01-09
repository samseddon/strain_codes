from pymeasure.instruments.keithley import Keithley2400                        
import numpy as np                                                             
import time                                                                    
                                                                               
                                                                               
                                                                               
                                                                               
def apply_v_to_piezo(keithley, V_var, n_step_per_V, t_step, start_t):                                         
    delta_V = np.abs(keithley.source_voltage - V_var)                 
    if(delta_V>0.):
        keithley.ramp_to_voltage(V_var, int(n_step_per_V*delta_V) + 1, t_step)
        if start_t - time.time() % 5: 
            print(keithley.source_voltage)

keithley = Keithley2400("GPIB::24")#v_keithley(lockin)                         
keithley.enable_source()                                                       
keithley.apply_voltage(200)                                                    
start_t = time.time()
n_step_per_V = 20.                                                             
t_step = 0.05 
V_var = 5
apply_v_to_piezo(keithley, V_var, n_step_per_V, t_step)
