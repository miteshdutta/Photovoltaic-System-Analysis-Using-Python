import numpy
from tkinter import *
from datetime import date
from datetime import datetime
from pvlib import pvsystem
import pandas as pd
import matplotlib.pyplot as plt
import os
from pvlib import solarposition, tracking
from pvlib import location
from pvlib import irradiance



today = date.today()
date = today.strftime("%B %d, %Y")
now = datetime.now()
time = now.strftime("%H:%M")

root1 = Tk()
root1.title('Solar Tool Box')
root1.geometry('1300x750')
logo = PhotoImage(file="icon.gif")
root1.iconphoto(False,logo)
root1.config(bg='black')

path='Specs.pdf'
PVCurrent=DoubleVar()
OutputCurrent=DoubleVar()
Temprature=DoubleVar()
MaxCurrent=DoubleVar()
MaxVoltage=DoubleVar()
lat_var=StringVar()
lon_var=StringVar()
strdate=StringVar()
stpdate=StringVar()

def pdf():
    os.system(path)

def end():
    root1.destroy()
    exit()

def mainpage():
    root1.destroy()
    import M1

def Calculate():
    I_pv=float(PVCurrent.get())
    I_o=float(OutputCurrent.get())
    Temp=float(Temprature.get())
    I_m=float(MaxCurrent.get())
    V_m=float(MaxVoltage.get())
    R_s=float('0.1')
    V_t =float(Temp*1.38*10**(-23))/(1.6*10**(-19))
    VarX = numpy.log((I_pv+I_o)/I_o)
    V_oc=float(2*V_t*VarX)
    I_sc=float(I_pv - I_o*((2.718**((I_pv*R_s)/(2*V_t)))-1))
    F=str((I_m*V_m)/(I_sc*V_oc))
    V_oc1=str(V_oc)
    I_sc1=str(I_sc)
    P_m=str(I_m*V_m)
    E=str(((I_m*V_m)/1000)*100) #Considering input power ""P_in"" as 1000 W/m^2
    output=Label(root1,text="Efficiency = "+E+' %',font=('Arial',12),fg='white',bg='black').place(x=60,y=690)
    output=Label(root1,text="Short Circuit Current = "+I_sc1+" A",font=('Arial',12),fg='white',bg='black').place(x=60,y=570)
    output2=Label(root1,text="Open Circuit voltage = "+V_oc1+' V',font=('Arial',12),fg='white',bg='black').place(x=60,y=600)
    output3=Label(root1,text="Fill Factor = "+F,font=('Arial',12),fg='white',bg='black').place(x=60,y=630)
    output=Label(root1,text="Maximum Power Point = "+P_m+' Watts',font=('Arial',12),fg='white',bg='black').place(x=60,y=660)

def run():
    # Module parameters for the Vikram Solar ELDORA NEO 72 SILVER SERIES:
    parameters = {
    'Name': 'Vikram Solar ELDORA NEO 72 SILVER SERIES',
    'Date': '10/5/2009',
    'T_NOCT': 45,
    'A_c': 2.34,
    'N_s': 72,
    'I_sc_ref': 9.22,
    'V_oc_ref': 46.5,
    'I_mp_ref': 8.66,
    'V_mp_ref': 38.71,
    'alpha_sc': 0.052,
    'beta_oc': -0.310,
    'a_ref': 2.6373,
    'I_L_ref': 5.114,
    'I_o_ref': 8.196e-10,
    'R_s': 1.065,
    'R_sh_ref': 381.68,
    'Adjust': 8.7,
    'gamma_r': -0.476,
    'PTC': 200.1,
    'Technology': 'Mono-c-Si',
    }

    cases = [
    (1000, 55),
    (800, 55),
    (600, 55),
    (400, 25),
    (400, 40),
    (400, 55)
    ]

    conditions = pd.DataFrame(cases, columns=['Eff Iradiance', 'Tcell'])

    # De Soto
    IL, I0, Rs, Rsh, nNsVth = pvsystem.calcparams_desoto(
        conditions['Eff Iradiance'],
        conditions['Tcell'],
        alpha_sc=parameters['alpha_sc'],
        a_ref=parameters['a_ref'],
        I_L_ref=parameters['I_L_ref'],
        I_o_ref=parameters['I_o_ref'],
        R_sh_ref=parameters['R_sh_ref'],
        R_s=parameters['R_s'],
        EgRef=1.121,                    # Band Gap
        dEgdT=-0.0002677
    )

    # Use the output parameters from above and solve for IV curves:
    curve_info = pvsystem.singlediode(
        photocurrent=IL,
        saturation_current=I0,
        resistance_series=Rs,
        resistance_shunt=Rsh,
        nNsVth=nNsVth,
        ivcurve_pnts=100,
        method='lambertw'
    )

    # For plotting the curves:
    plt.figure()
    for i, case in conditions.iterrows():
        label = (
            "$G_{eff}$ " + f"{case['Eff Iradiance']} $W/m^2$\n"
            "$T_{cell}$ " + f"{case['Tcell']} $C$"
        )
        plt.plot(curve_info['v'][i], curve_info['i'][i], label=label)
        v_mp = curve_info['v_mp'][i]
        i_mp = curve_info['i_mp'][i]
        # To mark the MPP we use:
        plt.plot([v_mp], [i_mp], ls='', marker='o', c='k')

    plt.legend(loc=(1.0, 0))
    plt.xlabel('Module voltage [V]')
    plt.ylabel('Module current [A]')
    plt.title(parameters['Name'])
    plt.show()
    plt.gcf().set_tight_layout(True)

    print(pd.DataFrame({
        'i_sc': curve_info['i_sc'],
        'v_oc': curve_info['v_oc'],
        'i_mp': curve_info['i_mp'],
        'v_mp': curve_info['v_mp'],
        'p_mp': curve_info['p_mp'],
    }))

