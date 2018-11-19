#!/bin/bash

# -----------------------------------------------------------------------------
# filename ... smartresize.sh
# author ..... marcus.trommen@gmx.net
# created .... 20181118
# purpose .... efficient image resizing with ImageMagick 
# see ........ https://www.smashingmagazine.com/2015/06/efficient-image-resizing-with-imagemagick
# -----------------------------------------------------------------------------


SCRIPTNAME=`basename $0`

# Version of current script as date string, formatted as 'YYYY-MM-DD hh:mm'
SCRIPT_VERSION='2018-11-18 12:00'

# ---------------------------
USAGE=`cat <<-__USAGE__
Usage: ${SCRIPTNAME} OPTIONS

Script for efficient image resizing with ImageMagick.

Parameters are separated by a blank (e.g. -m Gray or --mode Gray).
-s, --source SOURCEFILE  fully qualified filename (with absolute path and 
                      filename extension) of image file to be resized
-t, --target TARGETFILE  file name without path information and filename
                      extension.
                      HINT:
                      TARGETFILE will be placed in same direcotry as SOURCEFILE
                      and its file format will always be of type JPG
-w, --width OUTPUT_WIDTH_IN_PIXEL  horizontal output width in Pixel of 
                      TARGETFILE, this will be considered while resizing
-h, --help            optional, display this help message and exit
-v, --version         optional, print version information

example:
$> ${SCRIPTNAME} -s /home/user/image.png -w 800 -t image_800.jpg

Preconditions (on Debian like systems):

ImageMagick is installed:
$> sudo apt-get install imagemagick

__USAGE__`

# ---------------------------
# initialize variables
SOURCEFILE=''
OUTPUT_WIDTH_IN_PIXEL=''
TARGETFILE=''

# ---------------------------
# HANDLE COMMANDLINE PARAMETERS
while true; do
	case "$1" in
		--source|-s)
			shift
			SOURCEFILE="$1"
			shift
			;;
		--width|-w)
			shift
			OUTPUT_WIDTH_IN_PIXEL="$1"
			shift
			;;
		--target|-t)
			shift
			TARGETFILE="$1"
			shift
			;;
		--version|-v)
			shift
			echo "${SCRIPTNAME} version ${SCRIPT_VERSION}"
			exit 0
			;;
		--help|-h)
			echo "${USAGE}"
			exit 0
			;;
		"")
			break
			;;
		*)
			echo "ERROR: $1 wrong parameter! please refer to command line usage"
			exit 3
			;;
	esac
done


# ---------------------------
# check if necessary parameters are not empty
if [[ "$SOURCEFILE" == "" ]] || [[ "$OUTPUT_WIDTH_IN_PIXEL" == "" ]] || [[ "$TARGETFILE" == "" ]] ; then
	echo "ERROR: one of the necessary command line parameters is not set properly!"
	echo "please refer to command line usage"
	exit 1
fi


# 2) EXCTRACT SOURCE FILE DETAILS
SOURCE_PATH=$(dirname ${SOURCEFILE})
SOURCE_FILENAME=$(basename -- "${SOURCEFILE}")
SOURCE_EXTENSION="${SOURCE_FILENAME##*.}"
SOURCE_EXTENSION_LOWERCASE="${SOURCE_EXTENSION,,}"
SOURCE_FILENAME="${SOURCE_FILENAME%.*}"


# 3) EXCTRACT TARGET FILE DETAILS
TARGET_PATH=${SOURCE_PATH}
TARGET_FILENAME="${TARGETFILE}"
TARGETFILE="${TARGET_PATH}/${TARGET_FILENAME}"
TARGET_EXTENSION=".jpg"
TARGET_EXTENSION_LOWERCASE=".jpg"
TARGET_FILENAME="${TARGET_FILENAME%.*}"


# 4) ONLY JPG AND PNG FILEFORMATS ARE SUPPORTED
if [[ "${SOURCE_EXTENSION_LOWERCASE}" != "jpg" ]] && [[ "${SOURCE_EXTENSION_LOWERCASE}" != "png" ]] ; then
	echo "Only images of format 'jpg' or 'png' are supported."
	echo "File extension of SOURCEFILE is '${TARGET_EXTENSION_LOWERCASE}'!"
	exit 1
fi

if [[ "${TARGET_EXTENSION_LOWERCASE}" != "jpg" ]] && [[ "${TARGET_EXTENSION_LOWERCASE}" != "png" ]] ; then
	echo "Only images of format 'jpg' or 'png' are supported."
	echo "File extension of SOURCEFILE is '${TARGET_EXTENSION_LOWERCASE}'!"
	exit 1
fi


# 5) DO SOME PREWORK FOR MOGRIFY
IS_DIFFERENT_FORMAT='NO'
if [[ "${SOURCE_EXTENSION_LOWERCASE}" != "${TARGET_EXTENSION_LOWERCASE}" ]] ; then
	# source and target image are of different format
	IS_DIFFERENT_FORMAT='YES'
	TARGETFILE="${TARGET_PATH}/${TARGET_FILENAME}.${SOURCE_EXTENSION}"
fi
cp ${SOURCEFILE} ${TARGETFILE}


# 6) DO RESIZE AND OPTIMIZE THE IMAGE
COMMAND="mogrify"

#COMMAND="${COMMAND} -path ${TARGETPATH}"

if [[ "${IS_DIFFERENT_FORMAT}" == "YES" ]] ; then
	COMMAND="${COMMAND} -format ${TARGET_EXTENSION_LOWERCASE}"
fi

