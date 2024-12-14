from enum import Enum

class CrewMemberPositionEnum(str, Enum):
    GROUND = 'Ground'
    MECHANIC = 'Mechanic'
    MANAGEMENT = 'Management'

class IssueProgressEnum(str, Enum):
    REPORTED = 'Reported'
    IN_PROGRESS = 'In Progress'
    WAITING = 'Waiting for parts'
    READY = 'Ready for pickup'
    IN_SERVICE = 'Back in service'

class LocationTypeEnum(str, Enum):
    GA = 'General Aviation (GA).'
    AIRLINE = 'Airline'
    CARGO = 'Cargo'
    NONE = 'None'
