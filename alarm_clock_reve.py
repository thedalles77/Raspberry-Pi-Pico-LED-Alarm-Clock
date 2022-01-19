#   Copyright 2022 Frank Adams
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
import machine
import utime
import time
#
pico_led = machine.Pin(25, machine.Pin.OUT)
#
white_led = machine.PWM(machine.Pin(0))
white_led.freq(1000)
#
BuzzerObj=machine.PWM(machine.Pin(19))
#
light_sensor = machine.ADC(0) #analog value 
#
pir_sensor = machine.Pin(18, machine.Pin.IN)
#
digit_1 = machine.Pin(5, machine.Pin.OUT) # digit enables, active high
digit_2 = machine.Pin(4, machine.Pin.OUT)
digit_3 = machine.Pin(3, machine.Pin.OUT)
digit_4 = machine.Pin(2, machine.Pin.OUT)
#
segment_a = machine.Pin(13, machine.Pin.OUT) # LED segments, active high
segment_b = machine.Pin(15, machine.Pin.OUT)
segment_c = machine.Pin(11, machine.Pin.OUT)
segment_d = machine.Pin(9, machine.Pin.OUT)
segment_e = machine.Pin(8, machine.Pin.OUT)
segment_f = machine.Pin(14, machine.Pin.OUT)
segment_g = machine.Pin(12, machine.Pin.OUT)
segment_h = machine.Pin(10, machine.Pin.OUT)
#
button_minute = machine.Pin(6, machine.Pin.IN, machine.Pin.PULL_UP) # minute adjust push button, active low
button_hour = machine.Pin(7, machine.Pin.IN, machine.Pin.PULL_UP) # hour adjust push button, active low
set_time = machine.Pin(16, machine.Pin.IN, machine.Pin.PULL_UP) # slide switch, high=set time, low=set alarm
alarm_on = machine.Pin(17, machine.Pin.IN, machine.Pin.PULL_UP) # slide switch, high=alarm on, low=alarm off
# initial values
digit_1.value(0) # turn off all digit enables
digit_2.value(0)
digit_3.value(0)
digit_4.value(0)
segment_a.value(0) # turn off all LED segments
segment_b.value(0)
segment_c.value(0)
segment_d.value(0)
segment_e.value(0)
segment_f.value(0)
segment_g.value(0)
segment_h.value(0)
pico_led.value(0)
white_led.duty_u16(0)

global second_counter # 0 thru 59. set this to the current second
global minute_counter # 0 thru 59. set this to the current minute
global hour_counter # 24 hour mode 0 thru 23. Set this to the current hour

second_counter = 0
minute_counter = 0
hour_counter = 0

minute_alarm = 0
hour_alarm = 12

buzzed = False

def tick(timer):
    global second_counter 
    global minute_counter 
    global hour_counter
    if second_counter == 59:
        second_counter = 0
        if minute_counter == 59:
            minute_counter = 0
            if hour_counter == 23:
                hour_counter = 0
            else:
                hour_counter += 1  # increment hour counter
        else:
            minute_counter += 1  # increment minute counter
    else:
        second_counter += 1  # increment second counter

