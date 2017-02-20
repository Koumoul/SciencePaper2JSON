from PIL import Image
from pytesseract import image_to_string

text = image_to_string(Image.open('paper/test_split/crop3.jpeg'), lang='eng')

print(text)
