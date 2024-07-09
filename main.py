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
import pyttsx3
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
from pydub import AudioSegment
from moviepy.editor import VideoFileClip, AudioFileClip


def get_numeric_part(filename):
    match = re.search(r'_(\d+)\.png$', filename)
    return int(match.group(1)) if match else float('inf')


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
        # print("Text:", txt)

    except MemoryError as e:
        print(f"Memory error {e} occurred while processing {imgPath}")
        return False


def create_script(model: str, max_new_tokens: int) -> str:
    TextMaker = HuggingFacePipeline.from_model_id(
        model_id=model,
        task='text-generation',
        pipeline_kwargs={'max_new_tokens': max_new_tokens}
    )

    prompt = PromptTemplate.from_template("""
    Instruct: You're going to write a short script for an informational short form video. The video will be about the benefits of drinking water. The script should be 30 seconds long. The target audience is adults who are looking to improve their health. The script should be informative and engaging. The video will be around 30 seconds long. Place prompts for an ai image generator in brackets between text, [like this]. Don't have someone saying the text, simply write the text.
    Output: [Refreshing image of water] Did you know that drinking water for can help you lose weight? [Image of a scale] Water can also help you stay focused and energized throughout the day. [Image of a person working]. So next time you're feeling tired or hungry, try drinking a glass of water. [Image of a person drinking water]. Your body will thank you. [Image of a happy person]. Stay hydrated and stay healthy. [Image of a water bottle].
    Instruct: "You're goal is to write a short script about for an informational short form video. The video will be about {tag}. The script should be 30 seconds long. The target audience is {tag}. The script should be informative and engaging. The video will be around 30 seconds long. Place prompts for an ai image generator in brackets between text, [like this]. Don't have someone saying the text, simply write the text."
    Output: """, )

    chain = prompt | TextMaker
    script = chain.invoke({"tag": "The technology of an F1 Car"})
    script = script.replace(prompt.format(tag="The technology of an F1 Car"), "")

    return script


folder = os.getcwd()
length_per_img = 0.25


def create_images(script: str, folder: str):
    imageList = re.findall(r'\[.*?]', script)
    imageList = [image.replace("[", "").replace("]", "").replace("\"", "") for image in imageList]
    print(script, "\n", imageList)

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
            filename = folder + "\\" + base_filename + "1.png"
            count = 2

            while os.path.exists(filename):
                filename = f"{folder}\\{base_filename}{count}.png"
                count += 1

            with open(filename, 'wb') as f:
                try:
                    f.write(base64.b64decode(response.json()['images'][0]))
                except KeyError:
                    print("Error: ", response.json())
        else:
            print(f"Request failed with status code {response.status_code}")


def addTextToImages(script: str, folder: str):
    images = [image for image in glob.glob(os.path.join(folder, "*.png"))]
    print(images)

    pattern = re.compile(r'(\[.*?\])|(\w+\'?\w*)')
    matches = pattern.findall(script)

    image_count = {}
    word_index = 0

    for match in matches:
        image_placeholder, word = match

        if image_placeholder:
            # Extract the image name from the placeholder and increment the count
            image_name = image_placeholder.strip('[]').replace(' ', '')
            if image_name not in image_count:
                image_count[image_name] = 1
            else:
                image_count[image_name] += 1
            image_index = images.index(f"{os.getcwd()}\\{image_name}{image_count[image_name]}.png")
        elif word:
            # Generate the output path and call the image_on_text function
            output_path = f"image_{word_index + 1}.png"
            image_on_text(word, images[image_index], output_path)
            word_index += 1


# Add text to images -- Untested (tested only for one image at a time), hope this works.
script = "[Image of an F1 car] Did you know that the technology used in F1 cars is some of the most advanced in the world? [Image of a car engine] The engines used in F1 cars are designed to be incredibly powerful and efficient. [Image of a car on a track] The aerodynamics of F1 cars are also incredibly advanced, allowing them to reach incredible speeds. [Image of a car on a track] So next time you see an F1 car, remember that it's not just a car, it's a work of art. [Image of an F1 car] The technology used in F1 cars is truly amazing. [Image of a car on a track] Stay tuned for more information on the technology of F1 cars. [Image of a car on a track] "


def create_video(lpi: float, folder: str, video_name: str):
    # Concat images into video
    mimages = [img for img in os.listdir(folder) if
               img.endswith(".png") and img.startswith("image_")]  # mimages -> Modified IMAGES

    mimages = sorted(mimages, key=get_numeric_part)

    print(mimages)
    fps = 1 / lpi

    print(os.path.join(folder, mimages[0]))
    frame = cv2.imread(os.path.join(folder, mimages[0]))
    height, width, layers = frame.shape

    video = cv2.VideoWriter(video_name, 0, fps, (width, height))

    for img in mimages:
        video.write(cv2.imread(os.path.join(folder, img)))

    cv2.destroyAllWindows()
    video.release()


def create_mp3(script: str, folder: str, file: str, rate: float):
    script = re.sub(r'\[.*?]', '', script)  # Remove image placeholders
    rate = (1/rate) * 60
    engine = pyttsx3.init()
    engine.setProperty('rate', rate)
    engine.save_to_file(script, os.path.join(folder, file))
    engine.runAndWait()


create_video(length_per_img, folder, "test.mp4")
create_mp3(script, folder, "test.mp3", length_per_img)

videoClip = VideoFileClip("test.mp4")
audioClip = AudioFileClip("test.mp3")
finalClip = videoClip.set_audio(audioClip)

finalClip.write_videofile("final.mp4")
