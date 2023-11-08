import os
import json
import asyncio
from typing import Literal
import paho.mqtt.client as mqtt
import argparse

import manager.args as manager_args
from manager.tools import Oobabooga, AUTOMATIC1111

sub_topics = {}
pub_topics = {}
state: dict[
    Literal["oobabooga", "automatic1111"], Literal["idle", "running", "stopped"]
] = {"oobabooga": "idle", "automatic1111": "idle"}

client: mqtt.Client = mqtt.Client()


def publish_state(
    tool: Literal["oobabooga", "automatic1111"],
    new_state: Literal["idle", "running", "stopped"] | None,
):
    global state

    if new_state:
        state[tool] = new_state

    print(f"Publishing state: {tool} - {state[tool]}")
    client.publish(pub_topics[f"{tool}_state"], state[tool], retain=True)


# async def health_loop(timeout: float = 5 * 60):
#     while True:
#         await asyncio.sleep(timeout)
#         publish_state()


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("MQTT Broker connected")
        client.subscribe(
            [
                (topic, 2)
                for name, topic in sub_topics.items()
                if enabled_tools.get(name, True)
            ]
        )

        for tool, enabled in enabled_tools.items():
            if enabled:
                publish_state(tool, "idle")
            else:
                publish_state(tool, "stopped")
    else:
        print(f"MQTT Broker connection failed with code: {rc}")


def on_message(client, userdata, message):
    global process
    global state

    print("Message recieved!")

    if message.topic == sub_topics["oobabooga"]:
        payload = message.payload.decode("utf-8")
        if payload == "start":
            oobabooga.start()
        elif payload == "stop":
            oobabooga.stop()
    elif message.topic == sub_topics["automatic1111"]:
        payload = message.payload.decode("utf-8")
        if payload == "start":
            automatic1111.start()
        elif payload == "stop":
            automatic1111.stop()
    elif message.topic == sub_topics["standby"]:
        print("WARNING: Entering Stanby Mode is not supported!")
        # sp.run("sync")

        # ps = sp.Popen(('echo', 'mem'), stdout=sp.PIPE)
        # sp.check_output(('tee', '/sys/power/state'), stdin=ps.stdout)
        # ps.wait()
    else:
        print(f"Got message from unknown topic '{message.topic}'")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Manage different local AI Services over MQTT",
        epilog="Every option can also be defined as environment variable",
    )
    parser.add_argument(
        "-u",
        "--username",
        help="MQTT Username (Use unauthenticated connection if not provided) | MQTT_USER",
        default=os.environ.get("MQTT_USER"),
    )
    parser.add_argument(
        "-p",
        "--password",
        help="MQTT Password (Needs to be defined if username is set) | MQTT_PASSWORD",
        default=os.environ.get("MQTT_PASSWORD"),
    )
    parser.add_argument(
        "-a",
        "--address",
        help="MQTT Broker adress (Default: localhost) | MQTT_BROKER",
        default=os.environ.get("MQTT_BROKER", "127.0.0.1"),
    )
    parser.add_argument(
        "--port",
        help="MQTT Broker port (Default: 1883) | MQTT_PORT",
        type=int,
        default=os.environ.get("MQTT_PORT", 1883),
    )
    parser.add_argument(
        "-t",
        "--topic",
        help="Basetopic on which the programm listens for different messages | AI_MANGER_TOPIC",
        default=os.environ.get("AI_MANGER_TOPIC", "ai_machine"),
    )
    # parser.add_argument(
    #     "-i",
    #     "--interval",
    #     help="State message interval in minutes (Default: 5) | AI_MANGER_INTERVAL",
    #     type=float,
    #     default=os.environ.get("AI_MANGER_INTERVAL", 5),
    # )
    manager_args.default(parser)

    args = parser.parse_args()

    if args.username and args.password:
        client.username_pw_set(args.username, args.password)
    elif args.username or args.password:
        print("Please provide username and password")
        exit()

    enabled_tools = manager_args.validate(args)

    sub_topics = {
        "standby": f"{args.topic}/standby",
        "oobabooga": f"{args.topic}/oobabooga",
        "automatic1111": f"{args.topic}/automatic1111",
    }
    pub_topics = {
        "oobabooga_state": f"{args.topic}/oobabooga/state",
        "automatic1111_state": f"{args.topic}/automatic1111/state",
    }

    if enabled_tools["oobabooga"]:
        oobabooga = Oobabooga(
            args.oobabooga_location, args.oobabooga_venv, publish_state
        )

    if enabled_tools["automatic1111"]:
        automatic1111 = AUTOMATIC1111(
            args.automatic1111_location, args.automatic1111_venv, publish_state
        )

    client.on_message = on_message
    client.on_connect = on_connect
    client.on_disconnect = lambda _, __, ___: print("MQTT Broker disconnected")
    client.will_set(
        pub_topics["oobabooga_state"],
        "stopped",
        retain=True,
    )
    client.will_set(
        pub_topics["automatic1111_state"],
        "stopped",
        retain=True,
    )
    client.connect(args.address, args.port)
    client.loop_start()

    loop = asyncio.get_event_loop()
    # task = loop.create_task(health_loop(args.interval * 60))

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        if enabled_tools["oobabooga"]:
            oobabooga.stop()
        if enabled_tools["automatic1111"]:
            automatic1111.stop()

        client.disconnect()
        loop.stop()
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
