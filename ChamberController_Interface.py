# Environmental Chamber GUI
# Author: Reilly Pickard (contact: reilly.pickard@dal.ca)
# Last Update: April 5th, 2023
# Description: This GUI was created to control the
# environmental testing chamber located in D115A at
# Dalhousie University, Halifax, NS
# This was done to meet the requirements of the Team 3's 2023
# Mechanical Engineering Capstone Project.
# It has two main parts: A setpoint input table that accepts multiple
# temperature, humidity, and time-scale values. It also plots the live results
# for air and material temperature, along with the humidity readings.

### Imports
import serial
import time
import tkinter as tk
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pandas as pd
import csv
import smtplib
import ssl
import serial.tools.list_ports
import datetime
### Initialize e-mail messages
port = 587  
smtp_server = "smtp-mail.outlook.com"
sender = "chamberalerts@outlook.com"
recipient = "reilly.pickard@dal.ca"  ### Change this to user email
sender_password = "Pass2208*" ## Please do not share
message1 = """
Subject: CHAMBER ALERT.
The chamber has exceeded the maximum temperature of 350F. Please go check to
ensure the chamber has powered off. It is located in D115A. Turn off by removing
the USB cable or by pulling the lever down on the power source. """
message2 = """
Subject: CHAMBER ALERT.
The chamber has gone below the minimum temperature of -100F. Please go check to
ensure the chamber has powered off. It is located in D115A. Turn off by removing
the USB cable or by pulling the lever down on the power source. """
SSL_context = ssl.create_default_context()


#### Get a list of available ports
available_ports = list(serial.tools.list_ports.comports())
##### Intialize Serial Communication
if not available_ports:
    print("No ports available. Please connect your device.")
else:
    # Iterate through available ports and look for Arduino
    for port in available_ports:
        
        if "USB-SERIAL CH340" in port.description:
            # If Arduino is found, connect to it
            ser = serial.Serial(port.device, 115200)
            print("Connected to", port.description, "on", port.device)
            break
    else:
        print("Could not find an Arduino.")

#### Define a function to send data to Arduino
def send_to_arduino():
    temperatures = [temperature_entries[i].get() for i in range(len(temperature_entries))]
    humidities = [humidity_entries[i].get() for i in range(len(humidity_entries))]
    hold_times = [hold_time_entries[i].get() for i in range(len(hold_time_entries))]
    temperatures = [float(temperature) for temperature in temperatures if temperature]
    humidities = [float(humidity) for humidity in humidities if humidity]
    hold_times = [float(hold_time) for hold_time in hold_times if hold_time]
    data = []
    for i in range(len(temperatures)): ## send appended inputs with delimeter ','
        data.append(str(temperatures[i]) + ',' + str(humidities[i]) + ',' + str(hold_times[i]))
    ser.write('\n'.join(data).encode())

####Create the GUI
root = tk.Tk()
root.title("Chamber Controller")
root.geometry('475x375')
root.configure(bg='black')

##table headers
header_label = tk.Label(root, text="Chamber Controller", font=("Arial", 18, "bold"), bg="black", fg="white", pady=20, padx = 30)
header_label.grid(row=0, column=0, columnspan=3, sticky="nsew", padx  = 20)

temperature_label = tk.Label(root, text="Temperatures (°F)", bg = "black", fg = "white", font = ("Arial", 12, "bold"))
temperature_label.grid(row=1, column=0, padx=(12, 5))

humidity_label = tk.Label(root, text="Humidity (%)", bg = "black", fg = "white", font = ("Arial", 12, "bold"))
humidity_label.grid(row=1, column=1, padx = (5,5))

hold_time_label = tk.Label(root, text="Hold Times (min)", bg = "black", fg = "white", font = ("Arial", 12, "bold"))
hold_time_label.grid(row=1, column=2, padx=(5, 12))

##initialize storage arrays
temperature_entries = []
humidity_entries = []
hold_time_entries = []

### Create a Table and append entries
for i in range(10):## change from 10 to however amount of entries you want
    temperature_entry = tk.Entry(root, font = ("Arial", 10, "bold"))
    temperature_entry.grid(row=i+2, column=0, padx=(12, 5))
    temperature_entries.append(temperature_entry)

    humidity_entry = tk.Entry(root, font = ("Arial", 10, "bold"))
    humidity_entry.grid(row=i+2, column=1, padx = (5,5))
    humidity_entries.append(humidity_entry)

    hold_time_entry = tk.Entry(root, font = ("Arial", 10, "bold"))
    hold_time_entry.grid(row=i+2, column=2, padx=(5, 12))
    hold_time_entries.append(hold_time_entry)

