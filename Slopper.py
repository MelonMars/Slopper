import argparse
import model
import os

parser = argparse.ArgumentParser(description='Slopper')
parser.add_argument('--tpf', type=float, help="Time each frame is up, fps = 1/tpf", default=0.25)
parser.add_argument("--model", type=str, help="huggingface model id", default="microsoft/phi-2")
parser.add_argument("--max_new_tokens", type=int, help="Max new tokens to generate", default=250)
parser.add_argument("--folder", type=str, help="Folder to place new video and images", default=os.getcwd())
parser.add_argument("--name", type=str, help="Name of the video", default="test.mp4")
parser.add_argument("--aname", type=str, help="Name of the temporary audio file", default="test.mp3")
parser.add_argument("--bVideo", type=str, help="Path to the video to played on the bottom of the screen. Will be cut to size of the final video. IGNORES THE FOLDER VARIABLE", required=True)
parser.add_argument("--targetWidth", type=int, help="Width of the final video", default=480)
parser.add_argument("--tempVideo", type=str, help="Name of the temporary video file", default="test.mp4")
parser.add_argument("--tag", type=str, help="What you want your video to be about", required=True)
parser.add_argument("--imageURL", type=str, help="URL of the stable diffusion API", default="http://127.0.0.1:7860/")
parser.add_argument("--steps", type=int, help="Number of steps to take in the stable diffusion API", default=5)
args = parser.parse_args()

script = model.create_script(args.model, args.max_new_tokens, args.tag)
model.create_images(script, args.folder, args.imageURL, args.steps)
model.addTextToImages(script, args.folder)
model.create_video(args.tpf, args.folder, args.tempVideo)
model.create_mp3(script, args.folder, "test.mp3", args.tpf)
model.compositeVideo(args.tempVideo, args.aname, args.bVideo, args.name, args.folder, args.targetWidth)
