# -*- coding: utf-8 -*-
"""
Created on Sat Mar 20 17:09:54 2021

@author: ryanz
"""

from threading import Thread
import tkinter as tk
import re
from tkinter import ttk
from tkinter import messagebox
import datetime
from datetime import timedelta
import pandas as pd
nasdaq_url = "http://ftp.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt"
other_url = "http://ftp.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt"

LARGE_FONT= ("Verdana", 20)
NORMAL_FONT= ("Verdana", 12)
SMALLER_FONT = ("Verdana", 9)

#running_schedules = []

def load_data():
    nasdaq_df = pd.read_csv(nasdaq_url, delimiter = "|")
    other_df = pd.read_csv(other_url,delimiter= "|")
    return nasdaq_df, other_df

def isInt(num):
    try:
        return int(num), True
    except:
        return None, False
def isFloat(num):
    try:
        return float(num), True
    except:
        return None, False
    
nasdaq, other = load_data()

class Window(tk.Tk):
    container = None
    # nasdaq = pd.DataFrame()
    # other = pd.DataFrame()
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        
        tk.Tk.wm_title(self,"Trade Scheduler")
        scr_width = tk.Tk.winfo_screenwidth(self)
        scr_height = tk.Tk.winfo_screenheight(self)
        x_cordinate = int((scr_width/2) - (600/2))
        y_cordinate = int((scr_height/2) - (600/2))
        
        tk.Tk.geometry(self,"{}x{}+{}+{}".format(600, 600, x_cordinate, y_cordinate))
        tk.Tk.resizable(self, False, False)
        
        self.container = tk.Frame(self, width=600, height=600, relief='raised', borderwidth=0)
        self.container.pack(side="top", fill="both", expand = True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        
        self.frames = {}
        '''
        for F in start, enterParam:
            frame = F(container, self)
    
            self.frames[F] = frame
    
            frame.grid(row=0, column=0, sticky="nsew")
        '''
        self.show_frame1(start)

    def show_frame1(self,cont, scheduleInstance = None, running_schedules = None):
        frame = cont(self.container, self, scheduleInstance, running_schedules)
        self.show_frame(frame)
        
    def show_frame2(self,cont, ticker):
        frame = cont(self.container, self, ticker)
        self.show_frame(frame)
        
    def show_frame3(self,cont, newSchedule):
        frame = cont(self.container, self, newSchedule)
        self.show_frame(frame)
        
    def show_frame(self,frame):
            frame.grid(row = 0, column = 0, sticky = 'nsew')
            frame.tkraise()
            
class start(tk.Frame):
     running_instances = []
     finished_instances = []
     
     def __init__(self, parent, controller, instance, running_schedules):
        tk.Frame.__init__(self,parent)
        if running_schedules is not None:
            start.running_instances = running_schedules
        if instance !=None:
            start.running_instances.append(instance)
            
        label = ttk.Label(self, text="Trade Scheduler", font=LARGE_FONT)
        label.pack()
        label.place(relx=.5, rely = .3, anchor='center')
     
        entry1 = ttk.Entry(self) 
        entry1.pack(pady = 25)
        entry1.place(relx = .5, rely = 0.4, anchor = 'center')
        entry1.focus_force()
        
        button1 = ttk.Button(self, text="Enter Ticker",
                            command=lambda: enter_ticker())
        button1.pack()
        button1.place(relx = .5, rely = .45, anchor = 'center')
        
        self.timers = {}
        
        self.count= -1
        for i in start.running_instances:
            self.count+=1
            l = ttk.Label(self,text = i['ticker'], font = NORMAL_FONT)
            l.pack()
            l.place(relx = .075, rely = .2+(self.count*.15), anchor = 'center')
            
            l2 = ttk.Label(self, text = str(i['time']), font = SMALLER_FONT)
            l2.pack()
            l2.place(relx = .075, rely = .24+(self.count*.15), anchor = 'center')
            cButton = ttk.Button(self, text = "Cancel", command = lambda i = i:cancel_trade(i))
            cButton.pack()
            cButton.place(relx = .075, rely = .28+self.count*.15, anchor = 'center')
            
            self.timers[str(self.count)]= int(i['time'].seconds)
            t = Thread(target = self.countdown(i, l2, cButton, self.timers[str(self.count)]))
            t.start()
        
        count = -1
        for i in start.finished_instances:
            count+=1
            l = ttk.Label(self,text = i['ticker'], font = NORMAL_FONT)
            l.pack()
            l.place(relx = .875, rely = .2+(count*.15), anchor = 'center')
            
            l2 = ttk.Label(self, text ="Executed", font = SMALLER_FONT)
            l2.pack()
            l2.place(relx = .875, rely = .24+(count*.15), anchor = 'center')
         
        
            
        def enter_ticker():
            if len(entry1.get().strip())>0:
                ticker = entry1.get().strip()
                entry1.delete(0, 'end')
                if not nasdaq['Symbol'].str.contains(ticker.upper()).any() and not other['NASDAQ Symbol'].str.contains(ticker.upper()).any():
                    error_box(ticker.upper())
                    return
                print("'{}' ticker entered".format(ticker.upper()))
                controller.show_frame2(enterParam, ticker.upper())
            else:
                empty_error()
                
        def error_box(name):
            messagebox.showinfo("Error", "{} is not a NASDAQ or NYSE listed ticker.".format(name))
            entry1.focus_force()
        
        def empty_error():
            messagebox.showinfo("Error", "Please enter a ticker.")
            entry1.focus_force()
        def cancel_trade(instance):
             try:
                 start.running_instances.remove(instance)
                 controller.show_frame1(start)
             except:
                 return
             
     def countdown(self,instance, label, button,remaining = None):
        if remaining is not None:
            self.timers[str(self.count)]= remaining
        if self.timers[str(self.count)] > 0:
            label.configure(text=str(timedelta(seconds=self.timers[str(self.count)])))
            self.timers[str(self.count)] -=1
            instance['time'] = timedelta(seconds=self.timers[str(self.count)])
            self.after(1000, self.countdown(instance, label, button))
            
                

class enterParam(tk.Frame):
     def __init__(self, parent, controller, ticker):
        tk.Frame.__init__(self,parent)
        self.tickerName = ticker
        #tk.Frame.pack_propagate(self,False)
        label = ttk.Label(self, text="Schedule Trade for:", font=LARGE_FONT)
        label.pack()
        label.place(relx = .45, rely = .15, anchor = 'center')
        
        tickerLabel = tk.Label(self, fg = 'red', text = self.tickerName, font = LARGE_FONT)
        tickerLabel.pack()
        tickerLabel.place(relx = .68, rely = .15, anchor = 'w')
     
        label1 = ttk.Label(self, text = "When:", font = NORMAL_FONT)
        label1.pack(pady=5)
        label1.place(relx = .35, rely = .35, anchor = "center")
        
        label2 = ttk.Label(self, text = "Target Price:", font = NORMAL_FONT)
        label2.pack(pady=5)
        label2.place(relx = .35, rely = .5, anchor = "center")
        
        label3 = ttk.Label(self, text = "Max Price:", font = NORMAL_FONT)
        label3.pack(pady=5)
        label3.place(relx = .65, rely = .5, anchor = "center")
        
        
        label5 = ttk.Label(self, text="# Shares: ", font = NORMAL_FONT)
        label5.pack(pady=5)
        label5.place(relx = .65, rely = .35, anchor="center")
        
        
        entry1 = ttk.Entry(self) 
        entry1.pack(pady = 25)
        entry1.place(relx = .35, rely = 0.4, anchor = 'center')
        entry1.focus_force()
        
        entry4 = ttk.Entry(self)
        entry4.pack(pady=35)
        entry4.place(relx = .65, rely = .4, anchor = 'center')
        
        entry2 = ttk.Entry(self) 
        entry2.pack(pady = 25)
        entry2.place(relx = .35, rely = 0.55, anchor = 'center')
        
        entry3 = ttk.Entry(self) 
        entry3.pack(pady = 25)
        entry3.place(relx = .65, rely = 0.55, anchor = 'center')
        
        button1 = ttk.Button(self, text="Done",
                            command=lambda: execute_trade())
        button1.pack()
        button1.place(relx = .5, rely = .7, anchor = 'center')
        
        button2 = ttk.Button(self, text="Back",
                            command=lambda: controller.show_frame1(start))
        button2.pack()
        button2.place(relx = .5, rely = .65, anchor = 'center')
        
        infoButton = ttk.Button(self, text="Help", command=lambda: help_dialog())
        infoButton.pack()
        infoButton.place(relx = .5, rely = .275, anchor = 'center')
        
        count= -1
        for i in start.running_instances:
            count+=1
            l = ttk.Label(self,text = i['ticker'], font = NORMAL_FONT)
            l.pack()
            l.place(relx = .075, rely = .2+(count*.15), anchor = 'center')
            
            l2 = ttk.Label(self, text = str(i['time']), font = SMALLER_FONT)
            l2.pack()
            l2.place(relx = .075, rely = .24+(count*.15), anchor = 'center')
            cButton = ttk.Button(self, text = "Cancel", command = lambda i = i:cancel_trade(i))
            cButton.pack()
            cButton.place(relx = .075, rely = .28+count*.15, anchor = 'center')
        
        count = -1
        for i in start.finished_instances:
            count+=1
            l = ttk.Label(self,text = i['ticker'], font = NORMAL_FONT)
            l.pack()
            l.place(relx = .875, rely = .2+(count*.15), anchor = 'center')
            
            l2 = ttk.Label(self, text ="Executed", font = SMALLER_FONT)
            l2.pack()
            l2.place(relx = .875, rely = .24+(count*.15), anchor = 'center')
        
        

        def help_dialog():
            messagebox.showinfo("Help", "When: Time from now to execute trade (s: seconds, m: minutes, h: hours)\n\nMax Price: Maximum price of stock you are willing to buy\n\nTarget Price: Buy immediately if stock hits this price\n\n# Shares: Number of shares to buy")
            entry1.focus_force()
            
        def cancel_trade(instance):
             try:
                 start.running_instances.remove(instance)
                 controller.show_frame2(enterParam, ticker)
             except:
                 return
            
        def execute_trade():
            max_price = "n/a"
            target= "n/a"
            
            try:
                if "m" in entry1.get():
                    time = timedelta(minutes=int(entry1.get().replace("m","")))
                    #add check if the schedule will be outside market hours
                elif "h" in entry1.get():
                    time = timedelta(hours = int(entry1.get().replace("h","")))
                    #add check if the schedule will be outside market hours
                else:
                    time = timedelta(seconds = int(entry1.get().replace("s","")))
                    
                    #add check if the schedule will be outside market hours
                timeEnter = True
            except:
                timeEnter = False
                if isInt(entry4.get())[1]:
                    messagebox.showinfo("Error", "Enter a scheduled time.")
                    entry1.focus_force()
                    return
            
            #target price
            if len("".join(filter(str.isdigit, entry3.get())))>0:
                max_price = round(float(re.sub(r"[^0-9.]", "", entry3.get())),2)
            #max price
            if len("".join(filter(str.isdigit, entry2.get())))>0:
                target = round(float(re.sub(r"[^0-9.]", "", entry2.get())),2)
                
            if isFloat(max_price)[1] and isFloat(target)[1] and max_price<target:
                messagebox.showinfo("Error", "The target price cannot exceed the maximum price.")
                entry1.focus_force()
                return
            
            try:
                shares = int(entry4.get())
                if shares ==0:
                    if not timeEnter:
                        messagebox.showinfo("Error", "Enter a scheduled time and the number of shares.")
                        entry1.focus_force()
                        return
                    else:
                        messagebox.showinfo("Error", "Enter the number of desired shares.")
                        entry4.focus_force()
                        return
            except:
                if not timeEnter:
                    messagebox.showinfo("Error", "Enter a scheduled time and the number of shares.")
                    entry1.focus_force()
                    return
                else:
                    messagebox.showinfo("Error", "Enter the number of desired shares.")
                    entry4.focus_force()
                    return
        
            confirm(target, max_price, shares, time)
            
            
            
        def confirm(target, max_price, shares, time):
            response=messagebox.askyesno(title="Confirm Trade", 
                                  message="Are you sure you want to schedule this trade for {} shares of {} in {}?".format(shares, self.tickerName, time))
            if response:
                entry3.delete(0,'end')
                entry2.delete(0,'end')
                entry1.delete(0,'end')
                entry4.delete(0, 'end')
                print("'{}' trade scheduled to trade in {}.\n# Shares: {} \nTarget: {}\nMaximum: {}".format(self.tickerName, time, shares,target, max_price))
                #finish.setInfo(time.seconds, shares, max_price, target, self.tickerName)
                schedule = {}
                schedule['ticker'] = self.tickerName
                schedule['time'] = time
                schedule['shares'] = shares
                schedule['max_price'] = max_price
                schedule['target'] = target
                controller.show_frame3(finish, schedule)
              
class finish(tk.Frame):
    
    def __init__(self, parent, controller, schedule):
        tk.Frame.__init__(self,parent)
        self.scheduleInstance = schedule
        
        self.label = ttk.Label(self, text=self.scheduleInstance['ticker']+" will execute in: "+str(self.scheduleInstance['time']), font=LARGE_FONT)
        self.label.pack()
        self.label.place(relx = .5, rely = .3, anchor = 'center')
        
        self.sharesLabel = ttk.Label(self, text = "# Shares: "+str(self.scheduleInstance['shares']), font = NORMAL_FONT)
        self.sharesLabel.pack()
        self.sharesLabel.place(relx = .5, rely=.375, anchor = 'center')
        
        max_text = "${:.2f}".format(self.scheduleInstance['max_price']) if isFloat(self.scheduleInstance['max_price'])[1] else self.scheduleInstance['max_price']
        self.maxLabel = ttk.Label(self, text = "Max Buy Price: "+max_text, font = NORMAL_FONT)
        self.maxLabel.pack()
        self.maxLabel.place(relx = .5, rely = .475, anchor = 'center')
        
        target_text = "${:.2f}".format(self.scheduleInstance['target']) if isFloat(self.scheduleInstance['target'])[1] else self.scheduleInstance['target']
        self.targetLabel = ttk.Label(self, text = "Target Buy Price: "+target_text, font = NORMAL_FONT)
        self.targetLabel.pack()
        self.targetLabel.place(relx = .5, rely = .425, anchor = 'center')
        
        self.button1 = ttk.Button(self,text="Cancel Trade",
                            command=lambda: confirm())
        self.button1.pack()
        self.button1.place(relx = .5, rely = .550, anchor = 'center')
        
        self.button2 = ttk.Button(self, text="New Trade",
                            command=lambda: new_trade(self))
        self.button2.pack()
        self.button2.place(relx = .5, rely = .625, anchor = 'center')
        
        
        count= -1
        for i in start.running_instances:
            count+=1
            l = ttk.Label(self,text = i['ticker'], font = NORMAL_FONT)
            l.pack()
            l.place(relx = .075, rely = .2+(count*.15), anchor = 'center')
            
            l2 = ttk.Label(self, text = str(i['time']), font = SMALLER_FONT)
            l2.pack()
            l2.place(relx = .075, rely = .24+(count*.15), anchor = 'center')
            cButton = ttk.Button(self, text = "Cancel", command = lambda i = i:cancel_trade2(i))
            cButton.pack()
            cButton.place(relx = .075, rely = .28+count*.15, anchor = 'center')
        
        count = -1
        for i in start.finished_instances:
            count+=1
            l = ttk.Label(self,text = i['ticker'], font = NORMAL_FONT)
            l.pack()
            l.place(relx = .875, rely = .2+(count*.15), anchor = 'center')
            
            l2 = ttk.Label(self, text ="Executed", font = SMALLER_FONT)
            l2.pack()
            l2.place(relx = .875, rely = .24+(count*.15), anchor = 'center')
        
        self.remaining = 0
        self.countdown(self.scheduleInstance['time'].seconds)
        
    
        def confirm():
            resp = messagebox.askyesno(title="Confirm Cancellation", 
                                  message="Are you sure you want to cancel this scheduled trade?")
            if resp:
                cancel_trade(self)
                
        def cancel_trade(self):
            self.remaining = 0
            #something that will actually cancel the scheduled trade
            controller.show_frame1(start)
        
        def cancel_trade2(instance):
            start.running_instances.remove(instance)
            controller.show_frame3(finish, self.scheduleInstance)
        def new_trade(self):
            if self.remaining>0:
                #print(self.scheduleInstance)
                controller.show_frame1(start, self.scheduleInstance)
            else:
                controller.show_frame1(start)
            
            
    def countdown(self, remaining = None):
        if remaining is not None:
            self.remaining = remaining

        if self.remaining <= 0:
            self.label.configure(text=self.scheduleInstance['ticker']+" trade executed.")
            self.button1.destroy()
            self.targetLabel.configure(text = "Purchased at: $"+str(5))
            self.maxLabel.destroy()
            self.button2.place(relx = .5, rely = .525, anchor = 'center')
            
            start.finished_instances.append(self.scheduleInstance)
            start.running_instances.remove(self.scheduleInstance)
            
        else:
            self.label.configure(text=self.scheduleInstance['ticker']+" Trade Scheduled: "+str(timedelta(seconds=self.remaining)))
            self.remaining = self.remaining - 1
            self.scheduleInstance['time'] = timedelta(seconds=self.remaining)
            self.after(1000, self.countdown)
            
    
g = Window()
g.mainloop()