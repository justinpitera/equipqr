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
    GROUND   = "employee"
    MECHANIC = "mechanic"
    MANAGEMENT = "master"
    
class IssueProgressEnum(str, Enum):
    """Enum to describe issue progress."""
    REPORTED   = "Reported"
    IN_PROGRESS = "In Progress"
    WAITING = "Waiting for parts"
    READY = "Ready for pickup"
    IN_SERVICE = "Back in service"

class LocationTypeEnum(str, Enum):
    """Enum to describe location types."""
    GA   = "General Aviation (GA)."
    AIRLINE = "Airline"
    CARGO = "Cargo"
    NONE = "None"
