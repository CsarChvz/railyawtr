from aws_lambda_powertools import Logger

from app.config import get_settings

# from aws_lambda_powertools import Tracer
# from aws_lambda_powertools import Metrics

logger = Logger(level=get_settings().log_level)
# tracer = Tracer()
# metrics = Metrics()
