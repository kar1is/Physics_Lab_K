import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import math
import csv
from glob import glob
import os

# Constants #

h = 6.62607015e-34
c = 2.99792458e8
kb = 1.380649e-23
A = 1.684
B = 15.2e3

c1 = 2*math.pi*h*c**2
c2 = h*c/kb

wv_min = 400
wv_max = 800
offset = 73

# Wavelengths to be considered for theortical data
wavelengths = np.arange(200, 6e3, 1)



class Theory:
    # Returns theoretical data for intensity vs wavelength for temperature T (normalized)
    def wavelength(self, wav, T):
        intensity = []
        wav_x = []
        norm = 0
        for i in wav:
            wav_x.append(i)
            intensity.append(c1/( ((i*1e-9)**5)*(math.e**(c2/((i*1e-9)*T)) - 1.0) ))
            norm = max(norm, c1/( ((i*1e-9)**5)*(math.e**(c2/((i*1e-9)*T)) - 1.0) ))
        intensity = np.array(intensity)/norm
        return wav_x, intensity
    
    # Returns theoretical data for intensity vs refraction angle for temperature T (normalized)
    def angle(self, wav, T):
        intensity = []
        angle_x = []
        norm = 0
        for i in wav: 
            if math.sqrt(3)/2*(math.sqrt((A+B/(i**2))**2-3/4)-1/2)<=1:
                angle_x.append(math.asin(math.sqrt(3)/2*(math.sqrt((A+B/(i**2))**2-3/4)-1/2))*180/math.pi)
                intensity.append(c1/( ((i*1e-9)**5)*(math.e**(c2/((i*1e-9)*T)) - 1.0) ))
                norm = max(norm, c1/( ((i*1e-9)**5)*(math.e**(c2/((i*1e-9)*T)) - 1.0) ))
            else:
                continue
        intensity = np.array(intensity)/norm
        return angle_x, intensity

 

class Measurement:
    # Returns measured data for intensity vs wavelength for temperature T (normalized)
    def wavelength(self, plot):
        x = [] 
        y = []
        x_makk = 0
        norm = 0.0
        first = False
        for row in plot:
            if not first:
                first = True
                continue
            if row[3].find('E') != -1:
                continue
            else:
                x_p = math.radians(offset-float(row[3].replace(',', '.')))
                if (15.2e3)/(math.sqrt(((2/math.sqrt(3)*math.sin(x_p)+0.5)**2)+0.75)-A)<0:
                    continue
                else:
                    x_pp = math.sqrt((15.2e3)/(math.sqrt(((2/math.sqrt(3)*math.sin(x_p)+0.5)**2)+0.75)-A))
                    x.append(x_pp)
                    y_pp = (float(row[0].replace(',', '.')))
                    if y_pp > norm:
                        norm = max(norm, y_pp)
                        x_makk = x_pp
                    y.append(y_pp)
        y = np.array(y)/norm
        print(x_makk)
        return x, y, wv_min, wv_max
    
    # Returns measured data for intensity vs refraction angle for temperature T (normalized)
    def angle(self, plot):
        x = [] 
        y = []
        norm = 0.0
        angle_min = math.asin(math.sqrt(3)/2*(math.sqrt((A+B/(wv_max**2))**2-3/4)-1/2))*180/math.pi
        angle_max = math.asin(math.sqrt(3)/2*(math.sqrt((A+B/(wv_min**2))**2-3/4)-1/2))*180/math.pi
        first = False
        for row in plot:
            if not first:
                first = True
                continue
            if row[3].find('E') != -1:
                continue
            else:
                x.append(offset-float(row[3].replace(',', '.')))
                y_pp = (float(row[0].replace(',', '.')))
                norm = max(norm, y_pp)
                y.append(y_pp)
        y = np.array(y)/norm
        return x, y, angle_min, angle_max



def draw_spectrum(plt, x_beg, x_end, inp):
    def rects(x,y,w,h,c):
        ax = plt.gca()
        polygon = plt.Rectangle((x,y),w,h,color=c,alpha=0.025)
        ax.add_patch(polygon)
    
    def rainbow_fill(X,Y, cmap):
        plt.plot(X,Y,lw=0)  # Plot so the axes scale correctly
    
        dx = X[1]-X[0]
        N  = float(X.size)
    
        for n, (x,y) in enumerate(zip(X,Y)):
            color = cmap(n/N)
            rects(x,-0.1,dx,y,color)
       
    X = np.linspace(x_beg,x_end,100)
    Y = X*0+1.2
    if inp==1:
        rainbow_fill(X,Y, plt.get_cmap("jet_r"))
    else:
        rainbow_fill(X,Y, plt.get_cmap("jet"))
    return



folder = glob('.\\Data_K_Lab\*') # All measurement data should be in this subfolder

inp = 0
margins = 0
while True:
    inp = input("Type 1 - intensity vs angle, 2 - intensity vs wavelength: ")
    if inp == '1' or inp == '2':
        inp = int(inp)
        break
while True:
    margins = input("Type 1 - normal margins, 2 - tight margins: ")
    if margins == '1':
        margins = 'None'
        break
    elif margins == '2':
        margins = 'tight'
        break

for file in folder: 
    data = csv.reader(open(file,'r'), delimiter = ';')
        
    head, tail = os.path.split(file)
    head = tail[:-4]
    
    print(head)
    
    temp = [1498.84297, 1609.84313, 1713.88678, 1811.62241, 1574.69388,
            1999.97087, 2086.72371, 2180.0224, 2255.56993, 2323.10271]
    
    temperature = 0
    
    if head == '5V':
        temperature = 2000
    elif head == '5_5V':
        temperature = 2100
    elif head == '6V':
        temperature = 2350
    elif head == '6_5V':
        temperature = 2450
    elif head == '7V':
        temperature = 2560
    elif head == '7_5V':
        temperature = 2650
    elif head == '8V':
        temperature = 2740
    else:
        break
    
    # Set up
    ax = plt.gca()
    ax.set_ylim([-0.1, 1.1])
    plt.grid(True)
    mpl.rcParams['grid.color'] = '#d6d6d6'
    ax.set_axisbelow(True) 
    
    if inp==1:
        x_th, y_th = Theory().angle(wavelengths, temperature)
        x_ms, y_ms, x_beg, x_end = Measurement().angle(data)
    else:
        x_th, y_th = Theory().wavelength(wavelengths, temperature)
        x_ms, y_ms, x_beg, x_end = Measurement().wavelength(data)
    
    # Plot data
    plt.plot(x_th, y_th, label='Theoretical', color='black')
    plt.scatter(x_ms, y_ms, 5, label='Measured', color='red')
    
    plt.legend(loc='upper right',fancybox=True, framealpha=1)
    plt.ylabel('Light intensity, rel')
    draw_spectrum(plt, x_beg, x_end, inp)
    
    # Export plots
    if inp==1:
        plt.xlabel('Angle, degrees') 
        os.makedirs(os.path.dirname(r'.\Figures_angle\\'), exist_ok=True)
        plt.savefig(r'.\Figures_angle\\'+head+r'_angle.png', bbox_inches=margins, dpi=600)
    else:
        plt.xlabel(r'Wavelength of light $\lambda$, nm') 
        #os.makedirs(os.path.dirname(r'.\Figures_wavelength\\'), exist_ok=True)
        #plt.savefig(r'.\Figures_wavelength\\'+head+r'_wavelength.png', bbox_inches=margins, dpi=600)
    plt.show()