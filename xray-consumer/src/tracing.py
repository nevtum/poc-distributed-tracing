from typing import Union

from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core.models.trace_header import TraceHeader
from aws_xray_sdk.core.context import Context
from typing import Any

# Replace LambdaContext with brand new context to allow put_segment in a lambda.
# It does however leave the side effect where duplicate traces are created
# because of AWS lambda
xray_recorder.configure(context=Context())


def extract_trace_header(record) -> Union[TraceHeader, None]:
    trace_header_str = record.get("attributes", {}).get("AWSTraceHeader", None)
    if trace_header_str:
        return TraceHeader.from_header_str(trace_header_str)


class SqsLambdaSegmentContextManager:
    def __init__(self, recorder: Any, segment_name: str, trace_header: TraceHeader):
        self.recorder = recorder
        self.segment_name = segment_name
        self.trace_header = trace_header

    def __enter__(self):
        segment = self.recorder.begin_segment(
            name=self.segment_name,
            traceid=self.trace_header.root,
            parent_id=self.trace_header.parent,
            sampling=self.trace_header.sampled,
        )

        # Modify origin to display lambda icon in xray console
        segment.origin = "AWS::Lambda::Function"
        return segment

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.recorder.end_segment()


def segment_handle_sqs(record, context) -> SqsLambdaSegmentContextManager:
    # Use metadata from SQS trace headers to propagate the trace.
    # Assumes the producer is patched to attach headers to the SQS message
    trace_header = extract_trace_header(record)

    # TODO: what about the case where header is missing?

    return SqsLambdaSegmentContextManager(
        recorder=xray_recorder,
        segment_name=context.function_name,
        trace_header=trace_header,
    )
