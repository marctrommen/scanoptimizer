#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------
# 
# 
# 
# 
# Further information:
# https://docs.python.org/3/library/tkinter.html#handy-reference
# http://effbot.org/tkinterbook/grid.htm
# http://www.inf-schule.de/software/gui/entwicklung_tkinter/layout/grid
# https://forums.fedoraforum.org/showthread.php?297279-Python3-Tkinter-icon-What-gives!
# -----------------------------------------------------------------------------
# file name ..... scanopt_gui.py
# last change ... 2019-03-16
#
# The MIT License (MIT)
#
# Copyright (c) 2019 Marcus Trommen (mailto:marcus.trommen@gmx.net)
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


# -----------------------------------------------------------------------------
# Version of current script as date string, formatted as 'YYYY-MM-DD hh:mm'
# -----------------------------------------------------------------------------
SCRIPT_VERSION='2019-03-16'
AUTHOR = "Marcus Trommen (mailto:marcus.trommen@gmx.net)"


# -----------------------------------------------------------------------------
# available OPTIONS and DEFAULTS of local scanner / adjust these if necessary
# -----------------------------------------------------------------------------
# current device
DEVICE="hpaio:/usb/Officejet_Pro_8600?serial=CN2C1CXJGN05KC"

RESOLUTION_OPTIONS = ('75', '100', '200', '300')
RESOLUTION_DEFAULT = '200'
SCAN_FILENAME_DEFAULT = "scan"

SHELLSCRIPT = '/usr/bin/scanimage'
PROGRAM_ICON = 'scanopt_gui.gif'
SETTINGS_FILE_NAME = '.scan_and_optimize'

GREY_THRESHOLD = 200

# -----------------------------------------------------------------------------
# static label definitions (for translating UI change here)
# -----------------------------------------------------------------------------
APPLICATION_NAME = 'Scan optimieren'
LABEL_RESOLUTION = 'Scan-Auflösung [dpi]:'
LABEL_WORKDIR = 'Arbeitsverzeichnis:'
LABEL_FILENAME = "Dateiname des Scan: "
LABEL_INFO = 'Info'
LABEL_SCANNING = 'Scannen'
LABEL_CLOSE = 'Schließen'

# -----------------------------------------------------------------------------
# static label definitions (for settings file) - do not change
# -----------------------------------------------------------------------------
SETTING_RESOLUTION = 'resolution'
SETTING_SCANWORKDIR = 'scanworkdir'
SETTING_SCANFILENAME = 'scanfilename'


# -----------------------------------------------------------------------------
import datetime
import os
import sys
import subprocess
import tkinter
import tkinter.filedialog
import tkinter.messagebox
import tkinter.ttk

from PIL import Image
from fpdf import FPDF

