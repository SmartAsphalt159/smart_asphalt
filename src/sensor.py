#!/usr/bin/python3

import Jetson.GPIO as GPIO
import time

#NOTE: channel indicates GPIO port

class GPIO_Interaction():
    def __init__(self, enc_ch, servo_ch, motor_ch):
        self.enc_ch = enc_ch
        self.servo_ch = servo_ch
        self.motor_ch = motor_ch
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup(self.enc_ch, GPIO.IN)
        GPIO.setup((self.servo_ch, self.motor_ch),GPIO.OUT)
        self.servo_pwm = GPIO.PWM(self.servo_ch, 50)
        self.motor_pwm = GPIO.PWM(self.motor_ch, 50)

    def shut_down(self):
        self.servo_pwm.stop()
        self.motor_pwm.stop()
        GPIO.cleanup()

    def servo_format(self, val): #-10 => 8.5 10=>5.5
        if val < -10:
            return 8.5
        elif val > 10:
            return 5.5
        else:
            return val*3/20 + 7

    def motor_format(self, val): #-10 => 8.5 10=>5.5
        if val < -10:
            return 8.5
        elif val > 10:
            return 5.5
        else:
            return val*3/20 + 7

    def set_servo_pwm(self, value):     #-10->10
        self.servo_pwm.ChangeDutyCycle(self.servo_format(float(value)))

    def set_motor_pwm(self, value):     #-10->10
        self.motor_pwm.ChangeDutyCycle(self.motor_format(float(value)))


class Encoder():
    def __init__(self, channel, mag_num=2, tire_r=35):
        self.mag_num = mag_num
        self.channel = channel
        self.r = tire_r
        self.tally = 0
        self.speed = 0
        self.speed_read = True
        self.last_time = time.time()
        GPIO.add_event_detect(self.channel, GPIO.BOTH,callback=self.on_edge)

    def on_edge(self):
        self.tally += 1

    def sample_speed(self):
        now = time.time()
        rps = self.tally/(2*self.mag_num*(self.last_time-now))
        speed = 2*3.1415*rps*self.r
        self.tally = 0
        self.last_time = now
        self.speed = speed
        self.speed_read = False

    def get_speed(self):
        self.speed_read = True
        return self.speed
