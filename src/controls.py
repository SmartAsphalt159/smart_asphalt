import time
import numpy as np
from carphysics import Car
# TODO: Utilization Conventions https://namingconvention.org/python/


class NoObject(Exception):
    pass


class Controls(object):
    def __init__(self, lidar, gpio, carphys, encoder_consumer, lidar_consumer, network_producer=None):
        self.lidar = lidar
        self.gpio = gpio
        self.encoder_consumer = encoder_consumer
        self.lidar_consumer = lidar_consumer
        self.network_producer = network_producer
        self.carphys = carphys
        self.line = None
        self.obj = None

    def find_velocity_error(self, mode=0, target_velocity=0):   # mode 0: lidar // mode 1: encoders over networking
        if mode == 0:
            if self.obj.velocity:
                velocity_error = np.sign(self.obj.velocity[0])*(self.obj.velocity[0]**2+self.obj.velocity[0]**2)**0.5
            else:
                # TODO: Add condition for finding velocity error with encoders over network
                velocity_error = 0
        else:
            my_enc_vel = self.get_encoder_velocity()
            lead_enc_vel = target_velocity  # get this from communications
            velocity_error = lead_enc_vel - my_enc_vel

        return velocity_error

    def find_distance_error(self, d_ref):
        distance = self.get_distance()
        d_error = -d_ref + distance
        print(f"d_ref = {d_ref}  distance = {distance}")
        return d_error

    def find_steering_error(self, speed):
        """ TODO: Verify this is correct way of finding steering error, where is Steering Target?
        +x is forward
        +y is left
        if s_error > 0 turn left
        if past object list not long enough just use current y position of car.
        """
        str = self.last_steering
        vel = speed
        past_obj_pos = self.carphys.update_path(self.lidar.get_position(self.obj), str, vel)
        # print(past_obj_pos)

        try:
            past_obj_pos.shape[0]
        except IndexError:
            print("index err")
            return self.lidar.get_position(self.obj)[1]
        if np.min(past_obj_pos[:, 0]) > 0:   # takes smallest x value
            return self.lidar.get_position(self.obj)[1]
        else:
            # remove this to enable car physics
            return self.lidar.get_position(self.obj)[1]
            min_i = np.argmin(abs(past_obj_pos[:, 0]))
            # print(f"past obj pos = {past_obj_pos}")
            # print(f"abs obj pos = {abs(past_obj_pos)}")
            # print(f"min index = {min_i}")
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

    def find_intersection(self, a1, a2):    # from https://web.archive.org/web/20111108065352/https://www.cs.mun.ca/%7Erod/2500/notes/numpy-arrays/numpy-arrays.html
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

    def perp(self, a):
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
                        try:
                            time.sleep(0.08)
                        except KeyboardInterrupt as e:
                            raise e
                    except KeyboardInterrupt as e:
                        raise e
                except KeyboardInterrupt as e:
                    raise e
                except Exception as e:
                    print(e)
                    raise ValueError("Get lidar data")
            else:
                try:
                    time.sleep(0.01)
                except KeyboardInterrupt as e:
                    raise e

    def get_distance(self):
        position = self.lidar.get_position(self.obj)
        distance = (position[0]**2+position[1]**2)**0.5
        return distance

    def get_encoder_velocity(self):
        """ Gets the velocity of the encoder in meters per second """
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
        self.last_steering_cmd = 0
        self.last_throttle_cmd = 0
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
        print(f"enc vel: {enc_vel}")
        if enc_vel !=  0:
            delay = self.initial_distance/enc_vel + self.transmission_delay
            delayed_time = time.time()-delay
            steering_cmd = self.get_delayed_steering_cmd(delayed_time)
        else:
            steering_cmd = 0
        
        print(f"str: {steering_cmd} accel: {accel_cmd}")
    
        if steering_cmd != self.last_steering_cmd: 
            self.gpio.set_servo_pwm(steering_cmd)
            self.last_steering_cmd = steering_cmd
        if accel_cmd != self.last_throttle_cmd: 
            self.gpio.set_motor_pwm(accel_cmd)
            self.last_throttle_cmd = accel_cmd
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
        if len(self.steering_list) < 1:
            return 0
        for i, j in enumerate(self.steering_list):
            if delayed_time > j[0]:
                steering_cmd = j[1]
                del self.steering_list[:i]
                return steering_cmd
        return 0


