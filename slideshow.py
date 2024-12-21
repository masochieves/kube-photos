from PIL import Image, ImageOps
from inky.auto import auto
import argparse
import os

def parseargs():
	parser = argparse.ArgumentParser(description="Displays image on InkyImpressions.")
	parser.add_argument("path", help="Path to image.")
	args = parser.parse_args()
	return args

def display_slideshow(img_path):
	inky = auto(ask_user=True, verbose=True)
	saturation = 1.0

	try:
		image = Image.open(img_path)
	except FileNotFoundError:
		print("Image not found at path:", img_path)
		return

	image = ImageOps.fit(image, inky.resolution)
	inky.set_image(image, saturation=saturation)
	inky.show()

if __name__ == "__main__":
	args = parseargs()
	display_slideshow(args.path)
