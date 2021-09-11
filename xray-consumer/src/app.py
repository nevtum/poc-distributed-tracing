from tracing import segment_handle_sqs


def lambda_handler(event, context):
    for record in event["Records"]:
        with segment_handle_sqs(record, context) as segment:
            segment.put_metadata("record", record)
            segment.put_metadata("context", context)
            print("Distributed tracing FTW!")
