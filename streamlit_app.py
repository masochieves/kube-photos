import streamlit as st
from io import BytesIO
import os 
from math import ceil
import paho.mqtt.client as mqtt
import time 
from mqtt_broker import *

# Path to image files
os.chdir("/home/chief/kube-photos/")
# os.chdir("C:/D drive/2024 WTH")

class GalleryPage():
    def __init__(self, mqtt_client=None):
        self.mqtt_client = mqtt_client

        self.row_size = 4
        self.batch_size = 8
        self.img_dir = "./images/"

        # States
        self.current_state_text = None
        self.current_img = None
        self.page_no = 1                # gallery page
        # self.initialise_page()

    def initialise_page(self):
        st.title("Gallery")

        if 'img_ls' not in st.session_state:
            img_ls = get_all_images()
            st.session_state['img_ls'] = img_ls
        else: 
            img_ls = st.session_state['img_ls']
    
        num_batches = ceil(len(img_ls)/self.batch_size)
        if num_batches == 0: 
            num_batches = 1
            no_photos_text = st.empty()
            no_photos_text.markdown(":red[No images in the folder.]")
        files = img_ls

        # Show current display status
        self.current_state_text = st.empty()
        self.current_state_text.markdown("Current display mode: " 
                                         + (f"Displaying {st.session_state['displayed_image']}" if st.session_state['is_display_mode'] else "Slideshow"))
        self.current_img = st.empty()
        self.current_img.markdown("Selected image: "+st.session_state['selected_image'])

        # Initialise control buttons
        controls = st.columns(4) # display image, slideshow mode
        with controls[0]:
            _ = st.text("Select display mode:")
        with controls[1]:
            _ = st.button("Display Selected", on_click=lambda:self.on_click_mode_buttons(0))
        with controls[2]:
            _ = not st.button("Slideshow", on_click=lambda:self.on_click_mode_buttons(1))
        with controls[3]:
            self.page_no = st.selectbox("Page", range(1, num_batches+1))

        # Show gallery of images
        self.render_photo_grid()

    # @st.fragment
    def render_photo_grid(self):
        files = st.session_state['img_ls']

        # Show gallery of images
        batch_imgs = files[(self.page_no-1)*self.batch_size:self.page_no*self.batch_size]

        grid = st.columns(self.row_size)
        col = 0

        for img in batch_imgs:
            with grid[col]:
                st.image(self.img_dir+img, caption=img)
                _ = st.button("Select", key=f"button_{img}", on_click=lambda:self.on_click_select_img(img))
            col = (col+1) % self.row_size

    # Button functions
    def on_click_mode_buttons(self, clicked_button):
        show_str = "Current display mode: "
        # if clicked_button == 0, clicked button is 'display selected'
        if clicked_button == 0:
            st.session_state['is_display_mode'] = True
            st.session_state['displayed_image'] = st.session_state['selected_image']

            client = get_paho_client()
            if client != None and not st.session_state['displayed_image'] == "-":
                print("Publishing message...")
                message = "display," + st.session_state['displayed_image']
                result = client.publish("updates", message, qos=0)
                print("Message published: ", message)
                print(f"Publish result: {result}")
            elif client is None:
                print("Could not connect to client.")
            else:
                print("No image selected and display mode is 'Display selected'. No message was published.")

        # if clicked_button == 1, clicked button is 'slideshow'
        elif clicked_button == 1:
            st.session_state['is_display_mode'] = False

            client = get_paho_client()
            if client != None:
                print("Publishing message...")
                message = "slideshow,-"
                result = client.publish("updates", message, qos=0)
                print("Message published: ", message)
                print(f"Publish result: {result}")
            else:
                print("Could not reach MQTT client.")

        self.current_state_text.markdown(
            show_str + (f"Displaying {st.session_state['displayed_image']} " if st.session_state['is_display_mode'] else "Slideshow"))
        
    def on_click_select_img(self, img_name):
        st.session_state['selected_image'] = img_name
        self.current_img.markdown("Selected image: "+st.session_state['selected_image'])

    
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc, properties=None):
    if rc != 0:
        print("Connected with result code " + str(rc))

def on_publish(client, userdata, mid, properties=None, reasonCode=None):
    print(f"Message published with mid: {mid}")

def get_paho_client():
    print("Getting MQTT client...")
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, protocol=mqtt.MQTTv5)
    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(client, userdata, flags, rc, properties=None):
        if rc != 0:
            print("Connected with result code " + str(rc))

    client.on_connect = on_connect
    client.on_publish = on_publish
    # set username and password
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

    try:
        print("Connecting to publisher...")
        client.connect(MQTT_HOSTNAME, MQTT_PORT)
        client.loop_start()
    except TimeoutError as e:
        print(traceback.format_exc())
        client = None

    return client

def upload_page():
    st.title("Upload Images")
    uploaded_file = st.file_uploader("Upload image(s) here :open_file_folder:", accept_multiple_files= True, type=['jpg', 'jpeg', 'png'])

    # Handle uploaded files
    if uploaded_file is not None:
        img_ls = get_all_images()
        all_images_len = len(img_ls)

        for image in uploaded_file:
            all_images_len +=1
            st.image(image)
            extension = image.name[-4:]
            if extension[0] != ".":
                extension = image.name[-5:]
            with open(f"{self.img_dir}{all_images_len}{extension}", "wb") as f:
                f.write(image.getbuffer())

def get_all_images(img_dir="./images/"):
    img_list = []
    try:
        for file in os.listdir(img_dir):
            if file[-4:] in [".jpg", ".png"]:
                img_list.append(file)
        all_images_len = len(img_list)
    except FileNotFoundError:
        os.mkdir(img_dir)
        all_images_len = len(os.listdir(img_dir))
    return img_list

def main(mqtt_client=None):
    # Session states
    if 'is_display_mode' not in st.session_state:
        st.session_state['is_display_mode'] = True
    if 'selected_image' not in st.session_state:
        st.session_state['selected_image'] = "-"
    if 'displayed_image' not in st.session_state:
        st.session_state['displayed_image'] = "-"

    # Have pages in a navigation bar
    gallery_page = GalleryPage(mqtt_client).initialise_page
    nav = st.navigation([st.Page(gallery_page, title="Display Image"), st.Page(upload_page, title="Upload Image")])
    nav.run()

if __name__ == "__main__":
    main()