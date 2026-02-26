#
# Copyright (c) 2022, Neptune Labs Sp. z o.o.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
__all__ = ["OperationApiObjectConverter", "encode_float_for_json"]

import math
import struct
from typing import Union

from minfx.neptune_v2.common.exceptions import InternalClientError

# Standard NaN bit pattern (quiet NaN with no payload)
_STANDARD_NAN_BITS = 0x7FF8_0000_0000_0000
from minfx.neptune_v2.internal.operation import (
    AddStrings,
    AssignArtifact,
    AssignBool,
    AssignDatetime,
    AssignFloat,
    AssignInt,
    AssignString,
    ClearArtifact,
    ClearFloatLog,
    ClearImageLog,
    ClearStringLog,
    ClearStringSet,
    ConfigFloatSeries,
    CopyAttribute,
    DeleteAttribute,
    DeleteFiles,
    LogFloats,
    LogImages,
    LogStrings,
    Operation,
    RemoveStrings,
    TrackFilesToArtifact,
    UploadFile,
    UploadFileContent,
    UploadFileSet,
)
from minfx.neptune_v2.internal.operation_visitor import (
    OperationVisitor,
    Ret,
)


def _float_to_bits(value: float) -> int:
    """Convert float to its IEEE 754 bit representation."""
    return struct.unpack(">Q", struct.pack(">d", value))[0]


def encode_float_for_json(value: float) -> Union[float, str]:
    """Encode special float values as strings for JSON serialization.

    Standard JSON does not support NaN, Infinity, or -Infinity as number values.
    This function encodes these special IEEE 754 values as strings that can be
    decoded by the backend.

    Formats:
        - "NaN" - standard quiet NaN
        - "NaN(bits)" - NaN with custom bit pattern, e.g. "NaN(9221120237041090561)"
        - "PosInf" - positive infinity
        - "NegInf" - negative infinity
        - "NegZero" - negative zero (-0.0)

    Args:
        value: The float value to encode.

    Returns:
        The original float if it's a regular number, or a string representation
        for special values.
    """
    if math.isnan(value):
        bits = _float_to_bits(value)
        if bits == _STANDARD_NAN_BITS:
            return "NaN"
        return f"NaN({bits})"
    if math.isinf(value):
        return "PosInf" if value > 0 else "NegInf"
    if value == 0.0 and math.copysign(1.0, value) < 0:
        return "NegZero"
    return value


def encode_optional_float_for_json(value: Union[float, None]) -> Union[float, str, None]:
    """Encode optional float value for JSON serialization."""
    if value is None:
        return None
    return encode_float_for_json(value)


class OperationApiObjectConverter(OperationVisitor[dict]):
    def convert(self, op: Operation) -> dict:
        return op.accept(self)

    def visit_assign_float(self, op: AssignFloat) -> dict:
        return {"value": encode_float_for_json(op.value)}

    def visit_assign_int(self, op: AssignInt) -> dict:
        return {"value": op.value}

    def visit_assign_bool(self, op: AssignBool) -> dict:
        return {"value": op.value}

    def visit_assign_string(self, op: AssignString) -> dict:
        return {"value": op.value}

    def visit_assign_datetime(self, op: AssignDatetime) -> Ret:
        return {"valueMilliseconds": int(1000 * op.value.timestamp())}

    def visit_assign_artifact(self, op: AssignArtifact) -> dict:
        return {"hash": op.hash}

    def visit_upload_file(self, _: UploadFile) -> dict:
        raise InternalClientError("Specialized endpoint should be used to upload file attribute")

    def visit_upload_file_content(self, _: UploadFileContent) -> dict:
        raise InternalClientError("Specialized endpoint should be used to upload file attribute")

    def visit_upload_file_set(self, op: UploadFileSet) -> Ret:
        raise InternalClientError("Specialized endpoints should be used to upload file set attribute")

    def visit_log_floats(self, op: LogFloats) -> dict:
        return {
            "entries": [
                {
                    "value": encode_float_for_json(value.value),
                    "step": encode_optional_float_for_json(value.step),
                    "timestampMilliseconds": int(value.ts * 1000),
                }
                for value in op.values
            ]
        }

    def visit_log_strings(self, op: LogStrings) -> dict:
        return {
            "entries": [
                {
                    "value": value.value,
                    "step": encode_optional_float_for_json(value.step),
                    "timestampMilliseconds": int(value.ts * 1000),
                }
                for value in op.values
            ]
        }

    def visit_log_images(self, op: LogImages) -> dict:
        return {
            "entries": [
                {
                    "value": {
                        "data": value.value.data,
                        "name": value.value.name,
                        "description": value.value.description,
                    },
                    "step": encode_optional_float_for_json(value.step),
                    "timestampMilliseconds": int(value.ts * 1000),
                }
                for value in op.values
            ]
        }

    def visit_clear_float_log(self, _: ClearFloatLog) -> dict:
        return {}

    def visit_clear_string_log(self, _: ClearStringLog) -> dict:
        return {}

    def visit_clear_image_log(self, _: ClearImageLog) -> dict:
        return {}

    def visit_config_float_series(self, op: ConfigFloatSeries) -> dict:
        return {
            "min": encode_optional_float_for_json(op.min),
            "max": encode_optional_float_for_json(op.max),
            "unit": op.unit,
        }

    def visit_add_strings(self, op: AddStrings) -> dict:
        return {"values": list(op.values)}

    def visit_remove_strings(self, op: RemoveStrings) -> dict:
        return {"values": list(op.values)}

    def visit_delete_attribute(self, _: DeleteAttribute) -> dict:
        return {}

    def visit_clear_string_set(self, _: ClearStringSet) -> dict:
        return {}

    def visit_delete_files(self, op: DeleteFiles) -> Ret:
        return {"filePaths": list(op.file_paths)}

    def visit_track_files_to_artifact(self, op: TrackFilesToArtifact) -> dict:
        raise InternalClientError("Specialized endpoint should be used to track artifact files")

    def visit_clear_artifact(self, _: ClearArtifact) -> Ret:
        return {}

    def visit_copy_attribute(self, _: CopyAttribute) -> Ret:
        raise NotImplementedError("This operation is client-side only")
