"""
Tests all necessary sensors and functionality of the boat
"""
import sys

import constants as c
import camera

def test_capture(detect):
    """Takes a picture"""
    cam = camera.Camera()

def test_servos():
    """Moves servos"""
    
def test_survey(detect):
    
        
def test_gps():
    """A"""

def test_():
    """A"""
        
def test(func):
    """Runs a test with proper error handling"""
    print(f"Running tests")
    try:
        pass
    except Exception as e:
        print(f"Failed test_camera")
        print(f"Exception raised: {e}")
    else:
        print(f"Passed ")

if __name__ == "__main__":
    argsv = sys.argv[1]
    test(test_gps)
    