def submit():
    latitude=float(lat_var.get())
    longitude=float(lon_var.get())
    Str_date=strdate.get()
    Stop_date=stpdate.get()
    tz = 'Asia/Kolkata'
    lat, lon = latitude, longitude

    times = pd.date_range(Str_date, Stop_date, closed='left', freq='5min',
                        tz=tz)
    solpos = solarposition.get_solarposition(times, lat, lon)

    truetracking_angles = tracking.singleaxis(
        apparent_zenith=solpos['apparent_zenith'],
        apparent_azimuth=solpos['azimuth'],
        axis_tilt=0,
        axis_azimuth=180,
        max_angle=90,
        backtrack=False,  # for true-tracking
        gcr=0.5)  

    truetracking_position = truetracking_angles['tracker_theta'].fillna(0)
    truetracking_position.plot(title='Truetracking Curve')
    plt.xlabel('Time')
    plt.ylabel('Angle(Degree)')
    plt.show()
    # Backtracking
    fig, ax = plt.subplots()

    for gcr in [0.2, 0.4, 0.6]:
        backtracking_angles = tracking.singleaxis(
            apparent_zenith=solpos['apparent_zenith'],
            apparent_azimuth=solpos['azimuth'],
            axis_tilt=0,
            axis_azimuth=180,
            max_angle=90,
            backtrack=True,
            gcr=gcr)

        backtracking_position = backtracking_angles['tracker_theta'].fillna(0)
        backtracking_position.plot(title='Backtracking Curve',
                                label=f'GCR:{gcr:0.01f}',
                                ax=ax)

    plt.legend()
    plt.xlabel('Time')
    plt.ylabel('Angle(Degree)')
    plt.show()

def submit1():

    latitude=float(lat_var.get())
    longitude=float(lon_var.get())

    tz = 'Asia/Kolkata'
    lat, lon = latitude, longitude
    site = location.Location(lat, lon, tz=tz)

    def get_irradiance(site_location, date, tilt, surface_azimuth):
        times = pd.date_range(date, freq='10min', periods=6*24,
                            tz=site_location.tz)
        clearsky = site_location.get_clearsky(times)
        # Azimuth and Zenith
        solar_position = site_location.get_solarposition(times=times)
        # GHI to POA
        POA_irradiance = irradiance.get_total_irradiance(
            surface_tilt=tilt,
            surface_azimuth=surface_azimuth,
            dni=clearsky['dni'],
            ghi=clearsky['ghi'],
            dhi=clearsky['dhi'],
            solar_zenith=solar_position['apparent_zenith'],
            solar_azimuth=solar_position['azimuth'])
        return pd.DataFrame({'GHI': clearsky['ghi'],
                            'POA': POA_irradiance['poa_global']})

    summer_irradiance = get_irradiance(site, '06-20-2020', 23, 180)
    winter_irradiance = get_irradiance(site, '12-21-2020', 23, 180)

    summer_irradiance.index = summer_irradiance.index.strftime("%H:%M")
    winter_irradiance.index = winter_irradiance.index.strftime("%H:%M")

    fig, (ax1, ax2) = plt.subplots(1, 2, sharey=True)
    summer_irradiance['GHI'].plot(ax=ax1, label='GHI')
    summer_irradiance['POA'].plot(ax=ax1, label='POA')
    winter_irradiance['GHI'].plot(ax=ax2, label='GHI')
    winter_irradiance['POA'].plot(ax=ax2, label='POA')
    ax1.set_xlabel('Time of day (Winter)')
    ax2.set_xlabel('Time of day (Summer)')
    ax1.set_ylabel('Irradiance ($W/m^2$)')
    ax1.legend()
    ax2.legend()
    plt.show()
    
Label1=Label(root1,text="\nUser Input:",font=('Arial Bold',18),fg='blue',bg='Black').place(x=60,y=30)
Label_Heading1=Label(root1,text="Enter the following Values =>",font=('Arial',12),fg='springgreen',bg='black').place(x=60,y=110)
Label2=Label(root1,justify=LEFT,text=f'Time: {time}',fg='red',bg='black').place(x=1180)
Label3=Label(root1,justify=RIGHT,text=f'Date: {date}',fg='red',bg='black').place(x=1180,y=20)

