#! /bin/bash
#
# Test video Script
#

# Force applications to use the default language
LC_ALL=C 
export LC_ALL

# Make sure we are running under a compatible shell
try_exec(){
	echo "Trying shell $1"
	type "$1" > /dev/null 2>&1 && exec "$@"
}

show_help(){
	cat <<EOF
Usage: sh tesume.sh <input_file>
input_file has to be a 10s, mp4 video file encoded in H.264 

To set several bitrates, fps, color format and resolutions edit for loop in line 100
input_file should be a high resolution, high quality video 
EOF
	exit 0
}

# Checking argmuents
if [ $# -ne 1 ]
	then 
		echo "Invalid arguments."
		echo "usage: $0 <input_file>"
		echo "  - input_file should be an MP4 video encoded in h264"
		echo "Aborting."
		exit 1
fi

# Show help
case "$1" in
	--help|-h) show_help
	;;
	*)
	;;
esac

# Checking if ffmpeg is installed
echo "Checing if ffmpeg is installed in your computer..."
type ffmpeg >/dev/null 2>&1 || { echo >&2 "I require ffmpeg but it's not installed. Aborting."; exit 1; }
#hash ffmpe 2>/dev/null || { echo >&2 "I require ffmpeg but it's not installed. Aborting."; exit 1; }
echo "OK"
echo " "
sleep 1

clear
echo " "
echo "******************"
echo "*  ARQUEOPTERIX  *"
echo "******************"
#echo " "
echo "Video generation script for testing subjetive measures"
echo "------------------------------------------------------"
echo " "

# Remove the file suffix path and extract file name with extension
ifile=${1##*/}
echo "Detected input file argument: $ifile"
# Extract path where the input file is.
DIR=$(dirname "$1")
#echo "Videos will be generated in $DIR/TESUME"
# Set the working directory and create generated video folder
cd $DIR
mkdir -p TESUME
DIR2="$DIR/TESUME"
#cd TESUME/
#echo $PWD
echo "Videos will be generated in $DIR2"
echo ""

# Checking if directory TESUME is empty
if [ "$(ls -A $DIR2)" ]; then
	echo "Directory TESUME is not empty."
	echo "If you continue some files may be overwritten"
	read -r -p "Do you want to continue? [y/N] " response
	case "$response" in
		[nN][oO]|[nN]) 
			echo "Please, move all files to other directory before run again. Aborting"
			exit 1
			;;
		*)
			echo "Files will be overwritten"	
			;;
	esac
fi

#Copy reference video in TESUME directory
cp -f $ifile "$DIR2/video_ref.mp4"
echo "-----> Reference video has been generated"

cd $DIR2

for bitrate in 5000 40 #3000 2000 1000 500 #in kbit/s
do
	for fps in 24 2 #20 15 10 5 1
	do
		for size in "480:270" "240:136" #divisible by 2
 		do
 			width=${size%:*}
 			height=${size##*:}
 			for color in "yuv420p" "gray" #"yuv444p" "yuv422p" #see ffmpeg compatible formats
 			do
 				ffmpeg -y -i video_ref.mp4 -r "$fps" -b:v "$bitrate"k -minrate "$bitrate"k -vf scale="$size" -vf format="$color" video_"$width"x"$height"_"$fps"fps_"$bitrate"k_"$color".mp4
				echo "-----> "$width"x"$height" - "$fps"fps - "$bitrate"k - "$color" video has been generated"
			done

		done
	done
done

echo ""
echo "Successfully completed"
echo ""
