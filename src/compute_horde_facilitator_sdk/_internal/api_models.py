import enum
from typing import Annotated, Literal, NotRequired

import annotated_types
from typing_extensions import TypedDict

JOB_STATUS_TYPE = Literal["Failed", "Rejected", "Sent", "Accepted", "Completed"]


def is_in_progress(status: JOB_STATUS_TYPE) -> bool:
    return status in ("Sent", "Accepted")


class JobState(TypedDict, total=False):
    uuid: str
    status: JOB_STATUS_TYPE
    stdout: str
    output_download_url: str


class JobFeedback(TypedDict):
    """
    Represents feedback data for a job, detailing the job's execution and results.

    :Attributes:
        - **job_uuid**: job UUID
        - **result_correctness**
            The correctness of the job's result expressed as a float between 0.0 and 1.0.
            - 0.0 indicates 0% correctness (completely incorrect).
            - 1.0 indicates 100% correctness (completely correct).
        - **expected_duration** (*NotRequired[float]*):
            An optional field indicating the expected time in seconds for the job to complete.
            This can highlight if the job's execution was slower than expected, suggesting performance issues.
    """

    result_correctness: Annotated[float, annotated_types.Interval(ge=0.0, le=1.0)]
    expected_duration: NotRequired[Annotated[float, annotated_types.Gt(0.0)] | None]


class OutputUploadType(str, enum.Enum):
    single_file_post = "single_file_post"
    single_file_put = "single_file_put"

    def __str__(self):
        return str.__str__(self)


class SingleFilePostUpload(TypedDict):
    output_upload_type: Literal[OutputUploadType.single_file_post]
    url: str
    form_fields: dict[str, str] | None
    relative_path: str
    signed_headers: dict[str, str] | None


class SingleFilePutUpload(TypedDict):
    output_upload_type: Literal[OutputUploadType.single_file_put]
    url: str
    relative_path: str
    signed_headers: dict[str, str] | None


SingleFileUpload = SingleFilePostUpload | SingleFilePutUpload


class VolumeType(str, enum.Enum):
    zip_url = "zip_url"
    single_file = "single_file"

    def __str__(self):
        return str.__str__(self)


class ZipUrlVolume(TypedDict):
    volume_type: Literal[VolumeType.zip_url]
    contents: str
    relative_path: str | None


class SingleFileVolume(TypedDict):
    volume_type: Literal[VolumeType.single_file]
    url: str
    relative_path: str


Volume = ZipUrlVolume | SingleFileVolume
