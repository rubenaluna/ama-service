import logging
import os
import boto3
from botocore.exceptions import BotoCoreError, ClientError


logger = logging.getLogger(__name__)

region = "us-east-2"


def download_object_text(bucket: str, key: str, encoding: str = "utf-8") -> str:
    client = boto3.session.Session(region_name=region).client("s3")

    try:
        response = client.get_object(Bucket=bucket, Key=key)
        body = response["Body"].read()
        return body.decode(encoding)
    except (ClientError, BotoCoreError) as error:
        logger.error("Failed to download s3://%s/%s", bucket, key, exc_info=error)
        raise RuntimeError("Unable to download the requested S3 object.") from error

