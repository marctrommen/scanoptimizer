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


# -----------------------------------------------------------------------------
# Version of current script as date string, formatted as 'YYYY-MM-DD hh:mm'
# -----------------------------------------------------------------------------
SCRIPT_VERSION='2018-02-19 20:00'
AUTHOR = "Marcus Trommen (mailto:marcus.trommen@gmx.net)"


# -----------------------------------------------------------------------------
# available OPTIONS and DEFAULTS of local scanner / adjust these if necessary
# -----------------------------------------------------------------------------
RESOLUTION_OPTIONS = ('75', '100', '200', '300')
RESOLUTION_DEFAULT = '200'
OPTIMIZATIONCOUNT_DEFAULT = 7
OPTIMIZATIONCOUNT_MAX_VALUE = 15
COLORMODE_OPTIONS = {'Gray' : 'Grautöne', 'Color' : 'Farbe'}
COLORMODE_DEFAULT_KEY = 'Gray'
ORIGINAL_OPTIONS = {'text' : 'Text', 'graphics' : 'Bild'}
ORIGINAL_DEFAULT_KEY = 'text'
SCAN_FILENAME_DEFAULT = "scan"

SHELLSCRIPT = '/opt/scanopt/scan_and_optimize.sh'
PROGRAM_ICON = 'scanopt_gui.gif'
SETTINGS_FILE_NAME = '.scan_and_optimize'

# -----------------------------------------------------------------------------
# static label definitions (for translating UI change here)
# -----------------------------------------------------------------------------
APPLICATION_NAME = 'Scan optimieren'
LABEL_RESOLUTION = 'Scan-Auflösung [dpi]:'
LABEL_COLORMODE = 'Ausgabedokument:'
LABEL_OPTIMIZATIONCOUNT = 'Anzahl Optimierungen:'
LABEL_ORIGINAL = 'Vorlageart: überwiegend '
LABEL_WORKDIR = 'Arbeitsverzeichnis:'
LABEL_FILENAME = "Dateiname des Scan: "
LABEL_INFO = 'Info'
LABEL_SCANNING = 'Scannen'
LABEL_CLOSE = 'Schließen'

