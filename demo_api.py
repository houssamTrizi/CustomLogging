from flask import Flask
from flask import request
from logger import configure_logger, init_logger
import logging

import uuid

app = Flask(__name__)

REQUEST_TEMPLATE_MESSAGE = "{routeName} {correlationId} {logOrder} {msg}"
configure_logger()


def get_api_logger():
    return init_logger("api", extra=dict(correlationId=uuid.uuid4(), routeName=request.path))


@app.route("/ping")
def ping():
    logger = get_api_logger()
    logger.log("{routeName} {correlationId} {logOrder} {msg}", request.path, uuid.uuid4())
    return "pong"


@app.route("/imane/<id>")
def pong(id):
    logger = get_api_logger()
    logger.info(f"Parsing {id}")
    return id


if __name__ == '__main__':
    logger = logging.getLogger("server")
    logger.info("Starting service....")
    app.run()
