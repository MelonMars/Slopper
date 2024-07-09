import argparse
import main
import os

parser = argparse.ArgumentParser(description='Slopper')
parser.add_argument('--tpf', type=float, help="Time each frame is up, fps = 1/tpf", default=0.25)
parser.add_argument("--model", type=str, help="huggingface model id", default="microsoft/phi-2")
parser.add_argument("--max_new_tokens", type=int, help="Max new tokens to generate", default=250)
parser.add_argument("--folder", type=str, help="Folder to place new video and images", default=os.getcwd())
parser.add_argument("--name", type=str, help="Name of the video", default="test.mp4")
args = parser.parse_args()

script = main.create_script(args.model, args.max_new_tokens)
main.create_images(script, args.folder)
main.addTextToImages(script, args.folder)
main.create_video(args.tpf, args.folder, args.name)
