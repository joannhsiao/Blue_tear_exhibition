# Blue_tears

## Pre-Requisites
1. Open anaconda and activate your environment.
	```bash
	conda activate your_env
	```
2. Open the blue tears system directory.
	```bash
	cd ./Blue_tears
	```
3. Install all the required packages by type this command below:
	```bash
	pip install -r requirements.txt
	```

	> **NOTICE!** : If you could not install `dlib` by `pip/pip3` successfully, try `conda install dlib` under your environment.

4. Download all the data from google drive. Follow the [rules](#data-collection) as below.


## Instructions
All the instructions here only need one hand!!
1. To manipulate the sun: `scissors` hand gesture
2. To turn on the light: open your palm
3. To turn off the light: close your palm
4. To pray for the blue tears: `thumb up` hand gesture
5. To zoom in on the part of the blue tears: `OK` hand gesture
	
	> :warning: 
	> After praying for the blue tears, you need to **wait for a few seconds** then the blue tears would show up.
	> While blue tears or the sunset appeared, you **could not do anything** then. It will disappear after around 30 seconds. After then, you could manipulate everything again.


## Data Collection
- The size of the videos are large so we didn't upload them here, all the video are on our google drive. Download the materials from [here](https://drive.google.com/drive/u/0/folders/12hI5uB_-W8tm1z1VPcJoLmeoTQmb6mGd) before you run the program.
- Put them under the directory `./data/`, then rename `藍眼淚呈現v3.mp4` as `blue_tears_v3.mp4`, `燈塔轉動.mp4` as `rotate.mp4` and `陽光下的淚Sun.mp4` as `sun.mp4`.


## How to use?
- Scripts: 
	- `app.py`: server
	- `detection.py`: detect gesture and distance and display images/videos
	- `detect_gesture.py`: gesture recognition
- Usage: 
	```bash
	python app.py
	```
	And then paste `127.0.0.1:6200` to the browser.

## Reference
1. Mediapipe
2. Opencv
3. Kazuhito Takahashi, 2020 "hand-gesture-recognition-mediapipe". [Source code](https://github.com/Kazuhito00/hand-gesture-recognition-using-mediapipe)
