import time
import logging
import botocore.waiter
from threading import Event
from .waiter import patch_waiter
from .waiter_model import get_logs_model
from .clients import logs_client as client

logger = logging.getLogger()


def wait_for_logs(log_group: str, stream: str, event: Event):

    try:
        # waiting for logs to be available
        waiter_model = get_logs_model()
        waiter = botocore.waiter.create_waiter_with_client(
            "GetLogEvents", waiter_model, client)
        # patching the waiter object
        # so that it can be stopped using event
        patch_waiter(waiter)
        # waiting for log events to be available
        waiter.wait(event, logGroupName=log_group, logStreamName=stream)
    except botocore.waiter.WaiterError as e:
        if "Max attempts exceeded" in str(e):
            logger.error(
                "No Logs Available, please check the log group and stream name")
            logger.error("Exiting Logs Process ...")
        else:
            logger.error(e)
        return
    else:
        if event.is_set():
            # exiting the thread if event is set
            logger.info("Stopped receiving logs ...")
            return
        logger.info("Started to receive logs ...")
        response = client.get_log_events(
            logGroupName=log_group,
            logStreamName=stream,
        )
        for i in response['events']:
            logger.info(i['message'])
        next_token = response['nextForwardToken']

        while not event.is_set():
            time.sleep(2)
            r = client.get_log_events(
                logGroupName=log_group,
                logStreamName=stream,
                nextToken=next_token
            )
            for i in r['events']:
                logger.info(i['message'])
            next_token = r['nextForwardToken']

        logger.info("Stopped receiving logs ...")
