# (desired_velocity (m/s), desired_steering (pwm signal), time (secs))
from debug_tools import print_verbose
from timing import *

class PathPlanner:
    """
        Responsible for executing a path that is predefined by the user. Currently just uses time
        to determine how long to run for
    """

    _print_debugs = True

    def __init__(self, path_list=None):
        if path_list is None:
            msg = f"PathPlanner: the path provided is {path_list}, should be an iterable of tuples " \
                  f"that follow (desired_velocity (m/s), desired_steering (pwm signal), time (secs))"
            print_verbose(msg, PathPlanner._print_debugs)
        self.path = path_list
        self.current_commanded_entry = None
        self.path_index = 0
        self.path_end_index = len(self.path) - 1
        self.start_time = None

    def get_next_command(self):
        """
        Gets the next state that we must try to achieve by looking at the change in time
        :return: A tuple that has (desired_velocity (m/s), desired_steering (pwm signal), time (secs))
        """
        if self.current_commanded_entry is None:
            self.start_time = get_current_time()
            self.current_commanded_entry = self.path[0]
        else:
            desired_velocity, desired_steering, time_s = self.current_commanded_entry
            execution_time = get_current_time()
            if meas_diff(self.start_time, execution_time) >= time_s:
                if (self.path_index + 1) <= self.path_end_index:
                    self.path_index = self.path_index + 1
                    self.current_commanded_entry = self.path[self.path_index]
                    desired_velocity, desired_steering, time = self.current_commanded_entry
                    self.start_time = get_current_time()
                else:
                    self.path_index = -1
                    self.current_commanded_entry = (0, 0, 1)
        return self.current_commanded_entry

    def set_path(self, path_list):
        """
        Assigns the path
        :param path_list: consists of entries in an interable like this
        (desired_velocity (m/s), desired_steering (pwm signal), time (secs)
        :return: None
        """
        if path_list is None:
            msg = f"PathPlanner: the path provided is {path_list}, should be an iterable of tuples " \
                  f"that follow (desired_velocity (m/s), desired_steering (pwm signal), time (secs))"
        # TODO Check that the path values are correct
        self.path = path_list

    def get_path(self):
        """
        :return: a path that consists of entries in an interable like this
        (desired_velocity (m/s), desired_steering (pwm signal), time (secs)
        """
        return self.path_list

    def is_path_done(self):
        """
        Checks to see if the path is finished
        :return: bool, true if done, otherwise false
        """
        if self.path_index == -1:
            return True
        return False

<<<<<<< HEAD
<<<<<<< HEAD

=======
# Meant for testing PathPlanner class
>>>>>>> 26db94fd9596351ce327461e8fe230ffdc176cf2
=======
# Meant for testing PathPlanner class
>>>>>>> 065a59fa5602d65eea08f7df1dcdd6fe8f1035ac
# if __name__ == "__main__":
#     path1 = [(45, 1, 1), (22, 1, 2), (33, 1, 3)]
#     pp = PathPlanner(path1)
#     while not pp.is_path_done():
#         desired_velocity, desired_steering, time_ss = pp.get_next_command()
#         msg = f"desired_velocity: {desired_velocity}m/s, desired_steering: {desired_steering}, time_s: {time_ss}"
#         print_verbose(msg, True)
#     print_verbose("Done!", True)
