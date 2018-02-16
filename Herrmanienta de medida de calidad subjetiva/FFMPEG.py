import os,	subprocess
from multiprocessing import Process

def launchCommand(refVideo, fps, crf, size, output):
	print()
	command="ffmpeg -y -i "+refVideo+" -r "+fps+" -crf "+crf+" -vf scale="+size+" -an -sn "+output+" -vstats_file "+output+".log"
	print(command)
	os.system(command)
	return command
	
#	Change resolution
def reSize(width, height, res_step):
	height = int(height-res_step)
	width =  int(height*16/9)
	return width,height

#def getBitrate(refVideo, fps, crf, size, output):
def getBitrate(output):

	#launchCommand(refVideo, fps, crf, size, output)
	statistics_file= open(output+".log","r")

	last_line = statistics_file.readlines()[-1]
	avg_bitrate=float(last_line.split(" ")[-3].split("kbits/s")[0])
	statistics_file.close()
	
	return avg_bitrate



#def launchVideo(video1, video2):
def launchVideo(video1, video2,screenWmax,screenHmax):
	#command = ["ffplay" " -x" " 1280" " -y" " 360" " -autoexit" " -window_title" " \"Video A <<<<<------>>>>> Video B\"" "-f" " lavfi" " movie=\"+video1+\",scale=1280/2:720/2[v0];movie=\"+video2+\",scale=1280/2:720/2[v1];[v0][v1]hstack"]
	
	#print(command)
	#p=subprocess.check_output(command.split(" "))
	#p=subprocess.check_output(command)
	#subprocess.Popen(command.split(" "))

	#command = "ffplay  -x  1280  -y  360  -autoexit  -window_title  \"Video A <<<<<------>>>>> Video B\" -f  lavfi  \"movie="+video1+",scale=1280/2:720/2[v0];movie="+video2+",scale=1280/2:720/2[v1];[v0][v1]hstack\""
	#os.system(command)
	
	#subprocess.Popen(['ffplay', '-x', '1280', '-y', '360', '-autoexit', '-window_title', 'VIDEO A <<<----->>> VIDEO B', '-f', 'lavfi', 'movie='+video1+',scale=1280/2:720/2[v0];movie='+video2+',scale=1280/2:720/2[v1];[v0][v1]hstack'])
	#p = subprocess.Popen(['ffplay', '-x', '1280', '-y', '360', '-autoexit', '-window_title', 'VIDEO A <<<----->>> VIDEO B', '-f', 'lavfi', 'movie='+video1+',scale=1280/2:720/2[v0];movie='+video2+',scale=1280/2:720/2[v1];[v0][v1]hstack'],shell=False)
	#p = subprocess.Popen(['ffplay', '-x', '1664', '-y', '468', '-autoexit', '-window_title', 'VIDEO A <<<----->>> VIDEO B', '-f', 'lavfi', 'movie='+video1+',scale=1664/2:936/2[v0];movie='+video2+',scale=1664/2:936/2[v1];[v0][v1]hstack'],shell=False)
	p = subprocess.Popen(['ffplay', '-x', str(screenWmax*2), '-y', str(screenHmax), '-autoexit', '-window_title', 'VIDEO A <<<----->>> VIDEO B', '-f', 'lavfi', 'movie='+video1+',scale='+str(screenWmax)+':'+str(screenHmax)+'[v0];movie='+video2+',scale='+str(screenWmax)+':'+str(screenHmax)+'[v1];[v0][v1]hstack'],shell=False)
	##p = subprocess.Popen(['ffplay', '-x', '1280', '-y', '360', '-autoexit', '-window_title', 'VIDEO A <<<----->>> VIDEO B', '-f', 'lavfi', 'movie='+video1+',scale=1280/2:720/2[v0];movie='+video2+',scale=1280/2:720/2[v1];[v0][v1]hstack'],shell=False)
	#p = subprocess.Popen(['ffplay', '-x', '2560', '-y', '720', '-autoexit', '-window_title', 'VIDEO A <<<----->>> VIDEO B', '-f', 'lavfi', 'movie='+video1+',scale=2560/2:720[v0];movie='+video2+',scale=2560/2:720[v1];[v0][v1]hstack'],shell=False)
	p.wait()
	#subprocess.check_output(['ffplay', '-x', '1280', '-y', '360', '-autoexit', '-window_title', 'VIDEO A <<<----->>> VIDEO B', '-f', 'lavfi', 'movie='+video1+',scale=1280/2:720/2[v0];movie='+video2+',scale=1280/2:720/2[v1];[v0][v1]hstack'])
	
	#subprocess.call(['ffplay', '-x', '1280', '-y', '360', '-autoexit', '-window_title', 'VIDEO A <<<----->>> VIDEO B', '-f', 'lavfi', 'movie='+video1+',scale=1280/2:720/2[v0];movie='+video2+',scale=1280/2:720/2[v1];[v0][v1]hstack'])
	

# Read the parameters from init file
def getConfiguration(list_var, configFile):	
	variables=[];

	conf_file= open("./config/"+configFile+".conf","r")

	for i,line in enumerate(conf_file):

		if(line[0]!='#'):
			# print(line)
			out=line.split('\n')[0].split(' = ')
			if out[0] in list_var:
				variables.append(out[1])

	conf_file.close()
	return variables[0],list(map(int,variables[1:]))