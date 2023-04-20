import sys
import typer
import logging
from .codebuild import trigger_code_build
from .waiter_model import patch_config
# logger setup
logging.basicConfig(format='[%(levelname)s] %(asctime)s %(lineno)d  %(message)s',
                    level=logging.INFO, stream=sys.stdout)

# project = "gsts-fume-alembic-migrations"
# log_group = '/aws/codebuild/gsts-fume-alembic-migrations'


def main(project: str = typer.Option(..., help="Name of the Codebuild Project"),
         log_group: str = typer.Option(..., help="Name of the Cloudwatch Log Group /aws/codebuild/<project-name>"),
         codebuild_poll_interval: int = typer.Option(3, help="Polling interval for Codebuild in seconds"),
         codebuild_max_attempts: int = typer.Option(100, help=("Max attempts for Codebuild to complete, "
                                                               "For project taking more than 5 minutes, "
                                                               "adjust this value accordingly")),
         event_log_poll_interval: int = typer.Option(3, help="Polling interval for CloudWatch Logs in seconds"),
         event_log_max_attempts: int = typer.Option(100, help=("Max attempts for CLoudWatch Logs to Poll, "
                                                               "For project taking more than 5 minutes, "
                                                               "adjust this value accordingly")),
         ):
    patch_config(codebuild_poll_interval=codebuild_poll_interval,
                 codebuild_max_attempts=codebuild_max_attempts,
                 event_log_poll_interval=event_log_poll_interval,
                 event_log_max_attempts=event_log_max_attempts)
    trigger_code_build(project, log_group)


def run():
    typer.run(main)


if __name__ == "__main__":
    run()
