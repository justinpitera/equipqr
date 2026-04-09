from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class HealthStatusRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class HealthStatusResponse(_message.Message):
    __slots__ = ()
    VERSION_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    version: str
    status: str
    def __init__(self, version: _Optional[str] = ..., status: _Optional[str] = ...) -> None: ...

class GSEDetailsRequest(_message.Message):
    __slots__ = ()
    GSE_ID_FIELD_NUMBER: _ClassVar[int]
    gse_id: str
    def __init__(self, gse_id: _Optional[str] = ...) -> None: ...

class GSEDetailsResponse(_message.Message):
    __slots__ = ()
    GSE_ID_FIELD_NUMBER: _ClassVar[int]
    OLD_GSE_ID_FIELD_NUMBER: _ClassVar[int]
    GSE_TYPE_FIELD_NUMBER: _ClassVar[int]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    MANUFACTURER_FIELD_NUMBER: _ClassVar[int]
    LOCATION_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    ISSUE_COUNT_FIELD_NUMBER: _ClassVar[int]
    TYPE_OF_FUEL_FIELD_NUMBER: _ClassVar[int]
    IN_USE_FIELD_NUMBER: _ClassVar[int]
    MOST_RECENT_ISSUE_FIELD_NUMBER: _ClassVar[int]
    LIFT_INSPECTION_EXPIRES_FIELD_NUMBER: _ClassVar[int]
    LATEST_SERVICE_CHASSI_FIELD_NUMBER: _ClassVar[int]
    LATEST_SERVICE_UNIT_FIELD_NUMBER: _ClassVar[int]
    CAPACITY_FIELD_NUMBER: _ClassVar[int]
    DETAILS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    gse_id: str
    old_gse_id: str
    gse_type: str
    model: str
    manufacturer: str
    location: str
    status: str
    issue_count: int
    type_of_fuel: str
    in_use: bool
    most_recent_issue: MostRecentIssueResponse
    lift_inspection_expires: str
    latest_service_chassi: str
    latest_service_unit: str
    capacity: float
    details: str
    error: str
    def __init__(self, gse_id: _Optional[str] = ..., old_gse_id: _Optional[str] = ..., gse_type: _Optional[str] = ..., model: _Optional[str] = ..., manufacturer: _Optional[str] = ..., location: _Optional[str] = ..., status: _Optional[str] = ..., issue_count: _Optional[int] = ..., type_of_fuel: _Optional[str] = ..., in_use: _Optional[bool] = ..., most_recent_issue: _Optional[_Union[MostRecentIssueResponse, _Mapping]] = ..., lift_inspection_expires: _Optional[str] = ..., latest_service_chassi: _Optional[str] = ..., latest_service_unit: _Optional[str] = ..., capacity: _Optional[float] = ..., details: _Optional[str] = ..., error: _Optional[str] = ...) -> None: ...

class ListGSEReponse(_message.Message):
    __slots__ = ()
    GSE_ID_FIELD_NUMBER: _ClassVar[int]
    gse_id: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, gse_id: _Optional[_Iterable[str]] = ...) -> None: ...

class MostRecentIssueResponse(_message.Message):
    __slots__ = ()
    ID_FIELD_NUMBER: _ClassVar[int]
    GSE_ID_FIELD_NUMBER: _ClassVar[int]
    ISSUE_DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    REPORTED_AT_FIELD_NUMBER: _ClassVar[int]
    ATTACHMENTS_FIELD_NUMBER: _ClassVar[int]
    id: str
    gse_id: str
    issue_description: str
    reported_at: str
    attachments: str
    def __init__(self, id: _Optional[str] = ..., gse_id: _Optional[str] = ..., issue_description: _Optional[str] = ..., reported_at: _Optional[str] = ..., attachments: _Optional[str] = ...) -> None: ...

