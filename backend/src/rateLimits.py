from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from envVars import EnvVars


class RATE_LIMITS:

    def __init__(self, app) -> None:
        self.app = app

    def enable_OR_disable_rate_limits(self):
        print("Started Enabling/Disabling 'limiter' based on the value in EnvVars")
        limiter = Limiter(
            self.app,
            key_func=get_remote_address,
            headers_enabled=True,
            enabled=EnvVars.ENABLE_API_RATE_LIMITS
        )
        print("limiter: ", limiter)
        print("Completed Enabling/Disabling 'limiter' based on the value in EnvVars")
        return limiter


    def construct_rate_limit(self):
        rate_limits_per_minute = self.app.config['API_RATE_LIMITS_PER_MINUTE']
        rate_limits_per_hour = self.app.config['API_RATE_LIMITS_PER_HOUR']
        rate_limits = ''
        if rate_limits_per_minute is not None:
            rate_limits = rate_limits + rate_limits_per_minute+'/minute;'
        if rate_limits_per_hour is not None:
            rate_limits = rate_limits + rate_limits_per_hour+'/hour;'
        print("rate_limits : ", rate_limits)
        print("rate_limits[:-1] : ", rate_limits[:-1])
        return rate_limits[:-1] if rate_limits else None