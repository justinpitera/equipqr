"""
src/enums.py - This file contains various enums used throughout the api.

Date: November 24, 2024

Authors:
    Justin N. Pitera (justinpitera@gmail.com)
"""

# Standard
from enum import Enum


class CrewMemberPositionEnum(str, Enum):
    """Enum to describe crew member positions."""
    GROUND   = "Ground"
    MECHANIC = "Mechanic"
    MANAGEMENT = "Management"