from pathlib import Path
from re import search, match

class vehicle_command_interpreter():
    _script_dir = Path("../vehicle_command_scripts/")
    pattern_comment = r'^#'
    pattern_throttle = r'^(throttle)(\s\d+(.?\d+)?)'
    pattern_steer = r'(steer)(\s\d+(.?\d+)?)'
    pattern_wait = r'(wait)(\s\d+(.?\d+)?)'

    @staticmethod
    def read_command_script(file_name):
        file_to_open = vehicle_command_interpreter._script_dir / file_name
        command_list = []
        with open(file_to_open) as file:
            lines_in_file = list(non_blank_line for non_blank_line in (line.strip() for line in file) if non_blank_line)
        for line in lines_in_file:
            line = str(line)
            print(line)
            print(search(vehicle_command_interpreter.pattern_throttle, line))
            if search(vehicle_command_interpreter.pattern_comment, line):
                continue
            elif search(vehicle_command_interpreter.pattern_throttle, line):
                list_args = line.split(' ')
                throttle_setting = list_args[1]
<<<<<<< HEAD
                command_str = f"""throttle_val={throttle_setting}\ngi.set_motor_pwm({throttle_setting})\nsend_node.broadcast_data(steering_val, throttle_val, 0, 0)\n"""
=======
                command_str = f"""gi.set_motor_pwm({throttle_setting})\n"""
>>>>>>> 7073bc5b851257a08b121c3cc64ed2a6fda3d1e3
                command_list.append(command_str)
            elif search(vehicle_command_interpreter.pattern_steer, line):
                list_args = line.split(' ')
                steering = list_args[1]
<<<<<<< HEAD
                command_str = f"""steering_val={steering}\ngi.set_servo_pwm({steering})\nsend_node.broadcast_data(steering_val, throttle_val, 0, 0)\n"""
=======
                command_str = f"""gi.set_servo_pwm({steering})\n"""
>>>>>>> 7073bc5b851257a08b121c3cc64ed2a6fda3d1e3
                command_list.append(command_str)
            elif search(vehicle_command_interpreter.pattern_wait, line):
                list_args = line.split(' ')
                time = list_args[1]
                command_str = f"""time.sleep({time})\n"""
                command_list.append(command_str)
            else:
                raise ValueError(f'Unsupported phrase encountered in {file_name}: {line}')
        print(command_list)
        commands = vehicle_command_interpreter.generate_command_script(command_list)
        exec(commands)

    @staticmethod
    def generate_command_script(list_commands):
<<<<<<< HEAD
        init_code = """from sensor import GPIO_Interaction\nimport time\nfrom network import recv_network as rn, send_network as sn\nmotor_ch = 32\nservo_ch = 33\nenc_channel = 19\ngi = GPIO_Interaction(enc_channel, servo_ch, motor_ch)\n"""
        network_init_lead_vehicle = """steering_val = 0\nthrottle_val = 0\nport_index_send = 1\nsend_node = sn(port_index_send)\n"""
        init_code += network_init_lead_vehicle
=======
        init_code = """from sensor import GPIO_Interaction\nimport time\nmotor_ch = 32\nservo_ch = 33\nenc_channel = 19\ngi = GPIO_Interaction(enc_channel, servo_ch, motor_ch)\n"""
>>>>>>> 7073bc5b851257a08b121c3cc64ed2a6fda3d1e3
        for command in list_commands:
            init_code = init_code + command

        # Set everything to 0 at the end
        end = """gi.set_motor_pwm(0)\ngi.set_servo_pwm(0)\nprint("Script Finished Execution!")"""
        init_code += end
        print(init_code)
        return init_code


if __name__ == "__main__":
    vehicle_command_interpreter.read_command_script('basic_script.txt')
