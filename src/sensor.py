#!/usr/bin/python3

import Jetson.GPIO as GPIO
from math import pi

# NOTE: channel indicates GPIO port


class GPIO_Interaction():
    def __init__(self, enc_ch, servo_ch, motor_ch):
        self.enc_ch = enc_ch
        self.servo_ch = servo_ch
        self.motor_ch = motor_ch
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup((self.servo_ch, self.motor_ch), GPIO.OUT)
        self.servo_pwm = GPIO.PWM(self.servo_ch, 50)
        self.motor_pwm = GPIO.PWM(self.motor_ch, 50)
        self.servo_pwm.start(self.servo_format(0))
        self.motor_pwm.start(self.motor_format(0))

    def shut_down(self):
        self.servo_pwm.stop()
        self.motor_pwm.stop()
        GPIO.cleanup()

    def servo_format(self, val): # -10 => 9/R 10=>5.5/L
        if val < -10:
            return 9
        elif val > 10:
            return 6
        else:
            return val*3/20 + 7.5

    def motor_format(self, val): # -10 => 8.5 10=>6
        offset = 0.781# 0.781
        val = val+offset
        if val < -10:
            return 9
        elif val > 10:
            return 6
        else:
            return val*3/20 + 7.5

    def set_servo_pwm(self, value):     # -10->10
        self.servo_pwm.ChangeDutyCycle(self.servo_format(float(value)))

    def set_motor_pwm(self, value):     # -10->10
        self.motor_pwm.ChangeDutyCycle(self.motor_format(float(value)))


class Encoder:
    def __init__(self, channel):  # TODO: Why is channel here and never used?
        tire_r = 0.035  # Tire_radius in meters
        self.mag_num = 2  # Amount of magnets
        print("Initializing encoder")
        self.r = tire_r
        self.tally = 0
        self.speed = 0
        self.last_speed = 0
        self.speed_array = []
        self.acceleration_array = []
        self.speed_read = True
        self.mutex = False

    def sample_speed(self, tally, delta_ms):
        self.tally = tally
        rps = self.tally/(self.mag_num*(delta_ms/1000))
        speed = 2*pi*rps*self.r  # meters per second (m/s)
        self.mutex = True # Critical Section
        self.speed_array.append((speed, delta_ms/1000))
        self.mutex = False
        self.speed_read = False

    def get_speed(self):
        total_t = 0
        d = 0
        t = []        
        if (self.mutex):
            t = self.speed_array
        
        print("len of speed array: ", len(t))
        if len(t) == 0:
            if self.last_speed == 0:
                return 0
            else:
                return self.last_speed
        print("len of speed array: ", len(t))
        for speed, d_time in t:
            total_t += d_time
            d += speed*d_time

        avg_speed = d/total_t
        if (self.mutex):
            self.speed_array.clear()
        self.speed_read = True
        self.last_speed = avg_speed
        return avg_speed

    def get_acceleration(self):
        pass