class LidarControls(Controls):
    """
    Copy velocity of lead vehicles
    Delay steering by velocity of my car divided by initial distance - transmission time_last
        in order to make steering commands at the same position as the lead vehicles
    If mode is chain find initial distance with lidar. Else pre set it manually
    In control loop do above
    """

    def __init__(self, vp, vi, vd, vk, sp, si, sd, lidar, gpio, carphys, encoder_consumer, lidar_consumer, ref=0):
        super(LidarControls, self).__init__(lidar, gpio, carphys, encoder_consumer, lidar_consumer)    #runs init of superclass
        self.velocity_P = vp
        self.velocity_I = vi
        self.velocity_D = vd
        self.velocity_Kp = vk

        self.velocity_pid_list = []  # add tuple of (pid_val,time) for integration
        self.velocity_pid_length = 20
        self.velocity_pos_ref = 200  # millimeters (mm) reference position

        self.velocity_output_clamp = (-1, 4)  # clamps output between these two values
        self.velocity_output_scaling = 1/100

        self.steering_P = sp
        self.steering_I = si
        self.steering_D = sd

        self.steering_pid_list = []  # add tuple of (pid_val,time) for integration
        self.steering_pid_length = 20

        self.steering_output_clamp = (-10, 10)  # clamps output between these two values
        self.steering_output_scaling = 1/100

        self.last_steering = 0

        if ref == 0:
            print("getting lidar data")
            try:
                self.get_lidar_data()
            except KeyboardInterrupt as e:
                raise e
            print("lidar gotten")
            self.initial_distance = self.get_distance()
            self.carphys.set_past_obj_pos(self.lidar.get_position(self.obj))

    def control_loop(self, speed):
        d_ref = self.initial_distance
        v_error, d_error, s_error = self.get_errors(speed, d_ref)
        print(f"v_error = {v_error} d_error = {d_error} s_error = {s_error}")
        velocity_pid_input = d_error * self.velocity_Kp + v_error
        velocity_pid_output = self.velocity_pid_controller(velocity_pid_input)
        accel_cmd = self.convert_pid(velocity_pid_output, self.velocity_output_scaling, self.velocity_output_clamp) # TODO PID: output wtf is happening here
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
        self.velocity_pid_list.append((pid_input, t))

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
    def convert_pid(self, pid_val, output_scaling, output_clamp):
        val = output_scaling*pid_val

        if val > output_clamp[1]:
            return output_clamp[1]
        elif val < output_clamp[0]:
            return output_clamp[0]
        else:
            return val