# -----------------------------------------------------------------------------
# static label definitions (for settings file) - do not change
# -----------------------------------------------------------------------------
SETTING_RESOLUTION = 'resolution'
SETTING_COLORMODE = 'colormode'
SETTING_OPTIMIZATIONCOUNT = 'optimizationcount'
SETTING_ORIGINAL = 'originial'
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
		
		self.colormode = tkinter.StringVar()
		self.colormode.set(COLORMODE_DEFAULT_KEY)
		
		self.optcount = tkinter.IntVar()
		self.optcount = OPTIMIZATIONCOUNT_DEFAULT
		
		self.original = tkinter.StringVar()
		self.original.set(ORIGINAL_DEFAULT_KEY)
		
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
				elif key == SETTING_COLORMODE:
					self.colormode.set(value)
				elif key == SETTING_OPTIMIZATIONCOUNT:
					self.optcount = int(value)
				elif key == SETTING_ORIGINAL:
					self.original.set(value)
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
			fileHandle.write(SETTING_COLORMODE + "=" + self.colormode.get() + '\n')
			fileHandle.write(SETTING_OPTIMIZATIONCOUNT + "=" + str(self.optcount) + '\n')
			fileHandle.write(SETTING_ORIGINAL + "=" + self.original.get() + '\n')
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
		
		# ColorMode
		lColorMode = tkinter.Label(self)
		lColorMode['text'] = LABEL_COLORMODE
		lColorMode['justify'] = tkinter.LEFT
		lColorMode.grid(row=rowIndex, column=0, sticky='nw', padx=5, pady=8)
		self.widgetList.append(lColorMode)
		
		optionFrame = tkinter.Frame(self)
		optionRow = 0
		for cmodeKey in COLORMODE_OPTIONS.keys() :
			radio = tkinter.Radiobutton(optionFrame)
			radio["text"] = COLORMODE_OPTIONS[cmodeKey]
			radio["value"] = cmodeKey
			radio["variable"] = self.colormode
			radio.grid(row=optionRow, column=0, padx=0, pady=0, sticky='w')
			self.widgetList.append(radio)
			optionRow += 1
		optionFrame.grid(row=rowIndex, column=1, sticky='wn', padx=5, pady=8, columnspan=4)
		rowIndex += 1
		
		# OptimizationCount
		lOptCount = tkinter.Label(self)
		lOptCount['text'] = LABEL_OPTIMIZATIONCOUNT
		lOptCount['justify'] = tkinter.LEFT
		lOptCount.grid(row=rowIndex, column=0, sticky='w', padx=5, pady=5)
		self.widgetList.append(lOptCount)
		
		self.vOptCount = tkinter.Label(self)
		self.vOptCount['text'] = str(self.optcount)
		self.vOptCount['bg'] = 'white'
		self.vOptCount['width'] = 2
		self.vOptCount['justify'] = tkinter.RIGHT
		self.vOptCount.grid(row=rowIndex, column=1, sticky='w', padx=5, pady=5)
		self.widgetList.append(self.vOptCount)

		bDecOptCount = tkinter.Button(self)
		bDecOptCount['text'] = '-'
		bDecOptCount['width'] = 1
		bDecOptCount['command'] = self._decreaseOptCount
		bDecOptCount.grid(row=rowIndex, column=2, sticky='e', padx=0, pady=0)
		self.widgetList.append(bDecOptCount)
		
		bIncOptCount = tkinter.Button(self)
		bIncOptCount['text'] = '+'
		bIncOptCount['width'] = 1
		bIncOptCount['command'] = self._increaseOptCount
		bIncOptCount.grid(row=rowIndex, column=3, sticky='w', padx=0, pady=0)
		self.widgetList.append(bIncOptCount)
		rowIndex += 1
		 
		# Original (Vorlageart)
		lOrig = tkinter.Label(self)
		lOrig['text'] = LABEL_ORIGINAL
		lOrig['justify'] = tkinter.LEFT
		lOrig.grid(row=rowIndex, column=0, sticky='ewn', padx=5, pady=8)
		self.widgetList.append(lOrig)
		
		frameOrig = tkinter.Frame(self)
		optionRow = 0
		for origKey in ORIGINAL_OPTIONS.keys() :
			radio = tkinter.Radiobutton(frameOrig)
			radio["text"] = ORIGINAL_OPTIONS[origKey]
			radio["value"] = origKey
			radio["variable"] = self.original
			radio.grid(row=optionRow, column=0, sticky='w', padx=0, pady=0)
			self.widgetList.append(radio)
			optionRow += 1
		frameOrig.grid(row=rowIndex, column=1, sticky='ewns', padx=5, pady=8, columnspan=4)
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


	def _increaseOptCount(self):
		self.optcount += 1
		if (self.optcount > OPTIMIZATIONCOUNT_MAX_VALUE):
			self.optcount = OPTIMIZATIONCOUNT_MAX_VALUE
		self.vOptCount['text'] = str(self.optcount)


	def _decreaseOptCount(self):
		self.optcount -= 1
		if (self.optcount < 1):
			self.optcount = 1
		self.vOptCount['text'] = str(self.optcount)


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
		data['mode'] = self.colormode.get()
		data['original'] = self.original.get()
		data['resolution'] = self.resolution.get()
		data['count'] = str(self.optcount)

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
		self._doScan()
		#import time
		#time.sleep(5)


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
		command = []
		command.append(SHELLSCRIPT)
		command.append('--wdir')
		command.append(self.data['wdir'])
		command.append('--name')
		command.append(self.data['name'])
		command.append('--mode')
		command.append(self.data['mode'])
		command.append('--original')
		command.append(self.data['original'])
		command.append('--resolution')
		command.append(self.data['resolution'])
		command.append('--count')
		command.append(self.data['count'])
		
		process = subprocess.Popen(
			command,
			shell=False, 
			stdout=subprocess.PIPE,
			stderr=subprocess.STDOUT)
			
		stdoutBuffer = ''
		for line in process.stdout:
			stdoutBuffer += line.decode('utf-8')
		
		errorCode = process.wait()
		
		if errorCode == 0:
			tkinter.messagebox.showinfo("Info", "Scan war erfolgreich!", parent=self)
		else:
			tkinter.messagebox.showerror("FEHLER", stdoutBuffer, parent=self)	


# -----------------------------------------------------------------------------
# main program
# -----------------------------------------------------------------------------
if __name__ == '__main__' :
	root = tkinter.Tk()
	app = Application(master=root)
	root.mainloop()
