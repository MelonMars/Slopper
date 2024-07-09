"""
 :::===  :::      :::====  :::====  :::====  :::===== :::====
 :::     :::      :::  === :::  === :::  === :::      :::  ===
  =====  ===      ===  === =======  =======  ======   =======
     === ===      ===  === ===      ===      ===      === ===
 ======  ========  ======  ===      ===      ======== ===  ===

https://patorjk.com/software/taag/#p=display&f=USA%20Flag&t=Slopper
"""

# Fixed a lot the PEP errors & warnings by just ignoring them
# TODO:
# Fix:
# Video maker
# Test
# Add menu at start for selecting tag and everything

from langchain_huggingface.llms import HuggingFacePipeline
from langchain.prompts import PromptTemplate
import re
import os
import glob
import cv2
import requests
import base64
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
from pydub import AudioSegment
from moviepy.editor import VideoFileClip, AudioFileClip


def image_on_text(txt: str, imgPath: str, outputPath: str):
    counter = 0
    while True:
        if counter == 0:
            new_output_path = outputPath
        else:
            base, ext = os.path.splitext(outputPath)
            new_output_path = f"{base}_{counter}{ext}"

        if not os.path.exists(new_output_path):
            break
        counter += 1

    try:
        with Image.open(imgPath) as img:
            im1 = ImageDraw.Draw(img)
            image_width, image_height = img.size

            font = ImageFont.truetype("OpenSans-Bold.ttf", 65)

            text_bbox = im1.textbbox((0, 0), txt, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]

            position = ((image_width - text_width) / 2, (image_height - text_height) / 2)

            for offset in [(3, 3), (-3, 3), (3, -3), (-3, -3)]:
                im1.text((position[0] + offset[0], position[1] + offset[1]), txt, font=font, fill=(0, 0, 0))

            im1.text(position, txt, font=font, fill=(255, 255, 255))
            img.save(new_output_path)
            print(txt)

    except MemoryError as e:
        print(f"Memory error {e} occurred while processing {imgPath}")
        return False


TextMaker = HuggingFacePipeline.from_model_id(
    model_id='microsoft/phi-2',
    task='text-generation',
    pipeline_kwargs={'max_new_tokens': 250}
)

prompt = PromptTemplate.from_template("""
Instruct: You're going to write a short script for an informational short form video. The video will be about the benefits of drinking water. The script should be 30 seconds long. The target audience is adults who are looking to improve their health. The script should be informative and engaging. The video will be around 30 seconds long. Place prompts for an ai image generator in brackets between text, [like this]. Don't have someone saying the text, simply write the text.
Output: [Refreshing image of water] Did you know that drinking water for can help you lose weight? [Image of a scale] Water can also help you stay focused and energized throughout the day. [Image of a person working]. So next time you're feeling tired or hungry, try drinking a glass of water. [Image of a person drinking water]. Your body will thank you. [Image of a happy person]. Stay hydrated and stay healthy. [Image of a water bottle].
Instruct: "You're goal is to write a short script about for an informational short form video. The video will be about {tag}. The script should be 30 seconds long. The target audience is {tag}. The script should be informative and engaging. The video will be around 30 seconds long. Place prompts for an ai image generator in brackets between text, [like this]. Don't have someone saying the text, simply write the text."
Output: """,)


chain = prompt | TextMaker
script = chain.invoke({"tag": "The technology of an F1 Car"})
script = script.replace(prompt.format(tag="The technology of an F1 Car"), "")
script = "[Image of an F1 car] Did you know that the technology used in F1 cars is some of the most advanced in the world? [Image of a car engine] The engines used in F1 cars are designed to be incredibly powerful and efficient. [Image of a car on a track] The aerodynamics of F1 cars are also incredibly advanced, allowing them to reach incredible speeds. [Image of a car on a track] So next time you see an F1 car, remember that it's not just a car, it's a work of art. [Image of an F1 car] The technology used in F1 cars is truly amazing. [Image of a car on a track] Stay tuned for more information on the technology of F1 cars. [Image of a car on a track]"

imageList = re.findall(r'\[.*?]', script)
imageList = [image.replace("[", "").replace("]", "").replace("\"", "") for image in imageList]
print(script, "\n", imageList)

folder = os.getcwd()
length_per_img = 0.25


for image in imageList:
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json"
    }
    data = {
        "prompt": image,
        "steps": 5
    }

    print(data)
    response = requests.post(url='http://127.0.0.1:7862/sdapi/v1/txt2img', json=data, headers=headers)

    if response.status_code == 200:
        base_filename = image.replace(" ", "")
        filename = base_filename + ".png"
        count = 1

        while os.path.exists(filename):
            filename = f"{base_filename}{count}.png"
            count += 1

        with open(filename, 'wb') as f:
            try:
                f.write(base64.b64decode(response.json()['images'][0]))
            except KeyError:
                print("Error: ", response.json())
    else:
        print(f"Request failed with status code {response.status_code}")

# Add text to images -- Untested (tested only for one image at a time), hope this works.

images = [image for image in glob.glob(os.path.join(folder, "*.png"))]

words = script.split()
image_index = 0
word_index = 0

for word in words:
    if word.startswith('[') and word.endswith(']'):
        image_index = images.index(word.strip('[]') + ".png")
    else:
        output_path = f"image_{word_index + 1}.png"
        image_on_text(word, images[image_index], output_path)
        word_index += 1

# Concat images into video -- Untested, hope this works.
mimages = [img for img in os.listdir(folder) if img.endswith(".png")]  # mimages -> Modified IMAGES
fps = 1 / length_per_img

frame = cv2.imread(os.path.join(folder, images[0]))
height, width, layers = frame.shape

video = cv2.VideoWriter("test.mp4", cv2.VideoWriter_fourcc(*"MJPG"), fps, (width, height))

for img in images:
    img_path = os.path.join(folder, img)
    frame = cv2.imread(img_path)
    video.write(frame)

video.release()

# Make TTS -- Untested, hope this works.
script = re.sub(r'\[.*?]', '', script)

words = script.split()
combined = AudioSegment.silent(duration=0)

for word in words:
    tts = gTTS(text=word, lang='en')
    tts.save("tmp.mp3")
    word_audio = AudioSegment.from_mp3("tmp.mp3")
    combined += word_audio
    combined += AudioSegment.silent(duration=int(length_per_img * 1000))

combined.export("test.mp3", format="mp3")
os.remove("tmp.mp3")

video = VideoFileClip("test.mp4")
audio = AudioFileClip("test.mp3")
video = video.set_audio(audio)

video.write_videofile("test.mp4", codec="libx264", audio_codec="aac")