# -----------------------------------------------------------------------------
# Application class definition
# -----------------------------------------------------------------------------
class Application(tkinter.Frame):
	
	def __init__(self, master=None):
		super().__init__(master)
		self.master.protocol('WM_DELETE_WINDOW', self.closeApp)
		iconfile = os.path.join(os.path.dirname(__file__), PROGRAM_ICON)
		self.master.tk.call('wm', 'iconphoto', self.master._w, tkinter.PhotoImage(file=iconfile))
		self.grid(sticky='ewsn')
		self.widgetList = []
		
		self._defaultSettings()
		self._loadSettings()
		
		self.master.title(APPLICATION_NAME)
		self._createWidgets()
		self._adjustGeometry()
		

	def _defaultSettings(self):
		self.resolution = tkinter.StringVar()
		self.resolution.set(RESOLUTION_DEFAULT)
		
		self.workdir = tkinter.StringVar()
		self.workdir.set(os.getenv('HOME'))
		
		self.filename = tkinter.StringVar()
		self.filename.set(SCAN_FILENAME_DEFAULT)
	
	
	def _loadSettings(self):
		try:
			fileHandle = open(os.path.join(os.getenv('HOME'), SETTINGS_FILE_NAME), 'r')
		except:
			print("unbekannter Fehler:", sys.exc_info()[0])
		else:
			for line in fileHandle:
				line = line.rstrip()
				
				if line == '' or line.startswith('#'):
					continue
					
				(key, value) = line.split('=')
				key = key.strip()
				value = value.strip()
				
				if key == SETTING_RESOLUTION:
					self.resolution.set(value)
				elif key == SETTING_SCANWORKDIR:
					self.workdir.set(value)
				elif key == SETTING_SCANFILENAME:
					self.filename.set(value)
				else:
					pass
			fileHandle.close()
	
	
	def _writeSettings(self):
		fileHandle = sys.stdout
		try:
			fileHandle = open(os.path.join(os.getenv('HOME'), SETTINGS_FILE_NAME), 'w')
		except:
			print("unbekannter Fehler:", sys.exc_info()[0])
		else:
			fileHandle.write('# last change: ' + datetime.datetime.now().isoformat() + '\n')
			fileHandle.write(SETTING_RESOLUTION + "=" + self.resolution.get() + '\n')
			fileHandle.write(SETTING_SCANWORKDIR + "=" + self.workdir.get() + '\n')
			fileHandle.write(SETTING_SCANFILENAME + "=" + self.filename.get() + '\n')
		finally:
			fileHandle.close()
	
	
	def _adjustGeometry(self):
		#self.master.withdraw()
		self.master.update_idletasks()
		(root_wh, root_x, root_y) = self.master.geometry().split('+')
		self.master.geometry(root_wh + "+200+200")
		#self.master.deiconify()
		self.update()


	def _createWidgets(self):
		rowIndex = 0
		
		# Resolution
		lResolution = tkinter.Label(self)
		lResolution['text'] = LABEL_RESOLUTION
		lResolution['justify'] = tkinter.LEFT
		lResolution.grid(row=rowIndex, column=0, sticky='nw', padx=5, pady=(15,5))
		self.widgetList.append(lResolution)
		
		resBox = tkinter.ttk.Combobox(self)
		resBox['textvariable'] = self.resolution
		resBox['values'] = RESOLUTION_OPTIONS
		resBox.grid(row=rowIndex, column=1, sticky='nw', padx=5, pady=(15,5), columnspan=4)
		self.widgetList.append(resBox)
		rowIndex += 1
		
		# Working Directory
		lWorkdir = tkinter.Label(self)
		lWorkdir['text'] = LABEL_WORKDIR
		lWorkdir['justify'] = tkinter.LEFT
		lWorkdir.grid(row=rowIndex, column=0, sticky='w', padx=5, pady=0)
		self.widgetList.append(lWorkdir)
		rowIndex += 1
		
		eWorkdir = tkinter.Entry(self)
		eWorkdir['textvariable'] = self.workdir
		eWorkdir['justify'] = tkinter.LEFT
		eWorkdir['state'] = 'disabled'
		eWorkdir.grid(row=rowIndex, column=0, sticky='we', padx=5, pady=0, columnspan=4)

		bWorkdir = tkinter.Button(self)
		bWorkdir["text"] = "..."
		bWorkdir["command"] = self._workdirHandler
		bWorkdir.grid(row=rowIndex, column=4, sticky='w', padx=5, pady=0)
		self.widgetList.append(bWorkdir)
		rowIndex += 1
		
		# Scan file name
		lFilename = tkinter.Label(self)
		lFilename['text'] = LABEL_FILENAME
		lFilename['justify'] = tkinter.LEFT
		lFilename.grid(row=rowIndex, column=0, sticky='w', padx=5, pady=8)
		self.widgetList.append(lFilename)
		
		eFilename = tkinter.Entry(self)
		eFilename['textvariable'] = self.filename
		eFilename['justify'] = tkinter.LEFT
		eFilename.grid(row=rowIndex, column=1, sticky='we', padx=5, pady=8, columnspan=4)
		self.widgetList.append(eFilename)
		rowIndex += 1
		
		#-----------------------------------------------
		# Button Info
		bInfo = tkinter.Button(self)
		bInfo["text"] = LABEL_INFO
		bInfo["command"] = self._infoHandler
		bInfo.grid(row=rowIndex, column=0, sticky='w', padx=5, pady=15)
		self.widgetList.append(bInfo)
		
		# Button DoScan
		bScan = tkinter.Button(self)
		bScan["text"] = LABEL_SCANNING
		bScan["command"] = self._doScan
		bScan.grid(row=rowIndex, column=1, sticky='we', padx=5, pady=15, columnspan=2)
		self.widgetList.append(bScan)
		
		# Button Exit
		bquit = tkinter.Button(self)
		bquit["text"] = LABEL_CLOSE
		bquit["command"] = self._exitHandler
		bquit.grid(row=rowIndex, column=3, sticky='we', padx=5, pady=15, columnspan=2)
		self.widgetList.append(bquit)


	def _workdirHandler(self):
		#self.topLevel.update_idletasks()
		options = {}
		options['title'] = "Arbeitsverzeichnis ..."
		options['mustexist'] = True
		options['initialdir'] = self.workdir.get()
		options['parent'] = self
		retValue = tkinter.filedialog.askdirectory(**options)
		
		if len(retValue) > 0 :
			self.workdir.set(retValue)


	def _infoHandler(self):
		infotext = "Autor: " + AUTHOR
		infotext += "\nVersion: " + SCRIPT_VERSION
		tkinter.messagebox.showinfo("Programminfo", infotext)
	
	
	def _exitHandler(self):
		self._writeSettings()
		self.master.destroy()


	def _doScan(self):
		data = {}
		data['wdir'] = self.workdir.get()
		data['name'] = self.filename.get()
		data['resolution'] = self.resolution.get()

		self._toggleState('disabled')
		info = Busy(self.master, 'Info', data)
		info.destroy()
		self._toggleState('normal')


	def closeApp(self):
		tkinter.messagebox.showwarning("Programm schließen", "Bitte Programm über\nden Button \"Schließen\"\nbeenden.")


	def _toggleState(self, state):
		state = state if state in ('normal', 'disabled') else 'normal'
		for widget in self.widgetList:
			widget['state'] = state
		self.update_idletasks()


