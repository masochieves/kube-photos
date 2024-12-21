# listen to mqtt
import paho.mqtt.client as mqtt
import time
from PIL import Image, ImageOps
from inky.auto import auto
import random
import os

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    print("Subscribing to topic...")
    client.subscribe("update", qos=0)
    print("Subscribed!")

def on_message(client, userdata, msg):
    print("Message received!")
    print(f"Topic: {msg.topic}")
    print(f"Message: {msg.payload.decode()}")
    document = msg.payload.decode()
    array_pic_time = document.split(",")
    return

def on_subscribe(client, userdata, mid, granted_qos):
    print(f"Subscribed with mid: {mid} and QoS: {granted_qos}")

def display_image(details):
    # TODO
    os.chdir("/home/chief/photo-frame/")
    inky = auto()
    saturation = 1.0
    print(inky.resolution)
    all_images_len = len(os.listdir("./images/"))

    image_number = random.randrange(1, all_images_len)

    try:
        image = Image.open(f"./images/{image_number}.jpg")
    except FileNotFoundError:
        image = Image.open(f"./images/{image_number}.png")
    image = ImageOps.fit(image, inky.resolution)
    inky.set_image(image, saturation=saturation)
    inky.show()

def main():
    # hive connection
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    if on_message():
        display_image(on_connect)
    client.on_subscribe = on_subscribe

    client.username_pw_set("admin-user", "admin-password")

    print("Connecting to broker...")
    if client.connect("100.88.88.23", 1883):
        print("Connected")
    client.loop_forever()

if __name__ == "__main__":
    main()