def segment_decode(digit,dot):
    if digit == 0:
        segment_a.value(1)   
        segment_b.value(1)
        segment_c.value(1)
        segment_d.value(1)
        segment_e.value(1)
        segment_f.value(1)
        segment_g.value(0)
    elif digit == 1:
        segment_a.value(0)   
        segment_b.value(1)
        segment_c.value(1)
        segment_d.value(0)
        segment_e.value(0)
        segment_f.value(0)
        segment_g.value(0)
    elif digit == 2:
        segment_a.value(1)   
        segment_b.value(1)
        segment_c.value(0)
        segment_d.value(1)
        segment_e.value(1)
        segment_f.value(0)
        segment_g.value(1)
    elif digit == 3:
        segment_a.value(1)   
        segment_b.value(1)
        segment_c.value(1)
        segment_d.value(1)
        segment_e.value(0)
        segment_f.value(0)
        segment_g.value(1)
    elif digit == 4:
        segment_a.value(0)   
        segment_b.value(1)
        segment_c.value(1)
        segment_d.value(0)
        segment_e.value(0)
        segment_f.value(1)
        segment_g.value(1)
    elif digit == 5:
        segment_a.value(1)   
        segment_b.value(0)
        segment_c.value(1)
        segment_d.value(1)
        segment_e.value(0)
        segment_f.value(1)
        segment_g.value(1)
    elif digit == 6:
        segment_a.value(1)   
        segment_b.value(0)
        segment_c.value(1)
        segment_d.value(1)
        segment_e.value(1)
        segment_f.value(1)
        segment_g.value(1)
    elif digit == 7:
        segment_a.value(1)   
        segment_b.value(1)
        segment_c.value(1)
        segment_d.value(0)
        segment_e.value(0)
        segment_f.value(0)
        segment_g.value(0)
    elif digit == 8:
        segment_a.value(1)   
        segment_b.value(1)
        segment_c.value(1)
        segment_d.value(1)
        segment_e.value(1)
        segment_f.value(1)
        segment_g.value(1)
    elif digit == 9:
        segment_a.value(1)   
        segment_b.value(1)
        segment_c.value(1)
        segment_d.value(1)
        segment_e.value(0)
        segment_f.value(1)
        segment_g.value(1)
    else:
        segment_a.value(0)   
        segment_b.value(0)
        segment_c.value(0)
        segment_d.value(0)
        segment_e.value(0)
        segment_f.value(0)
        segment_g.value(0)
    if dot == 0: # see if decimal point should be displayed
        segment_h.value(0) # dot is off
    else:
        segment_h.value(1) # dot is on
    return

def buzzer(buzzerPinObject,frequency,sound_duration,silence_duration):
    # Set duty cycle to a positive value to emit sound from buzzer
    buzzerPinObject.duty_u16(int(65536*0.2))
    # Set frequency
    buzzerPinObject.freq(frequency)
    # wait for sound duration
    time.sleep(sound_duration)
    # Set duty cycle to zero to stop sound
    buzzerPinObject.duty_u16(int(65536*0))
    # Wait for sound interrumption, if needed 
    time.sleep(silence_duration)

#start the timer
machine.Timer().init(freq=1, mode=machine.Timer.PERIODIC, callback=tick)
BuzzerObj.deinit() #Deactivates the buzzer

while True: # endless loop
    if set_time.value() == True: # set and display time
        light_reading = light_sensor.read_u16() # ADC reads room light. Range is 47,000=Very Dark 10,000=Very Bright    
        if ((pir_sensor.value() == True) & (light_reading >= 33000)): # Motion and dark room
            white_led.duty_u16(100) # turn on white LED as a nightlight (adjust pwm setting to make it dim)
        else:
            white_led.duty_u16(0) # turn off white LED