# -----------------------------------------------------------------------------
# Busy class definition
# -----------------------------------------------------------------------------
class Busy(tkinter.Toplevel):
	# https://infohost.nmt.edu/tcc/help/pubs/tkinter/web/toplevel.html
	# https://pythonprogramming.net/change-show-new-frame-tkinter/
	# https://stackoverflow.com/questions/16115378/tkinter-example-code-for-multiple-windows-why-wont-buttons-load-correctly

	def __init__(self, master=None, title='', data=None):
		super().__init__(master)
		self.title(title)
		self.data = data
		
		label = tkinter.Label(self)
		label['text'] = "Scan in Arbeit ..."
		label.grid(row=0, column=0, padx=20, pady=(20,5))
		
		hourglass = tkinter.Label(self)
		hourglass['bitmap'] = 'hourglass'
		hourglass.grid(row=1, column=0, padx=20, pady=(5, 20))
		
		self._adjustGeometry()
		
		errorCode = self._doScan()
		
		if errorCode == 0:
			errorCode = self._manipulateTiff()
		
		if errorCode == 0:
			errorCode = self._renderPdf()
		
		if errorCode == 0:
			tkinter.messagebox.showinfo("Info", "Scan war erfolgreich!", parent=self)


	def _adjustGeometry(self):
		#self.withdraw()
		self.update_idletasks()
		root_geometry = self.master.geometry()
		(root_wh, root_x, root_y) = root_geometry.split('+')
		(_wh, _x, _y) = self.geometry().split('+')
		
		x = int(root_x) + 20
		y = int(root_y) + 30
		self.geometry(_wh + "+" + str(x) + "+" + str(y))
		#self.deiconify()
		self.update()


	def _doScan(self):
		#scanimage --device-name ${DEVICE} --mode Color --source Flatbed --resolution ${RESOLUTION} --format tiff > ${WORKING_DIRECTORY}/${FILENAME}.tiff
		command = []
		command.append(SHELLSCRIPT)
		# General options
		command.append("--device-name")
		command.append(DEVICE)
		command.append("--format=tiff")
		# Scan mode
		command.append("--mode=Color")
		command.append("--source=Flatbed")
		command.append("--resolution")
		command.append(self.data['resolution'])
		# Advanced
		command.append("--brightness=1000")
		command.append("--contrast=1000")
		command.append("--compression=None")
	
		process = subprocess.Popen(
			command,
			shell=False,
			stdout=subprocess.PIPE,
			stderr=None)
	
		stdoutBuffer, stderrBuffer = process.communicate()
	
		errorCode = process.wait()
	
		if errorCode == 0:
			tempfile = os.path.join(self.data['wdir'], "tempScan.tiff")
			with open(tempfile, "w+b") as fileobject:
				fileobject.write(stdoutBuffer);
			stdoutBuffer = None
		else:
			tkinter.messagebox.showerror("FEHLER", stdoutBuffer, parent=self)	
		return(errorCode)


	def _manipulateTiff(self):
		tempfile = os.path.join(self.data['wdir'], "tempScan.tiff")
		
		image = Image.open(tempfile)
	
		(width, height) = image.size
		#image = image.point(lambda i: 0 if i<26 else 102 if i<128 else 153 if i<179 else 255)
	
		pixel_array = image.load()
		(width, height) = image.size
		for x in range(width):
			for y in range(height):
				(red, green, blue) = pixel_array[x, y]
				red = 0 if red<26 else 102 if red<128 else 255
				green = 0 if green<26 else 102 if green<128 else 255
				blue = 0 if blue<26 else 102 if blue<128 else 255
			
				# check if grey value
				if (red == green and red == blue) :
					if (red < GREY_THRESHOLD) :
						image.putpixel((x, y), (0,0,0))
					else:
						image.putpixel((x, y), (255,255,255))
				else:
					image.putpixel((x, y), (red, green, blue))
		
		#image = image.convert(mode = "P", palette=Image.WEB)
		#image = image.transpose(Image.ROTATE_180)
		#image = image.quantize(colors=256, method=1)
		outfile = os.path.join(self.data['wdir'], self.data['name'] + ".png")
		image.save(outfile, "PNG", optimize = True)
		#image.show()
		return(0)


	def _renderPdf(self):
		pdf = FPDF(orientation = 'P', format = 'A4', unit = 'mm')
		pdf.add_page()
		pdf.set_margins(left = 0, top = 0, right = 0)
		pdf.set_auto_page_break(auto = False, margin = 0.0)
		filename = os.path.join(self.data['wdir'], self.data['name'])
		pdf.image(filename + ".png", w=210)
		pdf.output(filename + ".pdf")
		return(0)

# -----------------------------------------------------------------------------
# main program
# -----------------------------------------------------------------------------
if __name__ == '__main__' :
	root = tkinter.Tk()
	app = Application(master=root)
	root.mainloop()
