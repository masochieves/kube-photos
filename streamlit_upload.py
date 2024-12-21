import streamlit as st
from io import BytesIO
import os 
import pandas as pd

# Path to image files
# os.chdir("/home/chief/kube-photos/")
os.chdir("C:/D drive/2024 WTH")

class GalleryPage():
    def __init__(self):
        # States
        self.current_state_text = None
        self.current_img = None
        self.is_display_mode = True     # false if slideshow, true if selected display
        self.selected_image = "-"       # path of selected image
        self.page_no = 1                # gallery page
        self.initialise_page()

    def initialise_page(self):
        st.title("Gallery")
        img_dir = "./images/"
        num_batches = get_total_images()
        print("num_batches", num_batches)
        files = os.listdir(img_dir)

        # Show current display status
        self.current_state_text = st.empty()
        self.current_state_text.markdown("Current display mode:" 
                                         + (f"Displaying {self.selected_image}" if self.is_display_mode else "Slideshow"))
        self.current_img = st.empty()
        self.current_img.markdown("Selected image:"+self.selected_image)

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
        row_size = 4
        batch_size = 20
        batch_imgs = files[(self.page_no-1)*batch_size:self.page_no*batch_size]

        grid = st.columns(row_size)
        col = 0

        for img in batch_imgs:
            with grid[col]:
                st.image(img_dir+img, caption=img)
                _ = st.button("Select", on_click=lambda:self.on_click_select_img(img))
            col = (col+1) % row_size

    # Button functions
    def on_click_mode_buttons(self, clicked_button):
        show_str = "Current display mode:"
        # if clicked_button == 0, clicked button is 'display selected'
        if clicked_button == 0:
            self.selected_image = self.get_selected_img()
            self.is_display_mode = True
        # if clicked_button == 1, clicked button is 'slideshow'
        elif clicked_button == 1:
            self.is_display_mode = False

        self.current_state_text.markdown(
            show_str + (f"Displaying {self.selected_image}" if self.is_display_mode else "Slideshow"))
        
    def on_click_select_img(self, img_name):
        self.selected_image = img_name
        self.current_img.markdown("Selected image:"+self.selected_image)





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


if __name__ == "__main__":
    # Have pages in a navigation bar
    nav = st.navigation([st.Page(GalleryPage(), title="Display Image"), st.Page(upload_page, title="Upload Image")])
    nav.run()