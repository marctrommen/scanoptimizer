#!/bin/bash

# -----------------------------------------------------------------------------
# Script for scanning pages from a scanner via SANE, reduce the file size and
# finally convert the scanned page into a DIN-A4 PDF.
# Size reduction and format conversion is done via ImageMagick.
#
# Preconditions (on Debian like systems):
#
# 1) SANE is installed:
#    $> sudo apt-get install libsane
#
# 2) ImageMagick is installed:
#    $> sudo apt-get install imagemagick
#
# 3) "PDF Split and Merge" (pdfsam) is installed:
#    $> sudo apt-get install pdfsam
#
# Hints:
#
# 1) for getting a list of available local scan devices, run on command line:
#
#    $> scanimage --list-devices
#
# 2) for getting a list of available scan options for a certain scan device,
#    run on command line:
#
#    $> scanimage --help --device-name DEVICE
#
#   example:
#   $> scanimage --help --device-name 'hpaio:/usb/Officejet_Pro_8600?serial=CN2C1CXJGN05KC'
# -----------------------------------------------------------------------------
# file name ..... scan_and_optimize.sh
# last change ... 2018-02-19
#
# The MIT License (MIT)
#
# Copyright (c) 2018 Marcus Trommen (mailto:marcus.trommen@gmx.net)
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# -----------------------------------------------------------------------------

SCRIPTNAME=`basename $0`

# Version of current script as date string, formatted as 'YYYY-MM-DD hh:mm'
SCRIPT_VERSION='2018-02-19 20:00'

# current device
DEVICE='hpaio:/usb/Officejet_Pro_8600?serial=CN2C1CXJGN05KC'
#DEVICE='hpaio:/net/Officejet_Pro_8600?zc=HP843497A42027'
DEVICENAME='Hewlett-Packard Officejet_Pro_8600 all-in-one'

# ---------------------------
USAGE=`cat <<-__USAGE__
Usage: ${SCRIPTNAME} OPTIONS

Script for scanning pages from a scanner via SANE, reduce the file size and
finally convert the scanned page into a DIN-A4 PDF.
Size reduction and format conversion is done via ImageMagick.

Parameters are separated by a blank (e.g. -m Gray or --mode Gray).
-w, --wdir WORKING_DIRECTORY  existing working directory for storing all files
-n, --name FILE_NAME  file name without file extension for scan output
-m, --mode COLORMODE  available scan modes, depending from scan device
                      currently available: 'Gray' or 'Color'
-o, --original TYPE   original to scan consists mainly of type 'text' or 
                      'graphics'
-r, --resolution RESOLUTION  available scan resolutions, depending from 
                      scan device,  currently available: 75 100 200 300
                      recommended is 200
-c, --count OPTCOUNT  repeated runs of file size reduction, recommended is 7
-d, --device          currently used scan device
-h, --help            optional, display this help message and exit
-v, --version         optional, print version information

Preconditions (on Debian like systems):

1) SANE is installed:
   $> sudo apt-get install libsane

2) ImageMagick is installed:
   $> sudo apt-get install imagemagick

3) "PDF Split and Merge" (pdfsam) is installed:
   $> sudo apt-get install pdfsam

Hints:

1) for getting a list of available local scan devices, run on command line:

   $> scanimage --list-devices

2) for getting a list of available scan options for a certain scan device,
   run on command line:

   $> scanimage --help --device-name DEVICE

   example:
   $> scanimage --help --device-name ${DEVICE}
__USAGE__`

# ---------------------------
# initialize variables
FILENAME=''
WORKING_DIRECTORY=''
COLORMODE=''
RESOLUTION=''
OPTCOUNT=''
TYPE=''


# ---------------------------
# check command line parameters
while true; do
	case "$1" in
		--wdir|-w)
			shift
			WORKING_DIRECTORY="$1"
			shift
			;;
		--name|-n)
			shift
			FILENAME="$1"
			shift
			;;
		--mode|-m)
			shift
			COLORMODE="$1"
			shift
			;;
		--resolution|-r)
			shift
			RESOLUTION="$1"
			shift
			;;
		--original|-o)
			shift
			TYPE="$1"
			shift
			;;
		--count|-c)
			shift
			OPTCOUNT="$1"
			shift
			;;
		--device|-d)
			shift
			echo "current device is ${DEVICENAME}"
			echo "device info: ${DEVICE}"
			exit 0
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
if [[ "$WORKING_DIRECTORY" == "" ]] || [[ "$FILENAME" == "" ]] || [[ "$COLORMODE" == "" ]] || [[ "$TYPE" == "" ]] || [[ "$RESOLUTION" == "" ]] || [[ "$OPTCOUNT" == "" ]] ; then
	echo "ERROR: one of the necessary command line parameters is not set properly!"
	echo "please refer to command line usage"
	exit 4
fi


# ---------------------------
# scan to tiff
scanimage --device-name ${DEVICE} --mode ${COLORMODE} --resolution ${RESOLUTION} --format tiff > ${WORKING_DIRECTORY}/${FILENAME}.tiff
RETURN_CODE=$?
if [[ ${RETURN_CODE} -ne 0 ]] ; then
	exit ${RETURN_CODE}
fi


# ---------------------------
# convert tiff to png
convert ${WORKING_DIRECTORY}/${FILENAME}.tiff ${WORKING_DIRECTORY}/${FILENAME}.png
RETURN_CODE=$?
if [[ ${RETURN_CODE} -ne 0 ]] ; then
	exit ${RETURN_CODE}
fi


# ---------------------------
# reduce file size
convert ${WORKING_DIRECTORY}/${FILENAME}.png -normalize -gamma 0.8,0.8,0.8 -colorspace HSL -channel saturation -fx 'min(1.0,max(0.0,3*u.g-1))' -colorspace RGB +dither -posterize 3 ${WORKING_DIRECTORY}/${FILENAME}.png
RETURN_CODE=$?
if [[ ${RETURN_CODE} -ne 0 ]] ; then
	exit ${RETURN_CODE}
fi


# ---------------------------
# convert png to pdf
convert ${WORKING_DIRECTORY}/${FILENAME}.png ${WORKING_DIRECTORY}/${FILENAME}.pdf
RETURN_CODE=$?
if [[ ${RETURN_CODE} -ne 0 ]] ; then
	exit ${RETURN_CODE}
fi
