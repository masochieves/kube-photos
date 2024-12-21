import streamlit as st
from io import BytesIO
import os 

os.chdir("/home/chief/kube-photos/")
uploaded_file = st.file_uploader("Upload image(s) here :open_file_folder:", accept_multiple_files= True, type=['jpg', 'jpeg', 'png'])

if uploaded_file is not None:
    try:
        all_images_len = len(os.listdir("./images/"))
    except FileNotFoundError:
        os.mkdir("./images/")
        all_images_len = len(os.listdir("./images/"))

    for image in uploaded_file:
        all_images_len +=1
        st.image(image)
        extension = image.name[-4:]
        if extension[0] != ".":
            extension = image.name[-5:]
        with open(f"./images/{all_images_len}{extension}", "wb") as f:
            f.write(image.getbuffer())
