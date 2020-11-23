import boto3


def write_string_to_s3(s3_bucket, s3_key, data):
    encoded_data = data.encode("utf-8")

    s3 = boto3.resource("s3")
    s3.Bucket(s3_bucket).put_object(Key=s3_key, Body=encoded_data)
