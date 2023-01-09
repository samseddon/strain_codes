#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 18 09:59:39 2019

@author: esingh
"""
from pymeasure.instruments.keithley import Keithley2400 
from pymeasure.instruments.srs import SR830
from datetime import datetime
from tkinter import filedialog
from tkinter import *
from prettytable import PrettyTable
import numpy as np
import matplotlib.pyplot as plt
import time
import sys
import interface_01




class v_keithley(object):
    
    def __init__(self, var_lockin):
        self.voltage_source = 0.0
        self.lockin = var_lockin
        print("keithley created")

    def ramp_to_voltage(self,v_target,n_points,t_ramp):  
        self.voltage_source = v_target
        #print("v_keith = {}".format(v_target))
        self.lockin.update(v_target)
    
class v_lockin(object):
    
    def __init__(self, x, y):
    
        self.slope = (np.min(y)-y[0])/(x[np.where(y==np.min(y))]-x[0])[0]
        self.intercept = y[0]
        self.magnitude =  y[0]
        print("slope = {}".format(self.slope))
    
    def update(self,v_keithley):  
        #print("v_kinlocki9n = {}".format(v_keithley))
        #print(v_keithley)
        self.magnitude = self.slope*v_keithley + self.intercept

class strain_device(object):
    def __init__(self, measure_bot,condition_bot, keithley,lockin,P,I,calb,V_min,V_max,n_step_per_V,t_step,amp,sign, t_wait, data_manager, name):
        self.measure_bot = measure_bot
        self.condition_bot = condition_bot
        self.current_force = 0.
        self.keithley = keithley
        self.lockin = lockin
        parameters = []
        self.P = P
        parameters.append(["P", P])
        self.I = I
        parameters.append(["I", I])
        self.calb = calb
        parameters.append(["calb", calb])
        self.V_min = V_min
        parameters.append(["V_min", V_min])
        self.V_max = V_max
        parameters.append(["V_max", V_max])
        self.n_step_per_V = n_step_per_V
        parameters.append(["n_step_per_V", n_step_per_V])
        self.t_step = t_step
        parameters.append(["t_step", t_step])
        self.amp = amp
        parameters.append(["amp", amp])
        self.sign = sign
        parameters.append(["sign", sign])
        self.t_wait = t_wait
        parameters.append(["t_wait", t_wait])
        self.t_0 = time.time()
        self.lockfile_name = name
        self.data_manager = data_manager
        self.data_manager.set_titles(["t in [s]", "F_set in [N]", "V_set in [V]","V_var in [V]", "delta in [V]"])
        self.data_manager.set_name(name)
        self.data_manager.save_parameters(parameters)
        self.current_I_old = 0.

    def apply_force(self, F):
        self.current_force = F
        V_var_lst = [self.amp*self.lockin.magnitude]
        I_old_lst = [self.current_I_old]
        delta_lst = [np.abs(self.get_V_set(F, self.calb, self.amp)-V_var_lst[-1])]
        t_lst = [time.time()-self.t_0]
        V_var = V_var_lst[-1]
        I_old = I_old_lst[-1]
        delta = delta_lst[-1]
        condition = self.condition_bot.go_to_next_force()
        while (not condition):
            V_var, I_old, delta = self.keep_force_constant(I_old_lst[-1])
            V_var_lst.append(V_var)
            I_old_lst.append(I_old)
            self.current_I_old = I_old
            delta_lst.append(delta)
            t_lst.append(time.time()-self.t_0)
            self.data_manager.add_Data([time.time()-self.t_0, F, self.get_V_set(F, self.calb, self.amp), V_var_lst[-1], delta_lst[-1]])
            self.measure_bot.measure()
            condition = self.condition_bot.go_to_next_force()
            print(not condition)
        print("goes to next F")
        return

    def keep_force_constant(self, I_old):
        V_set = self.get_V_set(self.current_force,self.calb,self.amp)
        V_var = self.amp*self.lockin.magnitude
        V_var, I_old, delta = self.PID(self.sign*V_var,V_set,self.P,self.I,I_old) 
        self.apply_v_to_piezo(V_var)
        return(V_var, I_old, delta)
    
    def get_V_set(self, F, calb, amp):
        V_set = F*calb*amp    
        return(V_set)
 
    def PID(self, V_var,V_set,P,I,I_old):  #may be delta_t
        delta = V_set-V_var
        I_new = I_old + (I*delta)
        V_new = P*( delta + I_new)
        return(V_new, I_new, delta)
    
    def apply_v_to_piezo(self, V_var):
        if (V_var < self.V_min or V_var > self.V_max):
            self.keithley.ramp_to_voltage(0, self.n_step_per_V, self.t_step)
            print("voltage on piezo is out of range that you defined")
            sys.exit()
        delta_V = np.abs(self.keithley.source_voltage - V_var)
        if(delta_V>0.):
            self.keithley.ramp_to_voltage(V_var,int(self.n_step_per_V*delta_V)+1,self.t_step)
        time.sleep(self.t_wait)

class data_manager(object):
    def __init__(self):
        self.save_path = filedialog.askdirectory()
        self.results = PrettyTable()
        self.results.border = False

    def set_titles(self, titles):
        self.results.field_names = titles

    def set_name(self, name):
        self.name = name

    def reset_table(self, titles, name):
        self.results = PrettyTable(titles)
        self.set_name(name)

    def save_parameters(self, parameters):
        param_table = PrettyTable(["Parameter","Value"])
        param_table.border = False
        for i in range(len(parameters)):
            param_table.add_row([parameters[i][0], parameters[i][1]])
        file = open(self.save_path+"/Parameters_"+ self.name +".txt", 'w')
        file.write(param_table.get_string())
        file.close()

    def add_Data(self, data):
        self.results.add_row(data)
        file = open(self.save_path+"/"+self.name+".txt", 'w')
        file.write(self.results.get_string())
        file.close()
        return

class click_condition_bot(object):
    def __init__(self, interface):
        self.interface = interface

    def go_to_next_force(self):
        condition = self.interface.check_condition()
        if(condition):
            time.sleep(2)
            self.interface.reset_condition()
        return(condition)

    def exit_measurement(self):
        return(interface.check_exit_measurement())

class empty_measurement_bot(object):
    def measure(self):
        return

class conductivity_measurement_bot(object):
    def __init__(self,keithley, V_min, V_max, n_steps, n_step_per_V, data_manager, t_step):
        self.V_min = V_min
        self.V_max = V_max
        self.n_steps = n_steps
        self.n_step_per_V = n_step_per_V
        self.data_manager = data_manager
        self.counter = 0
        self.force_data_path = ""
        self.t_step = t_step

    def get_force_path(self):
        self.force_data_path = filedialog.askopenfilename(initialdir = "/",title = "Select strain device force data shet",filetypes = (("txt files","*.txt"),("all files","*.*")))
    
    def get_current_force(self):
        np.loadtxt(self.force_path_data, skiprows=1, usecols=1)
    
    def measure(self):
        
        if(self.force_data_path == ""):
            self.get_force_path()
        F = self.get_current_force()
        self.data_manager.reset_table([], "UI_measurement_NO_{}_at_{}N".format(self.counter, F))
        self.counter = self.counter +1
        V_arr = np.linspace(self.V_min, self.V_max, n_steps)
        for i in range(len(V_arr)):
            keithley.ramp_to_voltage(V_arr[i],1,self.t_step)
            time.sleep(0.1)
            keithley.reset_buffer()
            
            
            

measure_bot = empty_measurement_bot()
interface = interface_01.condition_checker()
condition_bot = click_condition_bot(interface)
lockin = SR830("GPIB::8")#v_lockin(y,z)
lockin.auto_offset("R")
keithley = Keithley2400("GPIB::24")#v_keithley(lockin)
keithley.enable_source()
keithley.apply_voltage(200)
data_manager = data_manager()
name = "test_real_devices_01"

P = .2
I = .6
calb = 2.3*10**(-6)
V_min = -7.
V_max = 120.0
n_step_per_V = 20.
t_step = 0.05
amp = 10**(6)
sign = -1.
#delta_min = 10**(-6)
t_wait = 10.


s_dev = strain_device(measure_bot,condition_bot,keithley,lockin,P,I,calb,V_min,V_max,n_step_per_V,t_step,amp,sign, t_wait, data_manager, name)
while(not condition_bot.exit_measurement()):
    print(interface.get_current_force())
    s_dev.apply_force(interface.get_current_force())

interface.close_window()
s_dev.apply_v_to_piezo(0.)
print("done")
