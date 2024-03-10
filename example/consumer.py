import asyncio
import sys

from confluent_kafka import Consumer, KafkaException
from confluent_kafka.serialization import MessageField, SerializationContext

from superstream import configure_deserializer, init
from superstream.serialization import SuperstreamDeserializer
from superstream.types import _Option


async def main():
    token = "<superstream-token>"
    superstream_host = "<superstream-host>"
    group = "<kafka-consumer-group>"
    topics = ["<kafka-topic>"]
    broker = "<kafka-broker>"
    conf = {
        "bootstrap.servers": broker,
        "group.id": group,
        "session.timeout.ms": 6000,
        "enable.auto.offset.store": False,
        "statistics.interval.ms": 1000,
    }

    options = _Option(host=superstream_host, learning_factor=10, servers=broker)
    client_id = await init(token, superstream_host, conf, options)

    c = Consumer(conf)
    c.subscribe(topics)

    deserialize = SuperstreamDeserializer()
    configure_deserializer(client_id, deserialize)

    try:
        while True:
            msg = c.poll(timeout=1.0)
            if msg is None:
                continue
            message = deserialize(msg.value(), SerializationContext(msg.topic(), MessageField.VALUE, msg.headers()))
            if msg.error():
                raise KafkaException(msg.error())
            else:
                sys.stderr.write("[%s: %d] %s %s\n" % (msg.topic(), msg.partition(), message, msg.headers()))
    except KeyboardInterrupt:
        sys.stderr.write("%% Aborted by user\n")

    finally:
        c.close()


if __name__ == "__main__":
    asyncio.run(main())
