import time
import Sensors

class ThrottleController():
    def __init__(self, p = 1, i = 1, d = 1, k = 1, sensors, motor):
        self.P = p
        self.I = i
        self.D = d
        self.Kp = k
        self.pwm_scale =  1000  #pulse width(ms)/speed(m/s)
        self._pid_list = [] #add touple of (pid_val,time) for integration
        self._pid_length = 20
        self.sensors = sensors  #object that interacts with the sensors
        self.motor = motor  #object that interacts and commands motor
        self.pos_ref = 20 #cm reference position
        self.operational_sensors = (True, True, True) #Encoder , lidar, comms at first assume all true

    def control_loop(self):
        self.operational_sensors = self.sensors.status
        if all(self.operational_sensors):   #determine mode of sensor collection

        velocity = get_velocity_somewhere() #pseudo code
        positional_error = get_positional_error()

        pid_input = positional_error * self.Kp + velocity
        pid_output = self.pid_controller(pid_input)
        pulse_width = self.pid_to_pwm(pid_output)
        self.motor.set_motor_to(pulse_width)

    def update_ref(self):
        self.pos_ref = get_comm_ref() #pseudocode


    def get_positional_error(self):


        if()
        distance = get_lead_car_delta_distance() #pseudo code from lidar


        return perror

    """Following methods are for PID controller"""
    def pid_controller(pid_input):
        time = time.time()
        _pid_list.append((pid_input,time))
        if len(_pid_list) > self._pid_length:
            del _pid_list[0]

        pid_val = self.proportional(pid_input) +
                  self.integral() +
                  self.derivative()

        return pid_val

    """find proportional value of PID"""
    def proportional(self, pid_input):
        p_val = pid_input * self.P
        return p_val

    """find integral value of PID"""
    def integral(self):
        if not self._pid_list:
            return 0

        modifier = (1/self.I)
        sum = 0
"""change taking from wrong side"""
        for x,(pid,t) in enumerate(self._pid_list):    #reiman sum of distance between vehicles
            sum += pid * (t - self._pid_list[x][1])   #calculate deltat * pid val

        i_val = sum * modifier
        return i_val

    """find derivative value of PID from communications and/or lidar"""
    def derivative(self):
        if not self._pid_list:
            return 0
"""change taking from wrong side"""
        d_val = (self._pid_list[-1][0]-self._pid_list[-2][0])
                /(self._pid_list[-1][1]-self._pid_list[-2][1])
        d_val =* self.D

        return d_val

    """convert value from PID controller to pwm"""
    def pid_to_pwm(self,pid_val):   #max val should be 2000 and min val is 1000

        return pwm_signal


    def get_lead_car_delta_distance(self):



class SteeringController():
    def __init__(self, p = 1, i = 1, d = 1, k = 1, sensors, servo):
        self.P = p
        self.I = i
        self.D = d
        self.Kp = k
        self.pwm_scale =  1000  #pulse width(ms)/speed(m/s)
        self._pid_list = [] #add touple of (pid_val,time) for integration
        self._pid_length = 20
        self.sensors = sensors  #object that interacts with the sensors
        self.servo = servo      #object that interacts and commands motor
        self._steering_angle = 0    #degrees from straight ahead
        self._reference_angle = 0   #degrees from straight ahead
        self.operational_sensors = (True, True, True) #Encoder , lidar, comms
        self.path = [] #((location),time) origin is x=0,y=0 y+ is forward right is +x

    def control_loop(self):
        self.operational_sensors = self.sensors.status
        if all(self.operational_sensors):   #determine mode of sensor collection

        velocity = get_velocity_somewhere() #pseudo code
        positional_error = get_positional_error()

        steering_error = self._reference_angle - self._steering_angle   #steering error
        pid_input = positional_error * self.Kp + steering_error

        pid_output = self.pid_controller(pid_input)
        self._steering_angle = self.pid_to_angle(pid_output)
        self.servo.set_servo_to(self._steering_angle)

    """Translate then add new point"""
    def update_path(self):
        if all(self.operational_sensors): #all sensors active
            now = time.time()
            delta_t = self.path[-1][1] - now
            my_movement =
            translation = my_movement + delta_leader_movement

            for :
                return
        elif self.operational_sensors[0]:   #encoder not working
            do stuff
        elif self.operational_sensors[1]: #lidar not working
        do stuff
        elif self.operational_sensors[3]: #coms not working
        do stuff



    def get_ref_angle(self):
        self._reference_angle

    def get_positional_error(self):


    """Following methods are for PID controller"""
    def pid_controller(pid_input):
        time = time.time()
        _pid_list.append((pid_input,time))
        if len(_pid_list) > self._pid_length:
            del _pid_list[0]

        pid_val = self.proportional(pid_input) +
                  self.integral() +
                  self.derivative()

        return pid_val

    """find proportional value of PID"""
    def proportional(self, pid_input):
        p_val = pid_input * self.P
        return p_val

    """find integral value of PID"""
    def integral(self):
        if not self._pid_list:
            return 0

        modifier = (1/self.I)
        sum = 0

        for x,(pid,t) in self._pid_list:    #reiman sum of distance between vehicles
            sum += pid * (t - self._pid_list[x][1])   #calculate deltat * pid val

        i_val = sum * modifier
        return i_val

    """find derivative value of PID from communications and/or lidar"""
    def derivative(self):
        if not self._pid_list:
            return 0

        d_val = (self._pid_list[-1][0]-self._pid_list[-2][0])
                /(self._pid_list[-1][1]-self._pid_list[-2][1])
        d_val =* self.D

        return d_val

    """convert value from PID controller to angle for servo """
    def pid_to_angle(self,pid_val):
        min_val = self.servo.min_angle
        max_val = self.servo.max_angle


class CarPhysics:
    """Car config here"""
    s = 16   #distance from center of front wheels
    j = 12   #distance between king pins
    r0 = 1  #distance from pin to center of wheel
    Ijt = 8 #front to back axel

    """calculations made with equations from
    https://www.engineersedge.com/calculators/
    vehicle_turning_circle_design_14730.htm"""
    @staticmethod
    def
