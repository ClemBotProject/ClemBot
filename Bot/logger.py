import logging
import sys


def setup_logger(name, log_file, level=logging.INFO, StdOut=False):

    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

    handler = logging.FileHandler(log_file, encoding='utf-8', mode='w')        
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    if StdOut:
        stdOutHandle = logging.StreamHandler(sys.stdout)
        stdOutHandle.setLevel(level)
        stdOutHandle.setFormatter(formatter)
        logger.addHandler(stdOutHandle)

    return logger

def setup_dis_py_log():
    logger = logging.getLogger('discord')
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(filename='Logs/discord.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)

botlog = setup_logger('botlog', 'Logs/bot.log', logging.INFO, True)