class NetworkAdaptiveCruiseController:
    """
        This controller is designed to work on the "following" vehicle to attempt and reach
        the desired velocity commanded that the "lead" vehicle that it is following. This class is design
        to be agnostic to the lidar. This means we wont have measurements of distance or tracking of the
        "lead" vehicle beyond velocity and steering commands.
    """

    def __init__(self, gpio=None, car_physics=None, encoder_consumer=None, is_sim_car=False):
        """
        Initializes the NetworkAdaptiveCruiseController class as long as the parameters are not
        None.

        :param gpio:
        :param car_physics:
        :param encoder_consumer:
        :param network_producer:
        """
        if (gpio is None): 
            raise ValueError("The gpio parameter in NetworkVelocityController was None!")
        if (car_physics is None):
            raise ValueError("The car_physics parameter in NetworkVelocityController was None!")
        if (encoder_consumer is None):
            raise ValueError("The encoder_consumer parameter in NetworkVelocityController was None!")
        # TODO: Verify network producer/consumer is what I want
        self.is_sim_car = is_sim_car
        if self.is_sim_car is True:
            self.encoder_consumer = None
        else:
            self.encoder_consumer = encoder_consumer

        self.gpio = gpio
        self.car_physics = car_physics
        self.car = Car(0, 0.07)             # Mass is zero for now and 0.07 meters is diameter of tire

        # Network Controller Variables and Parameters for controls
        self.desired_velocity = None
        self.measured_velocity = 0
        self.desired_steering_angle = None  # TODO: is this a good name to use?
        self.transmission_delay_millisecs = 3  # TODO: utilize a ping command to get round trip avg time, negligable
        self.encoder_sampling_rate = 400  # units in milliseconds
        self.integral_delta_time = 1/self.encoder_sampling_rate  # at different intervals in case of changes.
        self.proportional_constant = 0      # Modify P term as needed
        self.integral_constant = 0          # Modify I term as needed
        self.derivative_constant = 0        # Modify D term as needed
        self.accumulated_error = 0
        self.pid_limit_max = 10  # Can be modified
        self.pid_limit_min = 0   # Can be modified
        self.previous_velocity_error = 0
        # self.steering_output_clamp = (-10, 10)  # clamps output between these two values
        self.pid_out_scaling = 1/100

    def cruise_control_init_set_point(self):
        """
        Resets Control Variables
        :return:
        """
        self.desired_velocity = 0
        self.accumulated_error = 0

    def cruise_control(self):
        """
        Provides vehicle velocity control in the longitudinal direction using only the information from the
        encoder module to reach desired velocity and controls motors as a result.
        :return: None
        """
        if self.measured_velocity is None:
            raise ValueError("In cruise_control, measured_velocity has value of None, must be assigned!")

        # PI Controller Begins
        # pi_out = 0
        # tolerance = 2.5  # Error within 2.5 m/s of desired velocity we've reached goal
        velocity_error = self.desired_velocity - self.measured_velocity
        # if abs(velocity_error) < tolerance:
        #    pi_out = self.desired_velocity  # TODO: This should change such that we maintain our current velocity
        # else:
        proportional_expression = self.proportional_constant * velocity_error
        self.accumulated_error = velocity_error + self.accumulated_error
        integral_expression = self.integral_constant * self.accumulated_error * self.integral_delta_time
        # Anti windup for I term
        derivative_expression = self.derivative_constant * self.previous_velocity_error

        self.previous_velocity_error = velocity_error
        pi_out = proportional_expression + integral_expression + derivative_expression
        print("P=", proportional_expression, " I=", integral_expression, " D=", derivative_expression, "pid_out=", pi_out)

        return pi_out

    def control_loop(self):
        """
        Executes the Loop for the network cruise controller and verifies mode of operation is sim or real
        Reference: https://code.activestate.com/recipes/577231-discrete-pid-controller/
        Reference: https://github.com/ivmech/ivPID
        :return: None
        """

        if self.is_sim_car is False:
            self.measured_velocity = self.encoder_consumer.get_speed()
            print(self.measured_velocity)
        pi_controller_output = self.cruise_control()
        adjusted_throttle = self.clamp(pi_controller_output)
        self.gpio.set_motor_pwm(adjusted_throttle)
        print("Adjusted Throttle: ", adjusted_throttle)
        # Motor speed is between 0 - 10 where 0 is neutral and 10 is max throttle, we want to translate throttle
        # clamp
        # pi_controller clean_up
        # We want to output the change in power
        return adjusted_throttle

    def clamp(self, pid_out):
        """ Meant to clamp and scale the value of the pid to a reasonable range for the motor function """
        scaled_pid = self.pid_out_scaling * pid_out
        clamped_adjustment = max(min(self.pid_limit_max, scaled_pid), self.pid_limit_min)
        return clamped_adjustment

    def anti_windup(self):
        pass

    def set_measured_velocity(self, measured_velocity):
        """
        Assigns the measured_velocity when unable to be set from the network so in the case of the "fake car"
        :param measured_velocity: velocity value recorded from a sensor in m/s
        :return: None
        """
        self.measured_velocity = measured_velocity

    def set_desired_velocity(self, desired_velocity):
        """
        Assigns the desired_velocity for the controller
        :param desired_velocity: the set point to reach measured in meters per second (m/s)
        :return: None
        """
        if (self.desired_velocity - desired_velocity) == 0:
            self.cruise_control_init_set_point()
        self.desired_velocity = desired_velocity

    def get_desired_velocity(self):
        """
        :return: The desired velocity in m/s
        """
        return self.desired_velocity

    def set_proportional_value(self, pval):
        self.proportional_constant = pval

    def set_integral_value(self, ival):
        self.integral_constant = ival

    def set_derivative_value(self, dval):
        self.derivative_constant = dval


