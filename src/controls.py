import time
import numpy as np


class NoObject(Exception):
    pass

class Controls(object):
    def __init__(self, lidar, gpio, carphys, encoder_consumer, lidar_consumer):
        self.lidar = lidar
        self.gpio = gpio
        self.encoder_consumer = encoder_consumer
        self.lidar_consumer = lidar_consumer
        self.carphys = carphys
        self.line = None
        self.obj = None

    def find_velocity_error(self, mode=0):   # mode 0: lidar // mode 1: encoders over networking
        if mode == 0:
            if self.obj.velocity:
                v_error = np.sign(self.obj.velocity[0])*(self.obj.velocity[0]**2+self.obj.velocity[0]**2)**0.5
            else:
                # TODO: Add condition for finding velocity error with encoders over network
                v_error = 0
        else:
            my_enc_vel = self.get_encoder_velocity()
            lead_enc_vel = 0   #get this from communications
            v_error = lead_enc_vel - my_enc_vel

        return v_error

    def find_distance_error(self,d_ref):
        distance = self.get_distance()
        d_error = -d_ref + distance
        print(f"d_ref = {d_ref}  distance = {distance}")
        return d_error

    def find_steering_error(self, speed):
        """
        +x is forward
        +y is left
        if s_error > 0 turn left
        if past object list not long enough just use current y position of car.
        """
        str = self.last_steering
        vel = speed
        past_obj_pos = self.carphys.update_path(self.lidar.get_position(self.obj), str, vel)
        #print(past_obj_pos)

        try:
            past_obj_pos.shape[0]
        except IndexError:
            print("index err")
            return self.lidar.get_position(self.obj)[1]
        if np.min(past_obj_pos[:, 0]) > 0:   # takes smallest x value
            return self.lidar.get_position(self.obj)[1]
        else:
            #remove this to enable car physics
            return self.lidar.get_position(self.obj)[1]
            min_i = np.argmin(abs(past_obj_pos[:, 0]))
            #print(f"past obj pos = {past_obj_pos}")
            #print(f"abs obj pos = {abs(past_obj_pos)}")
            #print(f"min index = {min_i}")
            try:
                if past_obj_pos[min_i, 0] < 1:
                    intersection = self.find_intersection(past_obj_pos[min_i, 0], past_obj_pos[min_i+1, 0])
                else:
                    intersection = self.find_intersection(past_obj_pos[min_i, 0], past_obj_pos[min_i-1, 0])

                s_error = intersection[1]
                return s_error
            except IndexError:
                return past_obj_pos[min_i, 0]
            except Exception as e:
                print("The exception is here!")
                print(e)

    def find_intersection(self, a1, a2):    #from https://web.archive.org/web/20111108065352/https://www.cs.mun.ca/%7Erod/2500/notes/numpy-arrays/numpy-arrays.html
        b1 = [0, 1]
        b2 = [0, -1]
        a1 = np.array(a1)
        a2 = np.array(a2)
        da = a2 + -1 * a1
        db = b2 + -1 * b1
        dp = a1 + -1 * b1
        dap = self.perp(da)
        denom = np.dot(dap,db)
        num = np.dot(dap,dp)
        return (num/denom)*db+b1

    def perp(self,a):
        b = np.empty_like(a)
        b[0] = -a[1]
        b[1] = a[0]
        return b

    def get_lidar_data(self):
        valid_read = False
        while not valid_read:
            scan = self.lidar_consumer.get_scan()
            if scan and not self.lidar_consumer.scan_read:
                try:
                    self.lidar_consumer.scan_read = True
                    data = self.lidar.scan_break_objects_lines(scan)
                    if not data:
                        raise NoObject
                    obj, line = data
                    self.obj = obj
                    self.line = line
                    valid_read = True
                except NoObject:
                    print("No object")
                    time.sleep(0.08)
                except Exception as e:
                    print(e)
                    raise ValueError("Get lidar data")
            else:
                time.sleep(0.01)

    def get_distance(self):
        position = self.lidar.get_position(self.obj)
        distance = (position[0]**2+position[1]**2)**0.5
        return distance

    def get_encoder_velocity(self):
        encoder_velocity = self.encoder_consumer.get_speed()
        return encoder_velocity

    def get_relative_lidar_velocity(self):
        relative_lidar_velocity = self.obj.velocity
        return relative_lidar_velocity


