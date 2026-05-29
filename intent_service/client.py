import argparse

import grpc

import intent_service_pb2
import intent_service_pb2_grpc


def main() -> None:
    parser = argparse.ArgumentParser(description="Test the gRPC IntentService")
    parser.add_argument("message", nargs="?", default="I lost my card and need urgent support")
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", default="50051")
    args = parser.parse_args()

    target = f"{args.host}:{args.port}"
    with grpc.insecure_channel(target) as channel:
        stub = intent_service_pb2_grpc.IntentServiceStub(channel)
        response = stub.IntentRecognizer(intent_service_pb2.IntentRequest(message=args.message), timeout=10)
        print({
            "intent": response.intent,
            "confidence": round(float(response.confidence), 3),
            "reason": response.reason,
        })


if __name__ == "__main__":
    main()
