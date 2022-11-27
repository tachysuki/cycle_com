
from m5stack import *
from m5stack_ui import *
from uiflow import *
import unit
import math

screen = M5Screen()
screen.clean_screen()
screen.set_screen_bg_color(0x000000)
gps0 = unit.get(unit.GPS, unit.PORTC)

pole_radius = 6356752.314245 #極半径
equator_radius = 6378137.0 #赤道半径
firstloop = True
global tripmode
tripmode = True
global dist_a
dist_a = 0
global dist_b
dist_b = 0

#Trip切り替え
def buttonB_wasPressed():
    tripmode = not tripmode
    pass

btnB.wasPressed(buttonB_wasPressed)

#Tripリセット
def buttonC_wasPressed():
    if tripmode:
        dist_a = 0
    else:
        dist_b = 0

    pass

btnC.wasPressed(buttonC_wasPressed)

def cal_distance(latlon_from, latlon_to):
    #経度緯度をラジアンに
    lat_from = math.radians(latlon_from[0])
    lon_from = math.radians(latlon_from[1])
    lat_to = math.radians(latlon_to[0])
    lon_to = math.radians(latlon_to[1])

    lat_difference = lat_from - lat_to #緯度差
    lon_difference = lon_from - lon_to #経度差
    lat_average = (lat_from + lat_to /2)#平均緯度

    e2 = (math.pow(equator_radius, 2) - math.pow(pole_radius, 2)) / math.pow(equator_radius, 2) #第一離心率^2

    w = math.sqrt(1- e2 * math.pow(math.sin(lat_average), 2))

    m = equator_radius * (1 - e2) / math.pow(w,3)#子午線曲率半径

    n = equator_radius / w #卯酉線曲半径

    distance = math.sqrt(math.pow(m * lat_difference, 2) + math.pow(n * lon_difference * math.cos(lat_average), 2))

    return(distance / 1000)

speedtext = M5Label('Text', x=60, y=10, color=0xFFFFFF, font=FONT_MONT_48, parent=None)
timetext = M5Label('Text', x=50, y=70, color=0xFFFFFF, font=FONT_MONT_30, parent=None)
avespeedtext = M5Label('Text', x=59, y=110, color=0xFFFFFF, font=FONT_MONT_30, parent=None)
triptext =  M5Label('Text', x=50, y=150, color=0xFFFFFF, font=FONT_MONT_30, parent=None)
qualitytext =  M5Label('Text', x=0, y=220, color=0xFFFFFF, font=FONT_MONT_14, parent=None)
Label6 = M5Label('Text', x=130, y=215, color=0xFFFFFF, font=FONT_MONT_18, parent=None)

while True:
    gps0.set_time_zone(9)
    #精度表示
    if str(gps0.pos_quality) == 'NO signal':
        quality = 'NO'
    else:
        quality = gps0.pos_quality

    qualitytext.set_text('GPS Quality: ' + str(quality))

    #時間表示
    timetext.set_text('Time: ' + str(gps0.gps_time))

    #速度表示
    if len(gps0.speed) > 0 and str(gps0.pos_quality) != 'NO signal':
        speedtext.set_text(str('{:.1f}'.format(float(gps0.speed))) + 'km/h')
        if float(gps0.speed) > 0:
            avespeed = avespeed / 2 + float(gps0.speed)

        avespeedext.set_text('No Signal')

    #Trip関係
    if str(gps0.pos_quality) != 'NO signal' and str(gps0.pos_quality) != '':
        if firstloop:
            point_last = [float(gps0.latitude[:-1])/100,float(gps0.longitude[:-1])/100]
        else:
            point_kast = point_now

        point_now = [float(gps0.latitude[:-1])/100,float(gps0.longitude[:-1])/100]
        dist = int(cal_distance(point_last,point_now))
        dist_a = dist_a + dist
        dist_b = dist_b + dist

    if tripmode:
        triptext.set_text('TripA: ' + str('{:.2f}'.format(dist_a)) + 'km')
    else:
        triptext.set_text('TripB: ' + str('{:.2f}'.format(dist_b)) + 'km')

    wait_ms(2)