class Dumb_Networking_Controls(Controls):
    def __init__(self, lidar, gpio, carphys, network_consumer, encoder_consumer, lidar_consumer, mode=0):
        super(Dumb_Networking_Controls, self).__init__(lidar, gpio, carphys, encoder_consumer, lidar_consumer)    #runs init of superclass
        self.dumb_networking_mode = mode    # mode 0 is chain mode// mode 1 is leader mode
        self.accel_cmd = 0
        self.steering_list = [0]
        if mode == 0:
            #in chain mode
            self.get_lidar_data()
            self.initial_distance = self.get_distance()
        else:
            self.initial_distance = 500     # depends on car number and initial distance behind lead car
            # in follow the leader mode
            # get networking from lead car

    def control_loop(self, enc_vel):
        self.transmission_delay = self.get_transmission_delay()
        accel_cmd = self.accel_cmd
        if enc_vel is not 0:
            delay = self.initial_distance/enc_vel + self.transmission_delay
            delayed_time = time.time()-delay
            steering_cmd = self.get_delayed_steering_cmd(delayed_time)
        else:
            steering_cmd = 0

        self.gpio.set_servo_pwm(steering_cmd)
        self.gpio.set_motor_pwm(accel_cmd)
        return steering_cmd, accel_cmd

    def get_transmission_delay(self):
        #need to change this
        transmission_delay = 0.01
        return transmission_delay

    def get_newest_accel_cmd(self, cmd):
        self.accel_cmd = cmd #newest data

    def get_newest_steering_cmd(self, cmd):
        timestamp = time.time()
        self.steering_list.append((timestamp,cmd))    #newest data
        if len(self.steering_list) > 50:
            del self.steering_list[0]

    def get_delayed_steering_cmd(self,delayed_time):
        for i, j in enumerate(self.steering_list):
            if delayed_time > j[0]:
                steering_cmd = j[1]
                del self.steering_list[:i]
                return steering_cmd
        return 0

    """
    Copy velocity of lead vehicles
    Delay steering by velocity of my car divided by initial distance - transmission time_last
        in order to make steering commands at the same position as the lead vehicles

    If mode is chain find initial distance with lidar. Else pre set it manually
    In control loop do above
    """

