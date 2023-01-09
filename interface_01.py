#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  1 10:46:21 2019

@author: esingh
"""
import numpy as np
import tkinter as tk
import time
import threading


class data_manager(object):
    def __init__(self, P, I):
        self.forces = []
        self.current_force = 0.
        self.P = P
        self.I = I
        self.exit_measurement = False
        self.exit_condition = False
        
class condition_checker(object):
    def __init__(self):
        threading.Thread(target=self.__run_interface).start()
        self.forces = []
        self.current_force = 0.
        self.exit_measurement = False
    
    def __run_interface(self):
        self.exit_condition = False
        self.master = tk.Tk()
        self.f_label = tk.Label(self.master, text="F applied: -- N")
        self.f_label.grid(row=0,column=0)
        self.next_button = tk.Button(self.master, text="next force", command=self.__next_force,bg="green",relief="raised")
        self.next_button.grid(row=0,column=1)
        self.f_input_label = tk.Label(self.master, text="new force in [N]")
        self.f_input_label.grid(row=1,column=0)
        self.f_input = tk.Entry(self.master)
        self.f_input.grid(row=2,column=0)
        self.submit_force_button = tk.Button(self.master, text="add force", command=self.__add_force,bg="red",relief="raised")
        self.submit_force_button.grid(row=3,column=0)
        self.force_array = tk.Label(self.master, text="next forces: {}".format(self.forces))
        self.force_array.grid(row=4,column=0)
        self.exit_button = tk.Button(self.master, text="EXIT", command=self.__exit,bg="red",relief="raised")
        self.exit_button.grid(row=5,column=0)
        self.remove_button = tk.Button(self.master, text="remove force", command=self.__remove_force,bg="green",relief="raised")
        self.remove_button.grid(row=3,column=1)
        self.master.mainloop()

    def __remove_force(self):
        if(len(self.forces)!=0):
            del self.forces[-1]
            self.force_array["text"] = text="next forces: {}".format(self.forces)

    def __add_force(self):
        if(self.f_input.get() != ""):
            self.forces.append(float(self.f_input.get()))
            self.force_array["text"] = text="next forces: {}".format(self.forces)
            print(self.forces)
            while(self.f_input.get() != ""):
                self.f_input.delete(0)
        

    def __next_force(self):
        if(len(self.forces)!=0):
            self.exit_condition = True
            print("exit")
            self.next_button["relief"] = "sunken"
            self.next_button["bg"] = "darkred"
            self.current_force = self.forces[0]
            self.f_label["text"] = "F applied: {} N".format(self.current_force)
            del self.forces[0]
            self.force_array["text"] = text="next forces: {}".format(self.forces)
    
    def reset_condition(self):
        self.exit_condition = False
        self.next_button["relief"] = "raised"
        self.next_button["bg"] = "green"
    
    def check_condition(self):
        return self.exit_condition

    def __exit(self):
        self.exit_measurement = True
        self.exit_condition = True
    
    def close_window(self):
        self.master.quit()

    def check_exit_measurement(self):
        return(self.exit_measurement)

    def get_current_force(self):
        return(self.current_force)
