'''
Mixed_video.py

Make a video from a folder of images.

The idea here is to print out the waveform (as .png file)
underneath the text file in series.

This helps show time-series data!


'''
import cv2, os, shutil, librosa 
import soundfile as sf
import speech_recognition as sr_audio
import matplotlib.pyplot as plt
import numpy as np


def transcribe_pocket(filename):
    # transcribe the audio (note this is only done if a voice sample)
    try:
        r=sr_audio.Recognizer()
        with sr_audio.AudioFile(filename) as source:
            audio = r.record(source) 
        text=r.recognize_sphinx(audio)
    except:
        text=''
    print(text)

    # get audio features
    y, sr = librosa.load(filename)
    rmse=np.mean(librosa.feature.rmse(y)[0])*1000

    # write transcript to file (for archive)
    g=open(filename[0:-4]+'.txt','w')
    g.write(text)
    g.close()

    # remove wavfile 
    os.remove(filename)

    return text, rmse 

def make_fig(filename, transcriptions, x, y):
    plt.scatter(x, y, color='blue')
    for i, transcript in enumerate(transcriptions):
        plt.annotate(transcript, (x[i],y[i]))

    # write labels and save fig 
    plt.xlabel('time (seconds)')
    plt.ylabel('root mean square power (average)')

    plt.savefig(filename)

# change to data directory 
os.chdir('data')
curdir=os.getcwd()
wavfile=input('what .wav file in the ./data directory would you like to make a mixed feature video? \n')

# make a folder, delete the folder if it is there 
folder=wavfile[0:-4]

try:
	os.mkdir(folder)
	os.chdir(folder)
except:
	shutil.rmtree(folder)
	os.mkdir(folder)
	os.chdir(folder)

# now copy the file into the folder 
shutil.copy(curdir+'/'+wavfile, curdir+'/'+folder+'/'+wavfile)

# now break up the file into 1 second segments 
data, samplerate = sf.read(wavfile)
os.remove(wavfile)
duration=int(len(data)/samplerate)

for i in range(duration):
    try:
        sf.write(str(i)+'.wav', data[samplerate*(i):samplerate*(i+1)], samplerate)
    except:
        pass 

# now get wavfiles and sort them 
files=os.listdir()
wavfiles=list()
for i in range(len(files)):
	if files[i][-4:]=='.wav':
		wavfiles.append(files[i])
wavfiles=sorted(wavfiles)

# now transcribe each of these wav files and remove them 
# save as .txt files 
transcriptions=list()
x=list()
y=list()

for i in range(len(wavfiles)):
	# now make image from these transcripts 
	text, rmse=transcribe_pocket(wavfiles[i])

	# update lists 
	x.append(i)
	y.append(rmse)
	transcriptions.append(text)

	# make audio plot and save as filename 
	make_fig(str(i)+'.png',transcriptions,x,y)

# now get all the .png files in directory and sort by number 
listdir=os.listdir()
pngs=list()
for i in range(len(listdir)):
	if listdir[i][-4:]=='.png':
		pngs.append(listdir[i])

pngs=sorted(pngs,key=lambda x: int(os.path.splitext(x)[0]))
print(pngs)

# now make video from pngs 
video_name = 'mixed_video.avi'

img=cv2.imread(pngs[0])
height, width, layers = img.shape
video = cv2.VideoWriter(video_name,-1,1,(width,height))

for i in range(len(pngs)):
	video.write(cv2.imread(pngs[i]))

cv2.destroyAllWindows()
video.release()
