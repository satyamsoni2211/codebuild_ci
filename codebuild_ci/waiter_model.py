
import botocore.waiter
from dataclasses import dataclass


@dataclass()
class WaiterConfig:
    codebuild_poll_interval: int = 3
    codebuild_max_attempts: int = 100
    event_log_poll_interval: int = 3
    event_log_max_attempts: int = 100


config = WaiterConfig()


def patch_config(**kwargs):
    for k, v in kwargs.items():
        setattr(config, k, v)


# waiter for codebuild
def get_codebuild_model():
    return botocore.waiter.WaiterModel({
        'version': 2,
        'waiters': {
            "BatchGetBuilds": {
                'delay': config.codebuild_poll_interval,
                'operation': 'BatchGetBuilds',
                'maxAttempts': config.codebuild_max_attempts,
                'acceptors': [
                    {
                        'expected': "SUCCEEDED",
                        'matcher': 'pathAny',
                        'state': 'success',
                        'argument': 'builds[].buildStatus'
                    },
                    {
                        'expected': "FAILED",
                        'matcher': 'pathAny',
                        'state': 'failure',
                        'argument': 'builds[].buildStatus'
                    },
                    {
                        'expected': "STOPPED",
                        'matcher': 'pathAny',
                        'state': 'failure',
                        'argument': 'builds[].buildStatus'
                    },
                ]
            }
        }
    })

# Wait for logs to be available


def get_logs_model():
    return botocore.waiter.WaiterModel({
        "version": 2,
        "waiters": {
            "GetLogEvents": {
                "delay": config.event_log_poll_interval,
                "maxAttempts": config.event_log_max_attempts,
                "operation": "GetLogEvents",
                "acceptors": [
                    {
                        "matcher": "path",
                        "expected": True,
                        "argument": "length(events[]) > `0`",
                        "state": "success"
                    },
                    # Retry on ResourceNotFoundException
                    {
                        'expected': 'ResourceNotFoundException',
                        'matcher': 'error',
                        'state': 'retry'
                    }
                ]
            },
        }
    })