## Send button and message about user manual
send_button = tk.Button(root, text="Send", command=send_to_arduino, bg = "white", fg = "black", font = ("Arial", 12, "bold"))
send_button.grid(row=12, column=0, columnspan=3, pady = (10,10))

header_label2 = tk.Label(root, text="Refer to User Manual for Instructions", font=("Arial", 12, "bold", "italic"), bg="black", fg="white")
header_label2.grid(row=13, column=0, columnspan=3, sticky="nsew")


##### Live Plot #######
fig = plt.figure()

# Add temperature subplot
ax_temp = fig.add_subplot(2,1,1)
ax_temp.set_xlim([20, 40])
ax_temp.set_ylim([0, 400])

#ax_temp.set_title('Temperature Reading')
ax_temp.grid()

ys_temp = [] ## Init arrays
ys_tempm = []
data_temp = 0

#Add humidity subplot
ax_humidity = fig.add_subplot(2,1,2)
ax_humidity.set_xlim([20, 40])
ax_humidity.set_ylim([0, 100])
ax_humidity.set(xlabel='Time (S)', ylabel='Relative Humidity (%)')
ax_humidity.set_title('Humidity Reading')
ax_humidity.grid()
ys_humidity = []
data_humidity = 0

### Animate the plot
def animate(i):
    global data_temp, data_humidity
    data = ser.readline().decode("ascii") ## Receive the data
    data = str(data)
    data = data.split(',')  # split the temperature and humidity values using a comma separator
    data_temp = round(float(data[0]),2)
   # data_tempm = round(float(data[1]),2)
    data_humidity = (float(data[2]))
    ys_temp.append(data_temp)
    #ys_tempm.append(data_tempm)                        
    ys_humidity.append(data_humidity)
    df = pd.DataFrame({'Air Temp. (F)': ys_temp, 'Humidity (%)': ys_humidity})
    print(f"Temperature: {data_temp} F,  Rel. Humidity: {data_humidity}%")
    ## temperature plot
    ax_temp.clear()
    ax_temp.set_xlim([len(ys_temp)-60, len(ys_temp)]) ## this limit is set for showing 60 data points in a graph
    ax_temp.plot([i for i in range(len(ys_temp))], ys_temp, 'r')  ## plots the temperature graph
    #ax_temp.plot([i for i in range(len(ys_tempm))], ys_tempm, 'b', label = "Material")
    ax_temp.set_title('Chamber Temperature Readings')
    ax_temp.grid()
    #ax_temp.legend()
    ax_temp.set(xlabel='Time (S)', ylabel='Temperature (F)')
    now = datetime.datetime.now()
    date_string = now.strftime("%Y-%m-%d")
    filename = f'ChamberData{date_string}.csv' ## append the current date to the file name
    df.to_csv(filename)
    ## Humidity plot
    ax_humidity.clear()
    ax_humidity.set_xlim([len(ys_humidity)-60, len(ys_humidity)]) ## this limit is set for showing 60 data points in a graph
    ax_humidity.plot([i for i in range(len(ys_humidity))], ys_humidity, 'black')  ## plots the humidity graph
    ax_humidity.set_title('Humidity Reading')
    ax_humidity.set(xlabel='Time (S)', ylabel='Humidity (%)')
    ax_humidity.grid()

    plt.subplots_adjust(hspace=0.5)  # Add space between subplots

    ### Send email message
    if(data_temp> 400):
            with smtplib.SMTP(smtp_server, port) as server:
                 server.starttls(context=SSL_context)
                 server.login(sender, sender_password)
                 server.sendmail(sender, recipient,  message1)
    if(data_temp< -150):
            with smtplib.SMTP(smtp_server, port) as server:
                 server.starttls(context=SSL_context)
                 server.login(sender, sender_password)
                 server.sendmail(sender, recipient,  message2)    
    
anim = animation.FuncAnimation(fig, animate, interval=10)


plt.show()

root.mainloop()
