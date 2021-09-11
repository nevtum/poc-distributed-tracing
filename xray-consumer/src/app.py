from typing import Union

from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core.models.trace_header import TraceHeader
from aws_xray_sdk.core.context import Context

# Replace LambdaContext with brand new context to allow put_segment in a lambda.
# It does however leave the side effect where duplicate traces are created
# because of AWS lambda
xray_recorder.configure(context=Context())


def extract_trace_header(record) -> Union[TraceHeader, None]:
    trace_header_str = record.get("attributes", {}).get("AWSTraceHeader", None)
    if trace_header_str:
        return TraceHeader.from_header_str(trace_header_str)


def segment_name(context):
    print(context)
    return "Handle SQS message"


def lambda_handler(event, context):
    print(event)
    print(context)
    for record in event["Records"]:
        trace_header = extract_trace_header(record)
        print(record)
        if trace_header:
            print(trace_header)
            segment = xray_recorder.begin_segment(
                name=segment_name(context),
                traceid=trace_header.root,
                parent_id=trace_header.parent,
                sampling=trace_header.sampled,
            )
            segment.origin = "AWS::Lambda::Function"
            segment.put_metadata("record", record)
            segment.put_metadata("context", context)
            print("Distributed tracing FTW!")
            xray_recorder.end_segment()
