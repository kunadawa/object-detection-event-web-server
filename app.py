from flask import Flask
from flask.wrappers import Response
import argparse
import grpc
from concurrent import futures
import logging
import queue
import google.protobuf.json_format as json_format

from proto.generated import detection_handler_pb2_grpc, detection_handler_pb2
from web_handler import WebDetectionHandler

app = Flask(__name__)
event_queue = None

def detection_event_stream():
    """ get available detection item in event queue """
    # json_format or a dependency appears to change top level field names to camel case
    json_no_newlines = json_format.MessageToJson(event_queue.get()).replace('\n', '')
    yield f"event:detection\ndata:{json_no_newlines}\n\n"

@app.route('/stream')
def stream():
    response = Response(detection_event_stream(), mimetype="text/event-stream")
    # TODO manage this via configuration
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
    return response

if __name__ == '__main__':
    # parse args
    parser = argparse.ArgumentParser(description=" stream detected object events to web clients")
    parser.add_argument("handler_port", help="port to listen for detection handling requests")
    args = parser.parse_args()
    # credit - https://www.semantics3.com/blog/a-simplified-guide-to-grpc-in-python-6c4e25f0c506/
    # create server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    # grpc port setup
    port = args.handler_port
    logging.getLogger().setLevel(logging.DEBUG)
    logging.info(f'starting server on port {port}')
    server.add_insecure_port(f'[::]:{port}')
    # create queue
    event_queue = queue.SimpleQueue()
    # add implementing class to server
    web_handler = WebDetectionHandler(event_queue)
    detection_handler_pb2_grpc.add_DetectionHandlerServicer_to_server(web_handler, server);
    # start grpc server
    server.start()

    # start flask
    app.debug = True
    app.run(threaded=True)
