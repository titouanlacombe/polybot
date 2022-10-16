import os
import sentry_sdk
from Config.App import env, ver

def init(integrations=[]):
	sentry_sdk.init(
		dsn=os.getenv("SENTRY_DSN"),
		integrations=integrations,

		# Set traces_sample_rate to 1.0 to capture 100%
		# of transactions for performance monitoring.
		# We recommend adjusting this value in production.
		traces_sample_rate=1.0,
		environment=env,
		release=ver,
	)
