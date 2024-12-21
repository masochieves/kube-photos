import paho.mqtt.client as mqtt
import time
import streamlit as st
import os 
from io import BytesIO
from math import ceil
from streamlit_app import main
import traceback


def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")

def on_publish(client, userdata, mid):
    print(f"Message published with mid: {mid}")

if __name__ == "__main__":
    # Initialise MQTT Client
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_publish = on_publish
    client.username_pw_set("admin-user", "admin-password")

    try:
        print("Connecting to publisher...")
        #client.connect("localhost", 30083)
        client.connect("100.88.88.23", 1883)
        client.loop_start()
    except TimeoutError as e:
        print(traceback.format_exc())
        client = None

    main(client)

    try:
        client.loop_stop()
        client.disconnect()
    except AttributeError:
        pass