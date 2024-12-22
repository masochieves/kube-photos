import paho.mqtt.client as mqtt
import time
from PIL import Image, ImageOps
from inky.auto import auto
import random
import os
import asyncio
from functools import partial

class PhotoFrame:
    def __init__(self):
        self.current_task = None
        self.loop = asyncio.get_event_loop()
        self.inky = auto()

    def display_image(self, img_name):
        saturation = 1.0
        print(self.inky.resolution)
        try:
            image = Image.open(f"images/{img_name}.jpg")
        except FileNotFoundError:
            image = Image.open(f"images/{img_name}.png")
        
        image = ImageOps.fit(image, self.inky.resolution)
        self.inky.set_image(image, saturation=saturation)
        self.inky.show()

    def slideshow(self):
        # TODO
        all_images = os.listdir("images/")
        all_images_len = len(all_images)-1
        image_number = random.randrange(0, all_images_len)
        self.display_image(all_images[image_number])

    async def display_image_wrapper(self, img_name, mode):
        try:
            if mode == "display":
            # Cancel previous task if it exists
                if self.current_task and not self.current_task.done():
                    self.current_task.cancel()
                    try:
                        await self.current_task
                    except asyncio.CancelledError:
                        pass

            # Call display_image function
                self.display_image(img_name)
            # Sleep for specified time
                await asyncio.sleep(1)
            elif mode == "slideshow":
                if not self.current_task and self.current_task.done():
                    self.slideshow()

        except asyncio.CancelledError:
            pass

    def on_message(self, client, userdata, msg):
        print("Message received!")
        print(f"Topic: {msg.topic}")
        print(f"Message: {msg.payload.decode()}")
        
        # Parse message
        document = msg.payload.decode()
        array_pic_time = document.split(",")  # Assuming format: "image_number,sleep_time"
        
        # Create new task
        self.current_task = self.loop.create_task(
            self.display_image_wrapper(array_pic_time, array_pic_time[1])
        )

    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected with result code {rc}")
        print("Subscribing to topic...")
        client.subscribe("update", qos=0)
        print("Subscribed!")

    def on_subscribe(self, client, userdata, mid, granted_qos):
        print(f"Subscribed with mid: {mid} and QoS: {granted_qos}")

    async def start(self):
        client = mqtt.Client()
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        client.on_subscribe = self.on_subscribe

        client.username_pw_set("admin-user", "admin-password")

        print("Connecting to broker...")
        client.connect("100.88.88.23", 1883)
        client.loop_start()

        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            client.loop_stop()
            client.disconnect()

async def main():
    photo_frame = PhotoFrame()
    await photo_frame.start()

if __name__ == "__main__":
    asyncio.run(main())
