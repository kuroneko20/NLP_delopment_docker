from concurrent import futures
import logging

import grpc

import intent_service_pb2
import intent_service_pb2_grpc
from core.settings import get_settings
from nodes.intent_node import IntentNode


class IntentService(intent_service_pb2_grpc.IntentServiceServicer):
    def __init__(self) -> None:
        self.intent_node = IntentNode()

    def IntentRecognizer(self, request, context):
        message = request.message.strip()
        if not message:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("message must not be empty")
            return intent_service_pb2.IntentResponse(
                intent="unknown",
                confidence=0.0,
                reason="Empty message is invalid.",
            )

        prediction = self.intent_node.classify(message)
        return intent_service_pb2.IntentResponse(
            intent=prediction.intent,
            confidence=prediction.confidence,
            reason=prediction.reason,
        )


def serve() -> None:
    settings = get_settings()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    intent_service_pb2_grpc.add_IntentServiceServicer_to_server(IntentService(), server)
    server.add_insecure_port(f"[::]:{settings.grpc_port}")
    server.start()
    logging.info("Intent service started on port %s", settings.grpc_port)
    server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    serve()