# check for motion or room light turned on. Either one causes 4 digits of clock to be displayed 
        if ((pir_sensor.value() == True) | (light_reading <= 33000)):
            digit_4.value(1) # turn on far right digit
            segment_decode(minute_counter % 10,0) # display remainder of minute_counter / 10 = 1's column
            utime.sleep_ms(1) # wait
            segment_decode(100,0) # all segments off
            digit_4.value(0) # turn off far right digit
            digit_3.value(1) # turn on next digit
            segment_decode(minute_counter//10,0) # display integer division (truncates remainder) = 10's column
            utime.sleep_ms(1) # wait
            segment_decode(100,0) # all segments off
            digit_3.value(0) # turn off current digit
            digit_2.value(1) # turn on next digit
            segment_decode(hour_counter % 10,1) # display remainder of hour_counter / 10 = 1's column
            utime.sleep_ms(1) # wait
            segment_decode(100,0) # all segments off
            digit_2.value(0) # turn off current digit
            digit_1.value(1) # turn on next digit
            if hour_counter//10 != 0: # only display if not a leading zero
                segment_decode(hour_counter//10,0) # display integer division (truncates remainder) = 10's column
            else: # leading zero so turn off the leds
                segment_decode(100,0) # all segments off
            utime.sleep_ms(1) # wait
            segment_decode(100,0) # all segments off
            digit_1.value(0) # turn off current digit (all digits off)
        else:
            segment_decode(100,0) # all segments off
            utime.sleep_ms(1) # wait before proceeding
    
        if button_minute.value() == False:  #check if minute button is pushed (active low)
            if minute_counter == 59: # don't let it go to 60
                minute_counter = 0
                if hour_counter == 23: # don't let it go to 24
                    hour_counter = 0
                else:
                    hour_counter += 1  # increment hour counter
            else:
                minute_counter += 1  # increment minute counter
            utime.sleep_ms(150) # wait so doesn't increment too fast
    
        if button_hour.value() == False:  #check if hour button is pushed (active low)
            if hour_counter == 23: # don't let it go to 24
                hour_counter = 0
            else:
                hour_counter += 1  # increment hour counter
            utime.sleep_ms(150) # wait so doesn't increment too fast
#
# set and display the alarm time    
    else:   
        if button_minute.value() == False:  #check if minute button is pushed
            if minute_alarm == 59: # don't let it go to 60
                minute_alarm = 0
                if hour_alarm == 23: # don't let it go to 24
                    hour_alarm = 0
                else:
                    hour_alarm += 1  # increment hour value
            else:
                minute_alarm += 1  # increment minute value
            utime.sleep_ms(150) # wait so doesn't increment too fast
    
        if button_hour.value() == False:  #check if hour button is pushed
            if hour_alarm == 23: # don't let it go to 24
                hour_alarm = 0
            else:
                hour_alarm += 1  # increment hour value
            utime.sleep_ms(150) # wait so doesn't increment too fast
#show the alarm time on display
        digit_4.value(1) # turn on far right digit
        segment_decode(minute_alarm % 10,0) # display remainder of minute_counter / 10 
        utime.sleep_ms(1) # wait
        segment_decode(100,0) # all segments off
        digit_4.value(0) # turn off far right digit
        digit_3.value(1) # turn on next digit
        segment_decode(minute_alarm//10,0) # display integer division truncates remainder
        utime.sleep_ms(1) # wait
        segment_decode(100,0) # all segments off
        digit_3.value(0) # turn off current digit
        digit_2.value(1) # turn on next digit
        segment_decode(hour_alarm % 10,1) # display segments
        utime.sleep_ms(1) # wait
        segment_decode(100,0) # all segments off
        digit_2.value(0) # turn off current digit
        digit_1.value(1) # turn on next digit
        segment_decode(hour_alarm//10,0) # display segments
        utime.sleep_ms(1) # wait
        segment_decode(100,0) # all segments off
        digit_1.value(0) # turn off current digit (all digits off)
#
    if alarm_on.value() == False: # alarm is off
        pico_led.value(0)
        buzzed = False
    else: #alarm is on
        pico_led.value(1) # use pico led to show alarm is turned on
        # alarm turned on so check if it should buzz
        if (minute_alarm == minute_counter) & (hour_alarm == hour_counter) & (buzzed == False):
            # Play beginning of Beethoven's 5th symphony
            buzzer(BuzzerObj,659,0.2,0.1) #E
            buzzer(BuzzerObj,659,0.2,0.1) #E
            buzzer(BuzzerObj,659,0.2,0.1) #E
            buzzer(BuzzerObj,523,0.7,0.7) #C
            #
            buzzer(BuzzerObj,587,0.2,0.1) #D
            buzzer(BuzzerObj,587,0.2,0.1) #D
            buzzer(BuzzerObj,587,0.2,0.1) #D
            buzzer(BuzzerObj,494,0.7,0.1) #B
            #
            BuzzerObj.deinit() #Deactivates the buzzer
            buzzed = True