class LidarNetworkControls(Controls):
    """
    Copy velocity of lead vehicles
    Delay steering by velocity of my car divided by initial distance - transmission time_last
        in order to make steering commands at the same position as the lead vehicles
    If mode is chain find initial distance with lidar. Else pre set it manually
    In control loop do above
    """

    def __init__(self, vp, vi, vd, vk, sp, si, sd, lidar, gpio, carphys, encoder_consumer, lidar_consumer,
                 network_producer, ref=0):
        super(LidarNetworkControls, self).__init__(lidar, gpio, carphys, encoder_consumer,
                                                   lidar_consumer, network_producer)
        self.velocity_P = vp
        self.velocity_I = vi
        self.velocity_D = vd
        self.velocity_Kp = vk

        self.velocity_pid_list = []  # add tuple of (pid_val,time) for integration
        self.velocity_pid_length = 20
        self.velocity_pos_ref = 200  # millimeters (mm) reference position

        self.velocity_output_clamp = (-1, 4)  # clamps output between these two values
        self.velocity_output_scaling = 1/100

        self.steering_P = sp
        self.steering_I = si
        self.steering_D = sd

        self.steering_pid_list = []  # add tuple of (pid_val,time) for integration
        self.steering_pid_length = 20

        self.steering_output_clamp = (-10, 10)  # clamps output between these two values
        self.steering_output_scaling = 1/100

        self.last_steering = 0

        if ref == 0:
            print("getting lidar data")
            try:
                self.get_lidar_data()
                print("Got Lidar Data")
            except KeyboardInterrupt as e:
                raise e
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
        packet = self.network_producer.get_packet()
        # if packet == -1:
        leader_speed = packet.speed
        leader_steering = packet.steering
        leader_throttle = packet.throttle
        v_error = self.find_velocity_error(target_velocity=leader_speed)
        d_error = self.find_distance_error(d_ref)
        s_error = self.find_steering_error(speed)

        return v_error, d_error, s_error

    def velocity_pid_controller(self, pid_input):
        t = time.time()
        self.velocity_pid_list.append((pid_input, t))

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
        for x,(pid,t) in enumerate(pid_list[:-1]):    # reiman sum of distance between vehicles
            sum += pid * (t - pid_list[x+1][1])   # calculate delta_time * pid val

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
    def convert_pid(self, pid_val, output_scaling, output_clamp):
        val = output_scaling*pid_val

        if val > output_clamp[1]:
            return output_clamp[1]
        elif val < output_clamp[0]:
            return output_clamp[0]
        else:
            return val


class Smart_Networking_Controls(Controls):
    def __init__(self, lidar, gpio, encoder):
        super(Smart_Networking_Controls, self).__init__(lidar, gpio, encoder)    # runs init of superclass


    """
    """
    def get_errors(self):
        v_error = self.find_velocity_error()
        d_error = self.find_distance_error()
        s_error = self.find_steering_error()

        return v_error, d_error, s_error
