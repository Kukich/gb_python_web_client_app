import sys
import os
import logging
import yaml
import logging.handlers
sys.path.append(os.path.join(os.getcwd(), '..'))
from common.variables import CONFIG_LOG


def mkdir_p(path):
    print(f"mkdir_p {path}")
    try:
        os.makedirs(path, exist_ok=True)
    except TypeError:
        try:
            os.makedirs(path)
        except OSError as exc:
            print(exc)

def open_file(path):
    print("open_file")
    try:
        my_file = open(path, 'r')
    except FileNotFoundError:
        print("файла не существует ", path)
        return 0
    else:
        return my_file


def get_conf(name):
    stream = open_file(name)
    try:
        return yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)
        return 0
    finally:
        stream.close


config_path = os.path.dirname(os.path.abspath(__file__))
log_configs = get_conf(os.path.join(config_path,CONFIG_LOG))

for conf in log_configs:
    FORMATTER = logging.Formatter(conf["FORMAT"])
    PATH = os.path.dirname(os.path.abspath(__file__))
    PATH = os.path.join(PATH,str(conf["name"]+'_log'))
    mkdir_p(PATH)
    PATH = os.path.join(PATH,str(conf["name"] + '.log'))
    STREAM_HANDLER = logging.StreamHandler(sys.stderr)
    STREAM_HANDLER.setFormatter(FORMATTER)
    STREAM_HANDLER.setLevel(conf["STREAM_LOG_LEVEL"])
    LOG_FILE = logging.FileHandler(PATH,encoding='utf-8')
    if(conf["ROTATION"]):
        LOG_FILE = logging.handlers.TimedRotatingFileHandler(PATH,encoding='utf-8',interval=1,when='midnight')
    LOG_FILE.setFormatter(FORMATTER)
    LOGGER = logging.getLogger(conf["name"])
    LOGGER.addHandler(STREAM_HANDLER)
    LOGGER.addHandler(LOG_FILE)
    LOGGER.setLevel(conf["LOG_LEVEL"])

if __name__ ==  '__main__':
    mylog=logging.getLogger('server')
    mylog.debug('Hello server again')
