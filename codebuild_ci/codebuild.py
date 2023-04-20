import sys
import logging
import threading
import botocore.waiter
from codebuild_ci.logs import wait_for_logs
from .clients import codebuild_client as client
from codebuild_ci.waiter_model import get_codebuild_model

logger = logging.getLogger()


def trigger_code_build(project: str, log_group: str):
    # setting project name

    # starting codebuild pipeline
    res = client.start_build(projectName=project)

    # setting up parameters
    build_id = res.get('build').get('id')
    stream = build_id.split(':')[1]
    failure = False
    message = "CodeBuild pipeline completed successfully !"
    event = threading.Event()
    # logging
    logger.info("Started Build ID: {}".format(build_id))

    t = threading.Thread(target=wait_for_logs, args=(log_group, stream, event))
    t.start()

    try:
        waiter_model = get_codebuild_model()
        waiter = botocore.waiter.create_waiter_with_client(
            "BatchGetBuilds", waiter_model, client)
        logger.info("Waiting for CodeBuild pipeline to complete...")
        waiter.wait(
            ids=[build_id])
    except botocore.waiter.WaiterError as e:
        if "STOPPED" in str(e):
            message = "CodeBuild pipeline stopped !"
        else:
            message = "CodeBuild pipeline failed !"
        failure = True
    finally:
        event.set()
        t.join()
        if failure:
            logger.error(message)
            sys.exit(1)
        else:
            logger.info(message)
