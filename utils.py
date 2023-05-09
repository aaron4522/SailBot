import logging


def singleton(cls):
    """A decorator which prevents duplicate classes from being created.
    Useful for physical objects where only one exists.
        - Import, then invoke use @singleton before class definition"""
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


class Pivotable:
    """
    Any object that moves about an axis, ex. servos, rudder, sail

    Attributes:
        - name (str):  the name of the object (used for logging)
        - min_angle (int): the minimum allowed angle
        - max_angle (int): the maximum allowed angle
        - default_angle (int): the baseline angle (usually center)
        - angle (float): the current angle of the object
        - fget (func): a function which gets the angle
        - fset (func): a function which moves the angle
            - basic error checking already done

    Functions:
        - reset(): returns angle to default angle
    """

    def __init__(self, name, min_angle, max_angle, default_angle, fset, fget):
        self.name = name
        self.min_angle = min_angle
        self.max_angle = max_angle
        self.default_angle = default_angle
        self.fget = fget
        self.fset = fset

        logging.info(f"Initializing {self.name}")
        self._angle = default_angle

    def __str__(self):
        return f"{self.name} at {self.angle} degrees"

    @property
    def angle(self):
        return self.fget()

    @angle.setter
    def angle(self, angle_val):
        if angle_val < self.min_angle:
            angle_val = self.min_angle
        elif angle_val > self.max_angle:
            angle_val = self.max_angle
        logging.debug(f"Moving {self.name} to {angle_val}")
        self.fset()

    def reset(self):
        self.angle = self.default_angle
