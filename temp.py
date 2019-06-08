import os
import glob
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from time import sleep, strftime, time
from multiprocessing import Process

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

def read_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temp():
    global temp
    lines = read_raw()
    
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_raw()
        
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp = float(temp_string) / 1000
        return temp

def write_temp(temperature):
    with open('/home/pi/Desktop/temp.csv', 'a') as log:
        log.write("{0},{1}\n".format(strftime("%Y-%m-%d %H:%M:%S"),str(temperature)))
        
def fan_state(fan):
    if fan == 1:
        print("wrrrr")
    elif fan == 0:
        print("silence")

x_len = 200
y_range = [10,50]
fig = plt.figure()
ax = fig.add_subplot(1,1,1)
xs = list(range(0,200))
ys = [0] * x_len
ax.set_ylim(y_range)
line, = ax.plot(xs, ys)
plt.xticks(rotation = 45, ha = 'right')
plt.subplots_adjust(bottom=0.30)
plt.title('Wykres temperatury w czasie')
plt.ylabel('Temperatura [C]')
plt.xlabel('Probki')    

def animate(i, ys):
    temperature = read_temp()
    ys.append(temperature)
    ys = ys[-x_len:]
    line.set_ydata(ys)
    return line,
   
def temp_plot():   
    ani = animation.FuncAnimation(fig, animate, fargs=(ys,), interval=50, blit = True)
    plt.show()

def log_and_fan():
    fan = 0
    while True:
        temperature=read_temp()
        write_temp(temperature)
        if temperature > 26:
            fan = 1
        elif temperature < 22:
            fan = 0
        fan_state(fan)
        sleep(10)
    
if __name__ == '__main__':
    p1 = Process(target=temp_plot)
    p1.start()
    p2 = Process(target=log_and_fan)
    p2.start()
    p1.join()
    p2.join()