LabelofCalculator=Label(root1,text="\nSolar Parameter Calculator",font=('Arial Bold',18),fg='blue',bg='Black').place(x=60,y=450)
Label_Heading1=Label(root1,text="Press Calculate to display Values=>",font=('Arial',12),fg='springgreen',bg='black').place(x=60,y=530)


Label6=Label(root1,text="Enter PV Current :",font=('Arial',12),fg='gainsboro',bg='black').place(x=60,y=150)
Label6=Label(root1,text="Enter Output Current :",font=('Arial',12),fg='gainsboro',bg='black').place(x=60,y=180)
Label6=Label(root1,text="Enter Temprature in Kelvin :",font=('Arial',12),fg='gainsboro',bg='black').place(x=60,y=210)
Label6=Label(root1,text="Enter Maximum Current :",font=('Arial',12),fg='gainsboro',bg='black').place(x=60,y=240)
Label6=Label(root1,text="Enter Maximum Voltage :",font=('Arial',12),fg='gainsboro',bg='black').place(x=60,y=270)

PVCurrent1=Entry(root1,textvariable=PVCurrent).place(x=400,y=149)
OutputCurrent1=Entry(root1,textvariable=OutputCurrent).place(x=400,y=179)
Temprature1=Entry(root1,textvariable=Temprature).place(x=400,y=209)
MaxCurrent1=Entry(root1,textvariable=MaxCurrent).place(x=400,y=239)
MaxVoltage1=Entry(root1,textvariable=MaxVoltage).place(x=400,y=269)

Label4=Label(root1,text="Location : Asia/Calcutta",font=('Arial',12),fg='yellow',bg='black').place(x=60,y=300)
Label5=Label(root1,text="Enter Latitude(in degree) :",font=('Arial',12),fg='gainsboro',bg='black').place(x=60,y=330)
Label6=Label(root1,text="Enter Longitude(in degree) :",font=('Arial',12),fg='gainsboro',bg='black').place(x=60,y=360)
Label7=Label(root1,text="Enter Start Date for tracking(yyyy-mm-dd):",font=('Arial',12),fg='gainsboro',bg='black').place(x=60,y=390)
Label8=Label(root1,text="Enter End Date for tracking(yyyy-mm-dd):",font=('Arial',12),fg='gainsboro',bg='black').place(x=60,y=420)
Entry1=Entry(root1,textvariable=lat_var).place(x=400,y=330)
Entry2=Entry(root1,textvariable=lon_var).place(x=400,y=360)
Entry3=Entry(root1,textvariable=strdate).place(x=400,y=390)
Entry4=Entry(root1,textvariable=stpdate).place(x=400,y=420)

Button2=Button(root1,text='Exit!',command=end,bg='gray75').place(x=1240,y=710)
Button3=Button(root1,text='Return to Main Page!',command=mainpage,bg='gray75').place(x=20,y=10)
Button4=Button(root1,text='Calculate!',command=Calculate,bg='gray75').place(x=350,y=530)

LabelofIV=Label(root1,text="\nTrueTracking And BackTracking",font=('Arial Bold',18),fg='blue',bg='Black').place(x=700,y=30)
LabelHead2=Label(root1,text="To Display the TrueTracking Cuve and BackTracking Curve:",font=('Arial',12),fg='springgreen',bg='black').place(x=700,y=100)
Label5=Label(root1,text="Click Show=>",font=('Arial',12),fg='gainsboro',bg='black').place(x=700,y=150)
Button1=Button(root1,text='Show',command=submit,bg='gray75',width=10).place(x=850,y=150)

LabelofIV=Label(root1,text="\nGHI to POA",font=('Arial Bold',18),fg='blue',bg='Black').place(x=700,y=200)
LabelHead2=Label(root1,text="To Display the GHI to POA Curve:",font=('Arial',12),fg='springgreen',bg='black').place(x=700,y=270)
Label5=Label(root1,text="Click Show=>",font=('Arial',12),fg='gainsboro',bg='black').place(x=700,y=320)
Button1=Button(root1,text='Show',command=submit1,bg='gray75',width=10).place(x=850,y=320)

LabelofIV=Label(root1,text="\nI-V Curve of PV Cell",font=('Arial Bold',18),fg='blue',bg='Black').place(x=700,y=370)
LabelHead2=Label(root1,text="Select of the following options to continue:",font=('Arial',12),fg='springgreen',bg='black').place(x=700,y=440)
Label5=Label(root1,text="To plot I-V Curve of Vikram Solar Panel click show=>",font=('Arial',12),fg='gainsboro',bg='black').place(x=700,y=495)
Button1=Button(root1,text='Show',command=run,bg='gray75',width=10).place(x=1150,y=495)
Label6=Label(root1,text="To open the Specifications sheet of the Panel click open=>",font=('Arial',12),fg='gainsboro',bg='black').place(x=700,y=530)
Button2=Button(root1,text='Open',command=pdf,bg='gray75',width=10).place(x=1150,y=530)

root1.mainloop()