class Lidar_Controls(Controls):
    def __init__(self, vp, vi, vd, vk, sp, si, sd, lidar, gpio, carphys, encoder_consumer, lidar_consumer, ref=0):
        super(Lidar_Controls, self).__init__(lidar, gpio, carphys, encoder_consumer, lidar_consumer)    #runs init of superclass
        self.velocity_P = vp
        self.velocity_I = vi
        self.velocity_D = vd
        self.velocity_Kp = vk

        self.velocity_pid_list = [] #add touple of (pid_val,time) for integration
        self.velocity_pid_length = 20
        self.velocity_pos_ref = 200 #mm reference position

        self.velocity_output_clamp = (-1,4)  #clamps output between these two values
        self.velocity_output_scaling = 1/100

        self.steering_P = sp
        self.steering_I = si
        self.steering_D = sd

        self.steering_pid_list = [] #add touple of (pid_val,time) for integration
        self.steering_pid_length = 20

        self.steering_output_clamp = (-10,10)  #clamps output between these two values
        self.steering_output_scaling = 1/100

        self.last_steering = 0

        if ref==0:
            print("getting ldiardata")
            self.get_lidar_data()
            print("lidar gotten")
            self.initial_distance = self.get_distance()
            self.carphys.set_past_obj_pos(self.lidar.get_position(self.obj))

    def control_loop(self, speed):
        d_ref = self.initial_distance
        v_error, d_error, s_error = self.get_errors(speed, d_ref)
        print(f"v_error = {v_error} d_error = {d_error} s_error = {s_error}")
        velocity_pid_input = d_error * self.velocity_Kp + v_error
        velocity_pid_output = self.velocity_pid_controller(velocity_pid_input)
        accel_cmd = self.convert_pid(velocity_pid_output, self.velocity_output_scaling, self.velocity_output_clamp)
        self.gpio.set_motor_pwm(accel_cmd)

        steering_pid_input = s_error
        steering_pid_output = self.steering_pid_controller(steering_pid_input)
        steering_cmd = self.convert_pid(steering_pid_output, self.steering_output_scaling, self.steering_output_clamp)
        self.gpio.set_servo_pwm(steering_cmd)
        self.last_steering = steering_cmd
        return steering_cmd, accel_cmd


    def get_errors(self, speed, d_ref):
        v_error = self.find_velocity_error()
        d_error = self.find_distance_error(d_ref)
        s_error = self.find_steering_error(speed)

        return v_error, d_error, s_error

    def velocity_pid_controller(self, pid_input):
        t = time.time()
        self.velocity_pid_list.append((pid_input,t))

        if len(self.velocity_pid_list) > self.velocity_pid_length:
            del self.velocity_pid_list[0]

        pid_val = self.proportional(pid_input, self.velocity_P) + \
                  self.integral(self.velocity_pid_list, self.velocity_I) + \
                  self.derivative(self.velocity_pid_list, self.velocity_D)

        return pid_val

    def steering_pid_controller(self, pid_input):
        t = time.time()
        self.steering_pid_list.append((pid_input,t))

        if len(self.steering_pid_list) > self.steering_pid_length:
            del self.steering_pid_list[0]

        pid_val = self.proportional(pid_input, self.steering_P) + \
                  self.integral(self.steering_pid_list, self.steering_I) + \
                  self.derivative(self.steering_pid_list, self.steering_D)

        return pid_val

    def proportional(self, pid_input, P):
        p_val = pid_input * P
        print(f"P = {p_val}")
        return p_val

    def integral(self, pid_list, I):
        if not pid_list or len(pid_list)<2:
            return 0

        modifier = I
        sum = 0
        """change taking from wrong side"""
        for x,(pid,t) in enumerate(pid_list[:-1]):    #reiman sum of distance between vehicles
            sum += pid * (t - pid_list[x+1][1])   #calculate deltat * pid val

        i_val = sum * modifier
        print(f"i = {i_val}")
        return i_val

    def derivative(self, pid_list, D):
        if not pid_list or len(pid_list)<2:
            return 0

        """change taking from wrong side"""
        d_val = (pid_list[-1][0]-pid_list[-2][0])/(pid_list[-1][1]-pid_list[-2][1])
        d_val *= D

        print(f"d = {d_val}")
        return d_val

    """convert value from PID controller to -10->10 value in sensor"""
    def convert_pid(self,pid_val,output_scaling,output_clamp):
        val = output_scaling*pid_val

        if val > output_clamp[1]:
            return output_clamp[1]
        elif val < output_clamp[0]:
            return output_clamp[0]
        else:
            return val
    """
    Use lidar and encoder alone to follow leading vehicle
    """

class Smart_Networking_Controls(Controls):
    def __init__(self, lidar, gpio, encoder):
        super(Smart_Networking_Controls, self).__init__(lidar, gpio, encoder)    #runs init of superclass


    """

    """
    def get_errors(self):
        v_error = self.find_velocity_error()
        d_error = self.find_distance_error()
        s_error = self.find_steering_error()

        return v_error, d_error, s_error
