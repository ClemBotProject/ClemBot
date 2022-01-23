import os
import logging

import seqlog
from seqlog import StructuredRootLogger, StructuredLogger, ConsoleStructuredLogHandler

if bool(os.environ.get('PROD')):

    # Production logging setup
    url = os.environ.get('SEQ_URL')
    key = os.environ.get('SEQ_BOT_KEY')

    if not key:
        raise Exception('SEQ_BOT_KEY not found but SEQ_URL was specified')

    seqlog.log_to_seq(
        # Initialize the seq logging url before the secrets are loaded
        # this is ok because seq logging only happens in prod
        server_url=url,
        api_key=key,
        level=logging.INFO,
        batch_size=5,
        auto_flush_timeout=10,  # seconds
        override_root_logger=False,
    )
else:
    # Development logging setup
    logging.setLoggerClass(StructuredLogger)

    logging.root = StructuredRootLogger(logging.WARNING)
    logging.Logger.root = logging.root
    logging.Logger.manager = logging.Manager(logging.Logger.root)

    logging.basicConfig(
        format='%(asctime)s %(levelname)s %(module)s %(message)s',
        handlers=[
            ConsoleStructuredLogHandler()
        ],
        level=logging.INFO,
    )
