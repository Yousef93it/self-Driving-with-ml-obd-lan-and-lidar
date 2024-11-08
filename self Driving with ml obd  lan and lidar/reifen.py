from gpiozero import Motor
from time import sleep
import os

class Robot:
    def __init__(self, path):
        """
        Initialize the robot with motor pins and set up motor objects.
        """
        self.path = path
        # Motor pins
        self.PWM_Front_FORWARD_LEFT_PIN = 16
        self.PWM_Front_REVERSE_LEFT_PIN = 26
        self.PWM_Front_FORWARD_RIGHT_PIN = 6
        self.PWM_Front_REVERSE_RIGHT_PIN = 5
        self.PWM_Back_FORWARD_LEFT_PIN = 27
        self.PWM_Back_REVERSE_LEFT_PIN = 17
        self.PWM_Back_FORWARD_RIGHT_PIN = 23
        self.PWM_Back_REVERSE_RIGHT_PIN = 22

        # Motor setup
        self.left_motor_front = Motor(forward=self.PWM_Front_FORWARD_LEFT_PIN, backward=self.PWM_Front_REVERSE_LEFT_PIN, pwm=True)
        self.right_motor_front = Motor(forward=self.PWM_Front_FORWARD_RIGHT_PIN, backward=self.PWM_Front_REVERSE_RIGHT_PIN, pwm=True)
        self.left_motor_back = Motor(forward=self.PWM_Back_FORWARD_LEFT_PIN, backward=self.PWM_Back_REVERSE_LEFT_PIN, pwm=True)
        self.right_motor_back = Motor(forward=self.PWM_Back_FORWARD_RIGHT_PIN, backward=self.PWM_Back_REVERSE_RIGHT_PIN, pwm=True)

    def set_speed(self, left_speed_front, right_speed_front, left_speed_back, right_speed_back):
        """
        Set the speed of each motor. Speed values should be between -1 and 1.
        """
        self.left_motor_front.value = left_speed_front
        self.right_motor_front.value = right_speed_front
        self.left_motor_back.value = left_speed_back
        self.right_motor_back.value = right_speed_back

    def all_stop(self):
        """
        Stop all motors by setting their speeds to zero.
        """
        self.left_motor_front.stop()
        self.right_motor_front.stop()
        self.left_motor_back.stop()
        self.right_motor_back.stop()

    def clamp(self, n, minn, maxn):
        """
        Clamp a value n between a minimum and maximum range.
        """
        return max(min(maxn, n), minn)

    def log_movement(self, turn, right_speed, left_speed):
        """
        Log the turn and speed values for debugging.
        """
        dPath = os.path.join(self.path, 'selfDriving/data/output.txt')
        with open(dPath, 'a') as file:
            file.write(f'turn: {turn}, right_speed: {right_speed}, left_speed: {left_speed}\n')

    def move_t(self, speed=0.5, turn=0, duration=0):
        """
        Move the robot for a specified duration with the given speed and turn values.
        """
        turn *= 0.4
        left_speed = self.clamp(speed * (1 + turn), -1, 1)
        right_speed = self.clamp(speed * (1 - turn), -1, 1)
        self.log_movement(turn, right_speed, left_speed)
        self.set_speed(left_speed, right_speed, left_speed, right_speed)
        sleep(duration)

    def move(self, speed=0.5, turn=0, duration=0):
        """
        Move the robot with a specified speed and turn for a given duration.
        """
        turn *= 0.7
        left_speed = self.clamp(speed + turn, -1, 1)
        right_speed = self.clamp(speed - turn, -1, 1)
        print(f'left_speed {left_speed}, right_speed {right_speed}, Time {duration}')
        self.log_movement(turn, right_speed, left_speed)
        self.set_speed(left_speed, right_speed, left_speed, right_speed)
        sleep(duration)

if __name__ == "__main__":
    PATH = os.getcwd()
    reifen = Robot(PATH)
    try:
        reifen.move(speed=0.9, turn=-0.9, duration=5)
        reifen.all_stop()
        sleep(2)
        reifen.move(speed=0.9, turn=0.9, duration=3)
    except KeyboardInterrupt:
        reifen.all_stop()
