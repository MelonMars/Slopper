"""
 :::===  :::      :::====  :::====  :::====  :::===== :::====
 :::     :::      :::  === :::  === :::  === :::      :::  ===
  =====  ===      ===  === =======  =======  ======   =======
     === ===      ===  === ===      ===      ===      === ===
 ======  ========  ======  ===      ===      ======== ===  ===

https://patorjk.com/software/taag/#p=display&f=USA%20Flag&t=Slopper
"""

# TODO:
# -Fix error `OSError: [Errno 22] Invalid argument: 'C:\\Users\\carte\\PycharmProjects\\Slopper\\Slopper\\Did you know that the technology used in F1 cars is some of the most advanced in the world?'`, I THINK IT'S PASSING THE RANDOM TEXT INTO "imgPath"
# -Fix all warnings
# -Fix all weak warnings
# -Fix all typos

from langchain_huggingface.llms import HuggingFacePipeline
from langchain.prompts import PromptTemplate
import re, os, glob, cv2, requests, base64
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
from pydub import AudioSegment
from moviepy.editor import VideoFileClip, AudioFileClip


def image_on_text(text: str, imgPath: str, outputPath: str):
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

    with Image.open(imgPath) as img:
        I1 = ImageDraw.Draw(img)
        image_width, image_height = img.size

        font = ImageFont.truetype("OpenSans-Bold.ttf", 65)

        text_bbox = I1.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        position = ((image_width - text_width) / 2, (image_height - text_height) / 2)

        for offset in [(3, 3), (-3, 3), (3, -3), (-3, -3)]:
            I1.text((position[0] + offset[0], position[1] + offset[1]), text, font=font, fill=(0, 0, 0))

        I1.text(position, text, font=font, fill=(255, 255, 255))
        img.save(new_output_path)


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


imageList = re.findall(r'\[.*?\]', script)
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
    with open(image.replace(" ", "") + ".png", 'wb') as f:
        try:
            f.write(base64.b64decode(response.json()['images'][0]))
        except:
            print("Error: ", response.json())

# Add text to images -- Untested (tested only for one image at a time), hope this works.
images = [image in glob.glob(os.path.join(folder, "*.png"))]
#  if image.startswith("output_") else None

pattern = re.compile(r'\[(.*?)\] (.*?)(?=\[|$)')
matches = pattern.findall(script)

for i, (image_desc, text) in enumerate(matches):
    if i < len(images):
        image_path = images[i]
        output_path = f"output_{i}.png"
        image_on_text(image_path, text.strip(), output_path)

#Concat images into video -- Untested, hope this works.
mimages = [img for img in os.listdir(folder) if img.endswith(".png")]  #mimages -> Modified IMAGES
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
script = re.sub(r'\[.*?\]', '', script)

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
