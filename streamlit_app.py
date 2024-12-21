import streamlit as st
from io import BytesIO
import os 
from math import ceil
import paho.mqtt.client as mqtt
import time 

# Path to image files
# os.chdir("/home/chief/kube-photos/")
os.chdir("C:/D drive/2024 WTH")

class GalleryPage():
    def __init__(self, mqtt_client=None):
        self.mqtt_client = mqtt_client

        # States
        self.current_state_text = None
        self.current_img = None
        self.page_no = 1                # gallery page
        # self.initialise_page()

    def initialise_page(self):
        st.title("Gallery")

        row_size = 4
        batch_size = 8
        img_dir = "./images/"
        num_batches = ceil(get_total_images()/batch_size)
        files = os.listdir(img_dir)

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
        batch_imgs = files[(self.page_no-1)*batch_size:self.page_no*batch_size]

        grid = st.columns(row_size)
        col = 0

        for img in batch_imgs:
            with grid[col]:
                st.image(img_dir+img, caption=img)
                _ = st.button("Select", key=f"button_{img}", on_click=lambda:self.on_click_select_img(img))
            col = (col+1) % row_size

    # Button functions
    def on_click_mode_buttons(self, clicked_button):
        show_str = "Current display mode: "
        # if clicked_button == 0, clicked button is 'display selected'
        if clicked_button == 0:
            st.session_state['is_display_mode'] = True
            st.session_state['displayed_image'] = st.session_state['selected_image']

            if self.mqtt_client != None and not st.session_state['displayed_image'] == "-":
                print("Publishing message...")
                message = "display," + st.session_state['displayed_image']
                result = self.mqtt_client.publish("updates", message, qos=0)
                print(f"Publish result: {result}")
            else:
                print("No image selected and display mode is 'Display selected'. No message was published.")

        # if clicked_button == 1, clicked button is 'slideshow'
        elif clicked_button == 1:
            st.session_state['is_display_mode'] = False

            if self.mqtt_client != None:
                print("Publishing message...")
                message = "slideshow,-"
                result = self.mqtt_client.publish("updates", message, qos=0)
                print(f"Publish result: {result}")

        self.current_state_text.markdown(
            show_str + (f"Displaying {st.session_state['displayed_image']} " if st.session_state['is_display_mode'] else "Slideshow"))
        
    def on_click_select_img(self, img_name):
        st.session_state['selected_image'] = img_name
        self.current_img.markdown("Selected image: "+st.session_state['selected_image'])

def upload_page():
    st.title("Upload Images")
    uploaded_file = st.file_uploader("Upload image(s) here :open_file_folder:", accept_multiple_files= True, type=['jpg', 'jpeg', 'png'])

    # Handle uploaded files
    if uploaded_file is not None:
        all_images_len = get_total_images()

        for image in uploaded_file:
            all_images_len +=1
            st.image(image)
            extension = image.name[-4:]
            if extension[0] != ".":
                extension = image.name[-5:]
            with open(f"./images/{all_images_len}{extension}", "wb") as f:
                f.write(image.getbuffer())

def get_total_images():
    try:
        all_images_len = len(os.listdir("./images/"))
    except FileNotFoundError:
        os.mkdir("./images/")
        all_images_len = len(os.listdir("./images/"))
    return all_images_len

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