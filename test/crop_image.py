from PIL import Image
im = Image.open("pages/TCL/play_page_1.png")
region = im.crop((50, 50, 100, 100))
region.save("region.sample3.png")
