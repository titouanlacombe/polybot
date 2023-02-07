import sentry_sdk

from Config.App import env, ver, sentry_dsn

def init(integrations=[]):
	sentry_sdk.init(
		dsn=sentry_dsn,
		integrations=integrations,

		# Set traces_sample_rate to 1.0 to capture 100%
		# of transactions for performance monitoring.
		# We recommend adjusting this value in production.
		traces_sample_rate=1.0,
		environment=env,
		release=ver,
	)