class SubmitIssueRequest(_message.Message):
    __slots__ = ()
    GSE_ID_FIELD_NUMBER: _ClassVar[int]
    WORKER_ID_FIELD_NUMBER: _ClassVar[int]
    ISSUE_DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    IS_OPERABLE_FIELD_NUMBER: _ClassVar[int]
    ATTACHMENTS_FIELD_NUMBER: _ClassVar[int]
    GATE_TYPE_FIELD_NUMBER: _ClassVar[int]
    GATE_NAME_FIELD_NUMBER: _ClassVar[int]
    gse_id: str
    worker_id: str
    issue_description: str
    is_operable: str
    attachments: _containers.RepeatedScalarFieldContainer[bytes]
    gate_type: str
    gate_name: str
    def __init__(self, gse_id: _Optional[str] = ..., worker_id: _Optional[str] = ..., issue_description: _Optional[str] = ..., is_operable: _Optional[str] = ..., attachments: _Optional[_Iterable[bytes]] = ..., gate_type: _Optional[str] = ..., gate_name: _Optional[str] = ...) -> None: ...

class SubmitIssueResponse(_message.Message):
    __slots__ = ()
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class FetchIssuesRequest(_message.Message):
    __slots__ = ()
    PAGE_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    page: int
    page_size: int
    def __init__(self, page: _Optional[int] = ..., page_size: _Optional[int] = ...) -> None: ...

class FetchIssuesResponse(_message.Message):
    __slots__ = ()
    DATA_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    data: _containers.RepeatedCompositeFieldContainer[Issue]
    page: int
    page_size: int
    total: int
    def __init__(self, data: _Optional[_Iterable[_Union[Issue, _Mapping]]] = ..., page: _Optional[int] = ..., page_size: _Optional[int] = ..., total: _Optional[int] = ...) -> None: ...

class Issue(_message.Message):
    __slots__ = ()
    ID_FIELD_NUMBER: _ClassVar[int]
    GSE_ID_FIELD_NUMBER: _ClassVar[int]
    ISSUE_DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    ESTIMATED_TIME_FIELD_NUMBER: _ClassVar[int]
    REPORTED_AT_FIELD_NUMBER: _ClassVar[int]
    REPORTED_BY_FIELD_NUMBER: _ClassVar[int]
    PROGRESS_FIELD_NUMBER: _ClassVar[int]
    ATTACHMENTS_FIELD_NUMBER: _ClassVar[int]
    id: str
    gse_id: str
    issue_description: str
    estimated_time: str
    reported_at: str
    reported_by: str
    progress: str
    attachments: _containers.RepeatedCompositeFieldContainer[Attachment]
    def __init__(self, id: _Optional[str] = ..., gse_id: _Optional[str] = ..., issue_description: _Optional[str] = ..., estimated_time: _Optional[str] = ..., reported_at: _Optional[str] = ..., reported_by: _Optional[str] = ..., progress: _Optional[str] = ..., attachments: _Optional[_Iterable[_Union[Attachment, _Mapping]]] = ...) -> None: ...

class Attachment(_message.Message):
    __slots__ = ()
    ID_FIELD_NUMBER: _ClassVar[int]
    FILE_TYPE_FIELD_NUMBER: _ClassVar[int]
    UPLOADED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    file_type: str
    uploaded_at: str
    def __init__(self, id: _Optional[str] = ..., file_type: _Optional[str] = ..., uploaded_at: _Optional[str] = ...) -> None: ...

class SetLanguageRequest(_message.Message):
    __slots__ = ()
    LANGUAGE_FIELD_NUMBER: _ClassVar[int]
    language: str
    def __init__(self, language: _Optional[str] = ...) -> None: ...

class SetLanguageResponse(_message.Message):
    __slots__ = ()
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    token: str
    def __init__(self, token: _Optional[str] = ...) -> None: ...

class LoginRequest(_message.Message):
    __slots__ = ()
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    TENANT_SLUG_FIELD_NUMBER: _ClassVar[int]
    email: str
    tenant_slug: str
    def __init__(self, email: _Optional[str] = ..., tenant_slug: _Optional[str] = ...) -> None: ...

