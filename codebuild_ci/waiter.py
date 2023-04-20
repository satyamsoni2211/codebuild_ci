import time
from threading import Event
from botocore.waiter import (
    Waiter, is_valid_waiter_error, WaiterError, logger)


class EventWaiter(Waiter):
    def wait(self, event: Event = None, **kwargs):
        acceptors = list(self.config.acceptors)
        current_state = 'waiting'
        # pop the invocation specific config
        config = kwargs.pop('WaiterConfig', {})
        sleep_amount = config.get('Delay', self.config.delay)
        max_attempts = config.get('MaxAttempts', self.config.max_attempts)
        last_matched_acceptor = None
        num_attempts = 0

        while True:
            response = self._operation_method(**kwargs)
            num_attempts += 1
            for acceptor in acceptors:
                if acceptor.matcher_func(response):
                    last_matched_acceptor = acceptor
                    current_state = acceptor.state
                    break
            else:
                # If none of the acceptors matched, we should
                # transition to the failure state if an error
                # response was received.
                if is_valid_waiter_error(response):
                    # Transition to a failure state, which we
                    # can just handle here by raising an exception.
                    raise WaiterError(
                        name=self.name,
                        reason='An error occurred (%s): %s'
                        % (
                            response['Error'].get('Code', 'Unknown'),
                            response['Error'].get('Message', 'Unknown'),
                        ),
                        last_response=response,
                    )
            # if event is provided, program will exit if event is set
            if event and event.is_set():
                logger.debug(
                    "Waiting Complete, got exit event ..."
                )
                return
            if current_state == 'success':
                logger.debug(
                    "Waiting complete, waiter matched the " "success state."
                )
                return
            if current_state == 'failure':
                reason = 'Waiter encountered a terminal failure state: %s' % (
                    acceptor.explanation
                )
                raise WaiterError(
                    name=self.name,
                    reason=reason,
                    last_response=response,
                )
            if num_attempts >= max_attempts:
                if last_matched_acceptor is None:
                    reason = 'Max attempts exceeded'
                else:
                    reason = (
                        'Max attempts exceeded. Previously accepted state: %s'
                        % (acceptor.explanation)
                    )
                raise WaiterError(
                    name=self.name,
                    reason=reason,
                    last_response=response,
                )
            time.sleep(sleep_amount)


def patch_waiter(waiter: Waiter):
    """
    Function to monkey patch the wait method to the waiter object
    for accepting the event object
    to stop quit the wait method

    Args:
        waiter (Waiter): Waiter Object
    """
    def wait(event: Event = None, **kwargs):
        EventWaiter.wait(waiter, event, **kwargs)
    setattr(waiter, 'wait', wait)
