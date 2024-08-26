```
 :::===  :::      :::====  :::====  :::====  :::===== :::====
 :::     :::      :::  === :::  === :::  === :::      :::  ===
  =====  ===      ===  === =======  =======  ======   =======
     === ===      ===  === ===      ===      ===      === ===
 ======  ========  ======  ===      ===      ======== ===  ===
```


# Slopper
Slopper is an AI program that creates algorithmically generated short form content.

To run it, you need to install `requirements.txt`.
You also need to install [Stable Diffusion](https://github.com/AUTOMATIC1111/stable-diffusion-webui), and run it with the commands `--api --cors-allow-origins * --use-cpu all --precision full --no-half --skip-torch-cuda-test`. Technically `--use-cpu` and `--skip-torch-cuda-test` are optional, but I need them for Stable diffusion to work, and I've only tested with it.

You then need to run `Slopper.py`. Slopper takes the following arguments:
```
--tpf: Time per frame in the video. It is the recipricol of the frames per second (fps = 1/tpf). The default is 0.25 seconds.
--model: The model id of the text generation model. The system prompt, and default, has only been tested with microsoft/phi-2
--max-new-tokens: Essentially the length of the created script in tokens. The default is 250.
--folder: The new folder to place the images and videos created by the script. The default is the home directory.
--name: Name of the final video. The default is test.mp4
--aname: Name of the temporary audio file to be created. Default is test.mp3.
--bVideo: File path of the video to be played at the bottom of the screen. Named after background video.
--targetWidth: Width of the final video. The default is 400.
--tag: What you want your video to be about!
--imageURL: URL of the stable diffusion API, gotten from the site that opens up when you run stable diffusion. The default is http://127.0.0.1:7860/
--steps: Number of steps for the images. Higher steps makes crisper and better images, but takes longer (especially with no GPU acceleration)
```

## Example
This is an example video for F1 Cars:
[![Example video](https://upload.wikimedia.org/wikipedia/commons/thumb/8/8f/Max_Verstappen_2022.jpg/1920px-Max_Verstappen_2022.jpg)]([https://streamable.com/u67swo](https://www.youtube.com/watch?v=5CVAb7wuTOE))
