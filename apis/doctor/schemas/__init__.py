from .doctor import (
    DoctorInfo,
    DoctorListResponse,
    DoctorCreateRequest,
    DoctorUpdateRequest,
)
from .schedule import (
    SchedulingInfo,
    ScheduleCreateRequest,
    ScheduleUpdateRequest,
    ScheduleListResponse,
)
from .appointment import (
    AppointmentRequest,
    AppointmentResponse,
    AppointmentInfo,
    AppointmentUpdateRequest,
    AppointmentListResponse,
)

__all__ = [
    # Doctor schemas
    "DoctorInfo",
    "DoctorListResponse",
    "DoctorCreateRequest",
    "DoctorUpdateRequest",
    # Schedule schemas
    "SchedulingInfo",
    "ScheduleCreateRequest",
    "ScheduleUpdateRequest",
    "ScheduleListResponse",
    # Appointment schemas
    "AppointmentRequest",
    "AppointmentResponse",
    "AppointmentInfo",
    "AppointmentUpdateRequest",
    "AppointmentListResponse",
]
