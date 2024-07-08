from PIL import Image, ImageDraw, ImageFont

font = ImageFont.truetype("AntonSC-Regular.ttf", 50)
text = "You should"

img = Image.open("Slopper\\beae21a0-d6cf-11ec-bff7-b6ffa11a2c6c.jfif")
I1 = ImageDraw.Draw(img)
image_width, image_height = img.size

font = ImageFont.truetype("OpenSans-Bold.ttf", 65)
text = "Drink water"

text_bbox = I1.textbbox((0, 0), text, font=font)
text_width = text_bbox[2] - text_bbox[0]
text_height = text_bbox[3] - text_bbox[1]

position = ((image_width - text_width) / 2, (image_height - text_height) / 2)

for offset in [(3, 3), (-3, 3), (3, -3), (-3, -3)]:
    I1.text((position[0] + offset[0], position[1] + offset[1]), text, font=font, fill=(0,0,0))


I1.text(position, text, font=font, fill=(255,255,255))

img.show()