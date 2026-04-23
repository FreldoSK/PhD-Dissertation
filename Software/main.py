"""Author: Ing. Tomas Baca."""
from machine import Pin
from machine import PWM

class Engines:
    """Class for work with the engines."""

    def __init__(self,
                 right_engine_forward_pin: int = 18,
                 right_engine_reverse_pin: int = 19,
                 left_engine_forward_pin: int = 20,
                 left_engine_reverse_pin: int = 22) -> None:
        """
        Execute the constructor.

        :param right_engine_forward_pin: Pin to which is connected plus of the M1.
        :param right_engine_reverse_pin: Pin to which is connected minus of the M1.
        :param left_engine_forward_pin: Pin to which is connected plus of the M2.
        :param left_engine_reverse_pin: Pin to which is connected minus of the M2.
        :return:
        """
        self.__right_engine_forward: PWM = PWM(
            Pin(right_engine_forward_pin), freq=15000, duty_u16=0)
        self.__right_engine_reverse: PWM = PWM(
            Pin(right_engine_reverse_pin), freq=15000, duty_u16=0)
        self.__left_engine_forward: PWM = PWM(
            Pin(left_engine_forward_pin), freq=15000, duty_u16=0)
        self.__left_engine_reverse: PWM = PWM(
            Pin(left_engine_reverse_pin), freq=15000, duty_u16=0)

    @staticmethod
    def __percents_to_duty(percents: int) -> int:
        """
        Convert percents to the duty cycle.

        :param percents: percents in range 0 to 100.
        :return: duty cycle in range 0 to 65535.
        """
        value: int = int(percents * (65535 / 100))

        value = min(value, 65535)
        value = max(value, 0)

        return value

    def move_forward_right(self, percents: int) -> None:
        """
        Set the right engine to move forward based on the percent.

        :param percents: percentual speed of the movement.
        :return:
        """
        self.__right_engine_forward.duty_u16(self.__percents_to_duty(percents))
        self.__right_engine_reverse.duty_u16(self.__percents_to_duty(0))

    def move_reverse_right(self, percents: int) -> None:
        """
        Set the right engine to move reverse based on the percent.

        :param percents: percentual speed of the movement.
        :return:
        """
        self.__right_engine_forward.duty_u16(self.__percents_to_duty(0))
        self.__right_engine_reverse.duty_u16(self.__percents_to_duty(percents))

    def brake_right(self) -> None:
        """
        Brake the right engine.

        :return:
        """
        self.__right_engine_forward.duty_u16(self.__percents_to_duty(100))
        self.__right_engine_reverse.duty_u16(self.__percents_to_duty(100))

    def coast_right(self) -> None:
        """
        Let the right engine coast.

        :return:
        """
        self.__right_engine_forward.duty_u16(self.__percents_to_duty(0))
        self.__right_engine_reverse.duty_u16(self.__percents_to_duty(0))

    def move_forward_left(self, percents: int) -> None:
        """
        Set the left engine to move forward based on the percent.

        :param percents: percentual speed of the movement.
        :return:
        """
        self.__left_engine_forward.duty_u16(self.__percents_to_duty(percents))
        self.__left_engine_reverse.duty_u16(self.__percents_to_duty(0))

    def move_reverse_left(self, percents: int) -> None:
        """
        Set the left engine to move reverse based on the percent.

        :param percents: percentual speed of the movement.
        :return:
        """
        self.__left_engine_forward.duty_u16(self.__percents_to_duty(0))
        self.__left_engine_reverse.duty_u16(self.__percents_to_duty(percents))

    def brake_left(self) -> None:
        """
        Brake the left engine.

        :return:
        """
        self.__left_engine_forward.duty_u16(self.__percents_to_duty(100))
        self.__left_engine_reverse.duty_u16(self.__percents_to_duty(100))

    def coast_left(self) -> None:
        """
        Let the left engine coast.

        :return:
        """
        self.__left_engine_forward.duty_u16(self.__percents_to_duty(0))
        self.__left_engine_reverse.duty_u16(self.__percents_to_duty(0))

engines_instance: Engines = Engines()

engines_instance.move_forward_left(65)
engines_instance.move_forward_right(65)

# engines_instance.move_reverse_left(60)
# engines_instance.move_reverse_right(60)
# engines_instance.brake_right()
# engines_instance.brake_left()

