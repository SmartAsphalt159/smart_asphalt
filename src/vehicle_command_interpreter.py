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
                command_str = f"""gi.set_motor_pwm({throttle_setting})\n"""
                command_list.append(command_str)
            elif search(vehicle_command_interpreter.pattern_steer, line):
                list_args = line.split(' ')
                steering = list_args[1]
                command_str = f"""gi.set_servo_pwm({steering})\n"""
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
        init_code = """from sensor import GPIO_Interaction\nimport time\nmotor_ch = 32\nservo_ch = 33\nenc_channel = 19\ngi = GPIO_Interaction(enc_channel, servo_ch, motor_ch)\n"""
        for command in list_commands:
            init_code = init_code + command

        # Set everything to 0 at the end
        end = """gi.set_motor_pwm(0)\ngi.set_servo_pwm(0)\nprint("Script Finished Execution!")"""
        init_code += end
        print(init_code)
        return init_code


if __name__ == "__main__":
    vehicle_command_interpreter.read_command_script('basic_script.txt')
