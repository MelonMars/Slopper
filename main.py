from langchain_huggingface.llms import HuggingFacePipeline
from langchain.prompts import PromptTemplate
import re, os, glob


TextMaker = HuggingFacePipeline.from_model_id(
    model_id='microsoft/phi-2',
    task='text-generation',
    device=0,
    pipeline_kwargs={'max_new_tokens': 100}
)

prompt = PromptTemplate.from_template(
    """
Instruct: You're going to write a short script for an informational short form video. The video will be about the benefits of drinking water. The script should be 30 seconds long. The target audience is adults who are looking to improve their health. The script should be informative and engaging. The video will be around 30 seconds long. Place prompts for an ai image generator in brackets between text, [like this]. Don't have someone saying the text, simply write the text.
Output: [Refreshing image of water] Did you know that drinking water for can help you lose weight? [Image of a scale] Water can also help you stay focused and energized throughout the day. [Image of a person working]. So next time you're feeling tired or hungry, try drinking a glass of water. [Image of a person drinking water]. Your body will thank you. [Image of a happy person]. Stay hydrated and stay healthy. [Image of a water bottle].
Instruct: "You're goal is to write a short script about for an informational short form video. The video will be about {tag}. The script should be 30 seconds long. The target audience is {tag}. The script should be informative and engaging. The video will be around 30 seconds long. Place prompts for an ai image generator in brackets between text, [like this]. Don't have someone saying the text, simply write the text."
Output: 
"""
)

chain = prompt | TextMaker
script = chain.invoke({"tag": "The technology of an F1 Car"})

imageList = re.findall(r'\[.*?\]', script)
imageList = [image.replace("[", "").replace("]", "").replace("\"", "") for image in imageList]
print(script, "\n", imageList)

#Make images, put into a folder (can't test imageTest, bc my wifi is horrendous rn)
#Save ALL images as the description of the image, no spaces, .jpg (e.g. [Refreshing image of water] -> Refreshingimageofwater.jpg)


for img in glob.glob(os.path.join(os.getcwd(), "*.jpg")):
    pass