from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from common.envVars import EnvVars


class RATE_LIMITS:

    def __init__(self, app) -> None:
        self.app = app

    def prepare_limiter_obj(self):
        """
        This method returns limiter object by enabling or disabling API rate limits based on the value in environment variables.
        """
        limiter = Limiter(
            self.app,
            key_func=get_remote_address,
            headers_enabled=True,
            enabled=EnvVars.ENABLE_API_RATE_LIMITS
        )
        return limiter


    def construct_rate_limit(self):
        """
        This method returns rate limits string by preparing it based on the values in environment variables.
        """
        rate_limits_per_minute = self.app.config['API_RATE_LIMITS_PER_MINUTE']
        rate_limits_per_hour = self.app.config['API_RATE_LIMITS_PER_HOUR']
        rate_limits = ''
        if rate_limits_per_minute is not None:
            rate_limits = rate_limits + rate_limits_per_minute+'/minute;'
        if rate_limits_per_hour is not None:
            rate_limits = rate_limits + rate_limits_per_hour+'/hour;'
        # print("rate_limits : ", rate_limits)
        # print("rate_limits[:-1] : ", rate_limits[:-1])
        return rate_limits[:-1] if rate_limits else None