class LoginResponse(_message.Message):
    __slots__ = ()
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    TENANT_NAME_FIELD_NUMBER: _ClassVar[int]
    message: str
    tenant_name: str
    def __init__(self, message: _Optional[str] = ..., tenant_name: _Optional[str] = ...) -> None: ...

class DeleteIssuesRequest(_message.Message):
    __slots__ = ()
    IDS_FIELD_NUMBER: _ClassVar[int]
    ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, ids: _Optional[_Iterable[str]] = ...) -> None: ...

class DeleteIssuesResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class LogoutRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class LogoutResponse(_message.Message):
    __slots__ = ()
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    message: str
    def __init__(self, message: _Optional[str] = ...) -> None: ...

class FetchGatesRequest(_message.Message):
    __slots__ = ()
    ICAO_CODE_FIELD_NUMBER: _ClassVar[int]
    icao_code: str
    def __init__(self, icao_code: _Optional[str] = ...) -> None: ...

class FetchGatesResponse(_message.Message):
    __slots__ = ()
    GATES_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    gates: _containers.RepeatedCompositeFieldContainer[Gate]
    error: str
    def __init__(self, gates: _Optional[_Iterable[_Union[Gate, _Mapping]]] = ..., error: _Optional[str] = ...) -> None: ...

class Gate(_message.Message):
    __slots__ = ()
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    type: str
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., type: _Optional[str] = ...) -> None: ...

class IssueComment(_message.Message):
    __slots__ = ()
    ISSUE_ID_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    COMMENT_BY_FIELD_NUMBER: _ClassVar[int]
    issue_id: str
    comment: str
    comment_by: str
    def __init__(self, issue_id: _Optional[str] = ..., comment: _Optional[str] = ..., comment_by: _Optional[str] = ...) -> None: ...

class IssueCommentResponse(_message.Message):
    __slots__ = ()
    ID_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    id: str
    error: str
    def __init__(self, id: _Optional[str] = ..., error: _Optional[str] = ...) -> None: ...

class UploadFieldImage(_message.Message):
    __slots__ = ()
    IMAGE_FIELD_NUMBER: _ClassVar[int]
    GSE_ID_FIELD_NUMBER: _ClassVar[int]
    image: bytes
    gse_id: str
    def __init__(self, image: _Optional[bytes] = ..., gse_id: _Optional[str] = ...) -> None: ...

class UploadFieldImageResponse(_message.Message):
    __slots__ = ()
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: str
    error: str
    def __init__(self, success: _Optional[str] = ..., error: _Optional[str] = ...) -> None: ...

class FieldImageRequest(_message.Message):
    __slots__ = ()
    GSE_ID_FIELD_NUMBER: _ClassVar[int]
    gse_id: str
    def __init__(self, gse_id: _Optional[str] = ...) -> None: ...

class FieldImageResponse(_message.Message):
    __slots__ = ()
    IMAGE_FIELD_NUMBER: _ClassVar[int]
    DELETE_SUCCESS_FIELD_NUMBER: _ClassVar[int]
    image: bytes
    delete_success: bool
    def __init__(self, image: _Optional[bytes] = ..., delete_success: _Optional[bool] = ...) -> None: ...

class EditIssueRequest(_message.Message):
    __slots__ = ()
    ISSUE_ID_FIELD_NUMBER: _ClassVar[int]
    PROGRESS_FIELD_NUMBER: _ClassVar[int]
    ESTIMATED_TIME_FIELD_NUMBER: _ClassVar[int]
    issue_id: str
    progress: str
    estimated_time: str
    def __init__(self, issue_id: _Optional[str] = ..., progress: _Optional[str] = ..., estimated_time: _Optional[str] = ...) -> None: ...

class EditIssueResponse(_message.Message):
    __slots__ = ()
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    def __init__(self, success: _Optional[bool] = ..., message: _Optional[str] = ...) -> None: ...