# RESAMPLING
# Triangle defines a "bilinear interpolation" resampling filter for the 
# "resize" function, used by "thumbnail" option
# It determines pixel color by looking at a support area of neighboring pixels 
# and produces a weighted average of their colors. the best to specify this 
# is to set the support area at two pixels using the 
# "-define filter:support=2" setting.
COMMAND="${COMMAND} -filter Triangle -define filter:support=2"

# the thumbnail function uases a three-step process to resize images:
# 1)  It resizes the image to five times the output size using the 
#     "-sample" function, which has its own built-in resampling filter that’s 
#     similar to the nearest-neighbor approach
# 2)  It resizes the image to its final output size using 
#     the basic "-resize" filter.
# 3)  It strips meta data from the image.
COMMAND="${COMMAND} -thumbnail ${OUTPUT_WIDTH_IN_PIXEL}"

# SHARPENING
# Images pretty often get a little blurry when resized, so programs such as 
# Photoshop will often apply some sharpening afterwards to make the images a 
# little crisper. unsharp filter — which, despite its name, actually does 
# sharpen the image.
# Unsharp filters work by first applying a Gaussian blur to the image. The 
# first two values for the unsharp filter are the radius and sigma, 
# respectively — in this case, both have a value of 0.25 pixels. These values 
# are often the same and, combined, tell ImageMagick how much to blur the image.
# After the blur is applied, the filter compares the blurred version to the 
# original, and in any areas where their brightness differs by more than a 
# given threshold (the last value, 0.065), a certain amount of sharpening is 
# applied (the third value, 8). The exact meanings of the threshold and 
# numerical amounts aren’t very important; just remember that a higher 
# threshold value means that sharpening will be applied less often, and a 
# higher numerical amount means that the sharpening will be more intense 
# wherever it is applied.
COMMAND="${COMMAND} -unsharp 0.25x0.25+8+0.065"

# DITHERING
# Dithering is a process that is intended to mitigate color banding by adding 
# noise into the color bands to create the illusion that the image has more 
# colors. In theory, dithering seems like a good idea when you posterize; it 
# helps the viewer perceive the result as looking more like the original.
# Unfortunately, ImageMagick has a bug that ruins images with transparency when 
# dithering is used like this. So, it’s best to turn dithering off 
# with "-dither None".
# Luckily, even without dithering, the posterized images still look good.
COMMAND="${COMMAND} -dither None"

# COLOR REDUCTION
# he biggest reasons why resized images get bloated is because of all the 
# extra colors in them. So, try to reduce the number of colors — but not so 
# much that the quality suffers.
# One way to reduce colors is with "posterization", a process in which 
# gradients are reduced to bands of solid color. Posterization reduces colors 
# to a certain number of color levels — that is, the number of colors available 
# in each of the red, green and blue color channels that images use. 
# The total number of colors in the final image will be a combination of the 
# colors in these three channels.
# Posterization can drastically reduce file size, but can also drastically 
# change how an image looks. With only a few color levels, it creates an effect 
# like what you might see in 1970s rock posters, with a few discrete bands of 
# color. With many color levels — for example, 136 — you get a smaller file 
# without losing much image quality.
COMMAND="${COMMAND} -posterize 136"

if [[ "${TARGET_EXTENSION_LOWERCASE}" == "jpg" ]] ; then
	# QUALITY AND COMPRESSION
	# With lossy image formats such as JPEG, quality and compression go hand in 
	# hand: the higher the compression, the lower the quality and the lower the 
	# file size. We could drastically reduce file size by setting a high JPEG 
	# compression factor, but this would also drastically reduce quality.
	# A balance is needed.
	# It turns out that JPEG quality scales are not defined in a specification or 
	# standard, and they are not uniform across encoders.
	# A quality of 60 in Photoshop might be the same as a quality of 40 in one 
	# program, quality B+ in another and quality fantastico in a third. 
	# It looks like that Photoshop’s 60 is closest to "-quality 82" in ImageMagick.
	COMMAND="${COMMAND} -quality 82"
	COMMAND="${COMMAND} -define jpeg:fancy-upsampling=off"
else
	# PNG COMPRESSION FILTERING
	COMMAND="${COMMAND} -define png:compression-filter=5"
	COMMAND="${COMMAND} -define png:compression-level=9"
	COMMAND="${COMMAND} -define png:compression-strategy=1"
	COMMAND="${COMMAND} -define png:exclude-chunk=all"
fi

COMMAND="${COMMAND} -interlace none"

# COLOR SPACE
# While not strictly a matter of color reduction, setting an image’s color space
# is a related concept. The color space defines what colors are available for 
# an image.
# sRGB was created to be the one true king of color spaces on the Internet. It 
# has been endorsed by the W3C and other standards bodies; it is the required 
# color space in the CSS Color Module Level 3 and the SVG specification and is 
# the assumed color space of the WebP specification; and it is explicitly 
# referenced in the PNG specification. It’s also the default color space in 
# Photoshop. In short, sRGB is the color space of choice for the web platform, 
# and, assuming you want your images to render predictably, using it is 
#probably a good idea.
COMMAND="${COMMAND} -colorspace sRGB"

# COMMAND="${COMMAND} -strip INPUT_PATH"

COMMAND="${COMMAND} ${TARGETFILE}"

# run the command
${COMMAND}
ERROR_CODE=$?
if [[ "${RROR_CODE}" -ne 0 ]] ; then
	echo "ERROR ${ERROR_CODE} while mogrify command"
	exit ${ERROR_CODE}
fi

# remove the intermediate file in case of different image formats
if [[ "${IS_DIFFERENT_FORMAT}" == "YES" ]] ; then
	rm ${TARGETFILE}
	
	ERROR_CODE=$?
	if [[ "${RROR_CODE}" -ne 0 ]] ; then
		echo "ERROR ${ERROR_CODE} while removing file"
		exit ${ERROR_CODE}
	fi
fi
