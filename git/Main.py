import os
import signal
import time
import sys
import sh
import logging

from InputValuesCheck import *
from Repo import RepoFactory
from Notify import *
from ConfigReader import *
from Errors import *
from Config import AVAILABLE_LOG_LEVELS

POLLING_INTERVAL = os.environ.get('POLLING_INTERVAL', 1)
GIT_REPO_URL = os.environ.get("GIT_URL", None)
GIT_USER_NAME = os.environ.get("GIT_USER_NAME", None)
GIT_PERSONAL_TOKEN = os.environ.get("GIT_PERSONAL_TOKEN", None)
GIT_BRANCH = os.environ.get("GIT_PULL_BRANCH", "main")
GIT_USE_SSH_KEY = os.environ.get("GIT_USE_SSH_KEY", None)
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
GIT_STRICT_HOST_KEY_CHECKING = os.environ.get("GIT_STRICT_HOST_KEY_CHECKING", "yes")



print(str(type(GIT_USE_SSH_KEY)))
print(str(GIT_USE_SSH_KEY))
print("fucking log level = " + str(LOG_LEVEL))

#logger = logging.getLogger('dev')
if LOG_LEVEL not in AVAILABLE_LOG_LEVELS:
    LOG_LEVEL = "INFO"
    print("Invalid value given to LOG_LEVEL. Defaulting to level : INFO")
print("value à la noix retournée = " + str(getattr(logging, LOG_LEVEL)))
#logger.setLevel(getattr(logging, LOG_LEVEL))


logging.basicConfig()
logging.getLogger().setLevel(getattr(logging, LOG_LEVEL))

logging.error("-----> ERROR")
logging.warning("------> WARNING")
logging.info("------> INFO")
logging.debug("-----> DEBUG")

logging.info("Running Git (container) version : %s" % os.environ.get("VERSION", "?"))


def receive_signal(signal_number, frame):
    print('Received:', signal_number)
    if signal_number == 10:
        repo_refresh()


def repo_refresh():
    try:
        repo.update_repo()
    except GitUpdateError as err:
        logging.fatal(str(err))
        return

    if repo.has_repo_changed():
        notify.manifests_config(config_reader.load_config_from_fs())


try:
    check = InputValuesCheck()
    check.check_polling_time(POLLING_INTERVAL)
    check.check_git_url(GIT_REPO_URL, GIT_USE_SSH_KEY)
    check.check_git_auth(GIT_USER_NAME, GIT_PERSONAL_TOKEN, GIT_USE_SSH_KEY)
    check.check_git_strict_host_key_checking(GIT_STRICT_HOST_KEY_CHECKING)
    POLLING_INTERVAL = int(POLLING_INTERVAL)
except ValueError as err:
    logging.info(err)
    print("EXITING !")
    sys.exit()

config_reader = ConfigReader()
notify = Notify()
repo = RepoFactory.create_repo(GIT_REPO_URL, GIT_USER_NAME, GIT_PERSONAL_TOKEN, GIT_BRANCH, GIT_STRICT_HOST_KEY_CHECKING, notify)
config = None

notify.wait_for_ready_status()
notify.set_tofu_code()
notify.current_proc_pid()
signal.signal(signal.SIGUSR1, receive_signal)

while True:
    repo_refresh()
    print("Waiting !")
    time.sleep(POLLING_INTERVAL * 60)
