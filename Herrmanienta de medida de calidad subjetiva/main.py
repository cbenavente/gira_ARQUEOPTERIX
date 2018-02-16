#!/usr/bin/python3
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject, Gdk
from datetime import datetime
import FFMPEG
import threading
import BBDD
from time import sleep
import os
import sys
import math

class NoConnectionDialog(Gtk.Dialog):

	def __init__(self, parent):
		Gtk.Dialog.__init__(self, "Error de connexión a la BBDD", parent, 0,
			(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
			Gtk.STOCK_OK, Gtk.ResponseType.OK))

		self.set_default_size(150, 100)

		label = Gtk.Label("No se ha podido conectar a la base de datos.\n\nLos resultados de la prueba serán guardados en un archivo")

		box = self.get_content_area()
		box.add(label)
		box.pack_start(label,True,True,10)
		self.show_all()


class Window(Gtk.Window):
	def __init__(self):  
		Gtk.Window.__init__(self, title="ARQUEOPTERIX - Herramienta para la medida de la calidad subjetiva de videos")

		#obtener tamaño de la pantalla
		s=Gdk.Screen.get_default()
		self.screenW=s.get_width()
		self.screenH=s.get_height()
		#Ajustar tamaño de los textos
		self.size_font = [26000, 20000, 16000, 14000, 12000]
		divisor = 1
		if (self.screenW != 1680):
			divisor=(1680/self.screenW)+0.2
		for n in range(len(self.size_font)):
			self.size_font[n] = int(math.ceil(self.size_font[n]/divisor))

		self.box_outer=Gtk.VBox()
		self.add(self.box_outer)

		self.create_header()
		self.create_user()
		self.create_footer()
		self.create_VideoSelect()
		self.create_Instructions()
		self.create_SpinnerBox()
		self.create_VoteBoxAB()
		self.create_VoteBoxXC()
		self.create_finPruebaBox()
		self.add_to_outer()
	
		self.packOuter()

		# Make directory if no exist (EN WINDOWS ES DOBLE SLASH)
		if (not os.path.exists(os.getcwd()+"/tmp")): #En ubuntu
			os.mkdir('tmp')

		self.logFile=open('./tmp/logFile','w')
		#self.logFile=open('logFile','a')


	def create_header(self):
		## Header --> TOP BOX = logo + title y subtitle + logo UPM
		self.box_top=Gtk.HBox()
		#Logo Arqueopterix
		self.logo=Gtk.Image(yalign=0)
		self.logo.set_from_file("./Media/logo.png")
		self.box_top.pack_start(self.logo,False,True,0)
		# EVENT BOX to fill background color
		self.event_box = Gtk.EventBox()
		self.box_top.add(self.event_box)
		self.event_box.show()
		#TITLE BOX = title + subtitle
		self.title_box=Gtk.VBox()
		self.title_box.set_valign(Gtk.Align.CENTER)
		self.event_box.add(self.title_box)
		#Title
		self.title=Gtk.Label()
		self.title.set_markup("<span font_desc='Sans 12' foreground='#9AC42f' size=\'"+str(self.size_font[0])+"\'> HERRAMIENTA PARA LA MEDIDA DE LA CALIDAD SUBJETIVA DE VIDEOS </span>")
		#self.title.set_markup("<span font_desc='Sans 12' foreground='#9AC42f' size='xx-large'><b>HERRAMIENTA PARA LA MEDIDA DE LA CALIDAD SUBJETIVA DE VIDEOS</b></span>")
		##self.title.set_markup("<span font_desc='Sans 12' foreground='#9AC42f' size='large'><b>HERRAMIENTA PARA LA MEDIDA DE LA CALIDAD SUBJETIVA DE VIDEOS</b></span>")
		self.title_box.pack_start(self.title,False,True,10)
		#Subtitle
		self.subtitle=Gtk.Label()
		self.subtitle.set_markup("<span font_desc='Arial 12' foreground='#9D9C9C' size=\'"+str(self.size_font[2])+"\'> Esta herramienta permite analizar la percepción de un usuario frente a una degradación sucesiva en un tipo de video específico </span>")
		#self.subtitle.set_markup("<span font_desc='Arial 12' foreground='#9D9C9C' size='medium'> Esta herramienta permite analizar la percepción de un usuario frente a una degradación sucesiva en un tipo de video específico </span>")
		##self.subtitle.set_markup("<span font_desc='Arial 12' foreground='#9D9C9C' size='small'> Esta herramienta permite analizar la percepción de un usuario frente a una degradación sucesiva en un tipo de video específico </span>")
		self.title_box.pack_start(self.subtitle,False,True,10)
		#Logo UPM
		self.logo_upm=Gtk.Image(yalign=0)
		self.logo_upm.set_from_file("./Media/logo_upm.png")
		self.box_top.pack_start(self.logo_upm,False,True,0)
		#Filling background color
		self.logo.override_background_color(Gtk.StateType.NORMAL, Gdk.RGBA.from_color(Gdk.color_parse('#FFFFFF')))#3B9998
		self.event_box.override_background_color(Gtk.StateType.NORMAL, Gdk.RGBA.from_color(Gdk.color_parse('#FFFFFF')))##C63D2D
		self.logo_upm.override_background_color(Gtk.StateType.NORMAL, Gdk.RGBA.from_color(Gdk.color_parse('#FFFFFF')))

	def create_user(self):
		## Body --> MAIN BOX = user / video selection / instructions / test / results
		self.user_box=Gtk.HBox()

		self.user_box.set_halign(Gtk.Align.CENTER)
		self.user_box.set_valign(Gtk.Align.CENTER)

		# Username
		self.user=Gtk.Label("Username:",)
		self.user_box.pack_start(self.user, False, False, 0)

		self.entry = Gtk.Entry()
		self.user_box.pack_start(self.entry, False, False, 10)

		# Button box
		self.continue_button=Gtk.Button("Continuar")
		self.user_box.pack_start(self.continue_button,False,False,0)
		self.continue_button.connect("clicked",self.continue_button_clicked)

	def continue_button_clicked(self,button):
		# print('A')
		self.username=self.entry.get_text()

		if(self.username!=''):
			self.userBBDD = BBDD.writeUser(self.username)
			if (self.userBBDD==0):
				dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO, Gtk.ButtonsType.OK, "Error de connexión a la BBDD")
				dialog.format_secondary_text("No se ha podido conectar a la base de datos. Los resultados de la prueba serán guardados en un archivo")
				dialog.run()
				print("Info dialog closed")
				dialog.destroy()
				
			#print(self.username)
			#print(self.getDate())
			self.date=self.getDate()
			#print(date)
			self.user_box.hide()
			self.videoSelect_box.show()

		
	def create_footer(self):
		## Footer --> BOTTON BOX = logo CDTI + project and url + logo FEBER
		self.box_bottom=Gtk.HBox()
		#Logo Arqueopterix
		self.logo_cdti=Gtk.Image(yalign=0)
		self.logo_cdti.set_from_file("./Media/logo_cdti.jpg")
		self.box_bottom.pack_start(self.logo_cdti,False,True,0)
		# EVENT BOX to fill background color
		self.event_box2 = Gtk.EventBox()
		self.box_bottom.add(self.event_box2)
		self.event_box.show()
		#TITLE BOX = project + url
		self.project_box=Gtk.VBox()
		self.project_box.set_valign(Gtk.Align.CENTER)
		self.event_box2.add(self.project_box)
		#Title
		self.nproject=Gtk.Label()
		self.nproject.set_markup("<span font_desc='Arial 12' foreground='#515252' size=\'"+str(self.size_font[4])+"\'>   Proyecto Financiado por el Centro para el Desarrollo Tecnológico Industrial (CDTI)\n dentro del programa estrategico CIEN 2015 con numero de expediente IDI-20150609 </span>")
		##self.nproject.set_markup("<span font_desc='Arial 12' foreground='#515252' size='8000'>   Proyecto Financiado por el Centro para el Desarrollo Tecnológico Industrial (CDTI)\n dentro del programa estrategico CIEN 2015 con numero de expediente IDI-20150609 </span>")
		self.project_box.pack_start(self.nproject,False,True,5)
		#url
		self.url=Gtk.Label()
		self.url.set_markup("<span font_desc='Arial 12' foreground='#515252' size=\'"+str(self.size_font[4])+"\'> <a href=\"http://www.arqueopterix.es\">www.arqueopterix.es</a> </span>")
		##self.url.set_markup("<span font_desc='Arial 12' foreground='#515252' size='8000'> <a href=\"http://www.arqueopterix.es\">www.arqueopterix.es</a> </span>")
		self.project_box.pack_start(self.url,False,True,5)
		#Logo feber
		self.logo_feber=Gtk.Image(yalign=0)
		self.logo_feber.set_from_file("./Media/logo_feber.jpg")
		self.box_bottom.pack_start(self.logo_feber,False,True,0)
		#Filling background color
		self.logo_cdti.override_background_color(Gtk.StateType.NORMAL, Gdk.RGBA.from_color(Gdk.color_parse('#FFFFFF')))#3B9998
		self.event_box2.override_background_color(Gtk.StateType.NORMAL, Gdk.RGBA.from_color(Gdk.color_parse('#9AC42f')))##C63D2D
		self.logo_feber.override_background_color(Gtk.StateType.NORMAL, Gdk.RGBA.from_color(Gdk.color_parse('#FFFFFF')))
		
	def add_to_outer(self):
		# Add boxes to outer_box
		self.box_outer.add(self.box_top)
		self.box_outer.add(self.user_box)
		self.box_outer.add(self.videoSelect_box)
		self.box_outer.add(self.instructions_box)
		self.box_outer.add(self.spinnerBox)
		self.box_outer.add(self.voteBoxAB)
		self.box_outer.add(self.voteBoxXC)
		self.box_outer.add(self.finprueba_box)
		self.box_outer.add(self.box_bottom)

	def packOuter(self):
		# Set child packing
		self.box_outer.set_child_packing(self.box_top, False, True, 0, Gtk.PackType.START)
		self.box_outer.set_child_packing(self.box_bottom, False, True, 0, Gtk.PackType.END)

	def getDate(self):
		date = datetime.now()
		return date

	def create_VideoSelect(self):
		self.path='./Media/Frames/'
		self.images = ["01Pacman.png", "02DonkeyKongCountry.png", "03DragonBallFighterZ.png", "04PuzzleBall.png", "05ARMA3Jets.png", "06FormulaExtreme.png", "07DirtRally_onBoard.png", "08DirtRally2016.png", "09MarioCircuit.png", "10Battlefield.png", "11ExclusiveDOOM.png", "12Paladins.png", "13ProEvolutionSoccer2017.png", "14OnlineMeetingOne2One.png", "15OnlineMeetingMulti.png", "16BigBuckBunny.png"]
		self.videos = ["01Pacman.mp4", "02DonkeyKongCountry.mp4", "03DragonBallFighterZ.mp4", "04PuzzleBall.mp4", "05ARMA3Jets.mp4", "06FormulaExtreme.mp4", "07DirtRally_onBoard.mp4", "08DirtRally2016.mp4", "09MarioCircuit.mp4", "10Battlefield.mp4", "11ExclusiveDOOM.mp4", "12Paladins.mp4", "13ProEvolutionSoccer2017.mp4", "14OnlineMeetingOne2One.mp4", "15OnlineMeetingMulti.mp4", "16BigBuckBunny.mp4"]


		self.videoSelect_box = Gtk.VBox(spacing=10)
		#self.add(self.videoSelect_box)

		self.videoSelect_box.pack_start(Gtk.Label("Por favor, selecciona un video:"),True,True,0)

		self.videoSelect_box.set_halign(Gtk.Align.CENTER)
		self.videoSelect_box.set_valign(Gtk.Align.CENTER)

		grid = Gtk.Grid()
		grid.set_column_spacing(30)
		grid.set_row_spacing(10)
		self.videoSelect_box.pack_start(grid,True,True,0)

		buttons=[]

		for i in range(len(self.images)):

			image = Gtk.Image()
			image.set_from_file(self.path+self.images[i])
			button = Gtk.Button(image=image)
			button.connect("clicked", self.continue_selected_video, self.videos[i])
			buttons.append(button)


		grid.attach(buttons[0], 0, 0, 2, 2)	# (child,column,row,width,height)
		label0=Gtk.Label('Pacman')
		grid.attach_next_to(label0, buttons[0], Gtk.PositionType.BOTTOM, 2, 1)	# (child,sibling,position,width,height)

		grid.attach_next_to(buttons[1],buttons[0],Gtk.PositionType.RIGHT, 2, 2)
		grid.attach_next_to(Gtk.Label('Donkey Kong Country'), buttons[1], Gtk.PositionType.BOTTOM, 2, 1)

		grid.attach_next_to(buttons[2],buttons[1],Gtk.PositionType.RIGHT, 2, 2)
		grid.attach_next_to(Gtk.Label('Dragon Ball Fighter Z'), buttons[2], Gtk.PositionType.BOTTOM, 2, 1)

		grid.attach_next_to(buttons[3],buttons[2],Gtk.PositionType.RIGHT, 2, 2)
		grid.attach_next_to(Gtk.Label('Puzzle Ball'), buttons[3], Gtk.PositionType.BOTTOM, 2, 1)


		grid.attach_next_to(buttons[4], label0, Gtk.PositionType.BOTTOM, 2, 2)
		label4=Gtk.Label('ARMA 3 Jets')
		grid.attach_next_to(label4, buttons[4], Gtk.PositionType.BOTTOM, 2, 1)

		grid.attach_next_to(buttons[5],buttons[4],Gtk.PositionType.RIGHT, 2, 2)
		grid.attach_next_to(Gtk.Label('Formula Extreme'), buttons[5], Gtk.PositionType.BOTTOM, 2, 1)

		grid.attach_next_to(buttons[6],buttons[5],Gtk.PositionType.RIGHT, 2, 2)
		grid.attach_next_to(Gtk.Label('Dirt Rally on Board'), buttons[6], Gtk.PositionType.BOTTOM, 2, 1)

		grid.attach_next_to(buttons[7],buttons[6],Gtk.PositionType.RIGHT, 2, 2)
		grid.attach_next_to(Gtk.Label('Dirt Rally 2016'), buttons[7], Gtk.PositionType.BOTTOM, 2, 1)


		grid.attach_next_to(buttons[8], label4, Gtk.PositionType.BOTTOM, 2, 2)
		label8=Gtk.Label('Mario Circuit')
		grid.attach_next_to(label8, buttons[8], Gtk.PositionType.BOTTOM, 2, 1)

		grid.attach_next_to(buttons[9],buttons[8],Gtk.PositionType.RIGHT, 2, 2)
		grid.attach_next_to(Gtk.Label('Battle Field'), buttons[9], Gtk.PositionType.BOTTOM, 2, 1)

		grid.attach_next_to(buttons[10],buttons[9],Gtk.PositionType.RIGHT, 2, 2)
		grid.attach_next_to(Gtk.Label('Exclusive DOOM'), buttons[10], Gtk.PositionType.BOTTOM, 2, 1)

		grid.attach_next_to(buttons[11],buttons[10],Gtk.PositionType.RIGHT, 2, 2)
		grid.attach_next_to(Gtk.Label('Paladins'), buttons[11], Gtk.PositionType.BOTTOM, 2, 1)


		grid.attach_next_to(buttons[12], label8, Gtk.PositionType.BOTTOM, 2, 2)
		label12=Gtk.Label('Pro Evolution Soccer 2017')
		grid.attach_next_to(label12, buttons[12], Gtk.PositionType.BOTTOM, 2, 1)

		grid.attach_next_to(buttons[13],buttons[12],Gtk.PositionType.RIGHT, 2, 2)
		grid.attach_next_to(Gtk.Label('Online Meeting One 2 One'), buttons[13], Gtk.PositionType.BOTTOM, 2, 1)

		grid.attach_next_to(buttons[14],buttons[13],Gtk.PositionType.RIGHT, 2, 2)
		grid.attach_next_to(Gtk.Label('Online Meeting Multi'), buttons[14], Gtk.PositionType.BOTTOM, 2, 1)

		grid.attach_next_to(buttons[15],buttons[14],Gtk.PositionType.RIGHT, 2, 2)
		grid.attach_next_to(Gtk.Label('Big Buck Bunny'), buttons[15], Gtk.PositionType.BOTTOM, 2, 1)
	

	def continue_selected_video(self,button,video):
		self.videoSelected = video.split('.')[0]
		self.logFile.write("\nEl video seleccionado es: "+self.videoSelected)
		self.configLeida=0 #Para que lea la configuracion del video de referencia
		self.primerVideoA=1 #Indica que es el primer video a generar
		self.primerVideoB=1 #Indica que es el primer video a generar
		self.primerVideoC=1 #Indica que es el primer video a generar
		#print("El video seleccionado es:")
		#print(self.videoSelected)
		self.videoSelect_box.hide()
		self.instructions_box.show()
		

	def create_Instructions(self):
		self.instructions_box = Gtk.VBox(spacing=10)
		#self.add(self.instructions_box)
		self.instructions_box.set_border_width(30)

		self.instructions_box.set_halign(Gtk.Align.CENTER)
		self.instructions_box.set_valign(Gtk.Align.CENTER)

		self.instructions_title=Gtk.Label()
		self.instructions_title.set_markup("<span font_desc='Sans 12' foreground='#555555' underline='single' size=\'"+str(self.size_font[1])+"\'>INSTRUCCIONES DE LA REALIZACIÓN DE LA PRUEBA</span>")
		#self.instructions_title.set_markup("<span font_desc='Sans 12' foreground='#555555' underline='single' size='x-large'>INSTRUCCIONES DE LA REALIZACIÓN DE LA PRUEBA</span>")
		self.instructions_box.pack_start(self.instructions_title,False,True,20)

		self.frame_instuctions=Gtk.Frame()
		self.instructions_box.pack_start(self.frame_instuctions,False,True,20)
		#self.instructions_box.add(self.frame_instuctions)
		self.instructions_def=Gtk.Label()
		self.instructions_def.set_markup("\n<span font_desc='Sans 12' foreground='#555555' size=\'"+str(self.size_font[3])+"\'>"
										 "A continuación se le mostrará una secuencia de videos en pares: "
										 "el proceso consiste en mostrar al usuario dos videos a la vez y "
										 "tras ello el usuario deberá elegir cúal de esos videos le ha "
										 "gustado más o si por el contrario le han gustado por igual.\n\n"
										 "Tras la visualización de los videos dispondrá de 10 segundos para "
										 "votar.</span>\n")
		self.instructions_def.set_line_wrap(True)
		self.frame_instuctions.add(self.instructions_def)

		self.startTest_button=Gtk.Button("Comenzar")
		self.instructions_box.pack_start(self.startTest_button,False,False,0)
		self.startTest_button.set_halign(Gtk.Align.CENTER)
		self.startTest_button.set_valign(Gtk.Align.CENTER)
		self.startTest_button.connect("clicked",self.continue_button_startTest)


	def continue_button_startTest(self,button):
		#self.logFile.close()
		#self.logFile=open('logFile','a')
		if self.configLeida == 0:
			print("Comenzamos el test")
			self.starttime=self.getDate()
			self.logFile.write("\nComenzamos el test a las "+str(self.starttime))
			self.pruebaBBDD = BBDD.writePrueba(self.userBBDD, self.starttime, self.videoSelected)
			self.instructions_box.hide()
			#self.spinnerBox.show()
			self.videoElegido = 'D'
			
		
		self.hilo=threading.Thread(target=self.videoProcess)
		self.hilo.start()

	def create_SpinnerBox(self):
		self.spinnerBox=Gtk.VBox()
		#self.add(self.spinnerBox)

		self.spinnerBox.set_halign(Gtk.Align.CENTER)
		self.spinnerBox.set_valign(Gtk.Align.CENTER)

		self.spinner=Gtk.Spinner()
		self.spinner.set_halign(Gtk.Align.CENTER)
		self.spinner.set_valign(Gtk.Align.CENTER)
		self.spinner.set_size_request(50,50)
		self.spinner.start()
		self.label_spinner=Gtk.Label()
		self.label_spinner.set_markup("<span font_desc='Sans 12' foreground='#555555' size=\'"+str(self.size_font[3])+"\'>Procesando videos ...</span>")
		##self.label_spinner.set_markup("<span font_desc='Sans 12' foreground='#555555' size='10000'>Procesando videos ...</span>")

		self.spinnerBox.pack_start(self.label_spinner,False,False,20)
		self.spinnerBox.pack_start(self.spinner,False,False,20)


	def videoProcess(self):
		self.spinnerBox.show()
		#Si es la primera vez que que se entra en videoProcess
		if self.configLeida == 0:
			#list_var = ['refVideo','fps','fpsstep','crf','crfstep','width','height','resstep','bitrate_max','bitratestep' ]
			list_var = ['refVideo','fps','fpsstep','crf','crfstep','resstep','bitrate_max','bitratestep' ]
			refVideo,rest = FFMPEG.getConfiguration(list_var,self.videoSelected)
			#fps, fps_step, crf, crf_step, width, height, res_step, bitrate_max, bitrate_step = rest 	#ints
			fps, fps_step, crf, crf_step, res_step, bitrate_max, bitrate_step = rest 	#ints

			#Adaptar la anchura y altura máxima de los videos
			width = self.screenW/2
			index = math.floor(width/16)
			if (index % 2 != 0):
				index = index -1
			width = index * 16;
			height = index * 9;

			self.widthMax = width
			self.heightMax = height

			self.logFile.write("\nHemos leido la configuracion:")
			self.logFile.write("\n\tVideoRef:\t"+refVideo)
			self.logFile.write("\n\tfps:\t\t"+str(fps)+"\t\t(en pasos de "+str(fps_step)+")")
			self.logFile.write("\n\tcrf:\t\t"+str(crf)+"\t\t(en pasos de "+str(crf_step)+")")
			self.logFile.write("\n\twidth x height:\t"+str(width)+"x"+str(height)+"\t(en pasos de "+str(res_step)+")")
			self.logFile.write("\n\tbitrate_max:\t"+str(bitrate_max))
			#self.logFile.close()

			##Inicializacion de variables
			self.videoRef=refVideo
			self.crf_step=crf_step
			self.fps_step=fps_step
			self.res_step=res_step
			self.target_bitrate = bitrate_max
			self.bitrate_step = bitrate_step

			#Variables para el video A (degradación en resolución) res_step = [18, 36, 54, 72, 90]
			self.fpsA=fps
			self.crfA=crf
			#self.widthA=width
			#self.heightA=height
			self.widthA , self.heightA = FFMPEG.reSize(width,height,res_step)

			#Variables para el video B (degradación en fps)
			self.fpsB=fps-fps_step
			#self.fpsB=fps
			self.crfB=crf
			self.widthB=width
			self.heightB=height

			#Variables para el video C (degradación en calidad)
			self.fpsC=fps
			self.crfC=crf+crf_step
			#self.crfC=crf
			self.widthC=width
			self.heightC=height

			self.configLeida=1

		if self.configLeida == 1:
			#self.target_bitrate = self.target_bitrate-300 #Disminución del bitrate para la siguiente prueba
			self.target_bitrate = self.target_bitrate-self.bitrate_step #Disminución del bitrate para la siguiente prueba
			refVideo=self.videoRef
			self.logFile.write("\n---> Target bitrate: "+str(self.target_bitrate))

		if (self.target_bitrate>=0):
			hiloA=threading.Thread(target=self.genVideoA)
			hiloB=threading.Thread(target=self.genVideoB)
			hiloC=threading.Thread(target=self.genVideoC)

			hiloA.start()
			hiloB.start()
			hiloC.start()

			hiloA.join()
			hiloB.join()
			hiloC.join()
			
			if (self.heightA >= self.res_step and self.fpsB >= self.fps_step and self.crfC <= 51):
				#	Visualizacion de videosProcessing videos
				self.spinnerBox.hide()
				FFMPEG.launchVideo(self.outputA, self.outputB, self.widthMax, self.heightMax)
		
				#show the self.progressbar and buttons
				sleep(0.5) #Esperar tras reproducir el video
				self.voteBoxAB.show()
				self.startBar()
			else:
				self.endtime=self.getDate()
				BBDD.writeEndDate(self.pruebaBBDD,self.endtime)
				self.spinnerBox.hide()
				self.logFile.write("\n******************\nPRUEBA FINALIZADA\n******************\n")
				self.finprueba_box.show()
				#self.videoSelect_box.show()
		else:
			self.endtime=self.getDate()
			BBDD.writeEndDate(self.pruebaBBDD,self.endtime)
			self.spinnerBox.hide()
			self.logFile.write("\n******************\nPRUEBA FINALIZADA\n******************\n")
			self.finprueba_box.show()
			#self.videoSelect_box.show()



	#	Processing videos
	def genVideoA(self):
		while True:
			if (self.primerVideoA == 1):
				## Generacion video A
				#Lanzo ffmpeg paraq video A
				self.outputA="./tmp/A.mp4"
				#self.widthA , self.heightA = FFMPEG.reSize(self.widthA,self.heightA,res_step)
				FFMPEG.launchCommand(self.videoRef,str(self.fpsA),str(self.crfA),str(self.widthA)+":"+str(self.heightA),self.outputA)
				self.logFile.write("\n(He generado el primer video de A)")
				#Calculo bitrate del video A
				self.avg_bitrateA=FFMPEG.getBitrate(self.outputA)
				self.primerVideoA=0

			#Si continuo cumpliendo el objetivo de bitrate no hago nada
			if (self.avg_bitrateA<float(self.target_bitrate)):
				print("#### Video A preparado: fps="+str(self.fpsA)+" crf="+str(self.crfA)+" resolution="+str(self.widthA)+"x"+str(self.heightA)+" bitrate="+str(self.avg_bitrateA)+" kbits/s")
				self.logFile.write("\n#### Video A preparado: fps="+str(self.fpsA)+" crf="+str(self.crfA)+" resolution="+str(self.widthA)+"x"+str(self.heightA)+" bitrate="+str(self.avg_bitrateA)+" kbits/s")
				self.prefpsA=self.fpsA
				self.precrfA=self.crfA
				self.prewidthA=self.widthA
				self.preheightA=self.heightA
				break
			else:
				self.widthA , self.heightA = FFMPEG.reSize(self.widthA,self.heightA,self.res_step)
				if (self.heightA < self.res_step or self.crfA > 51):
					break

			#No se cumple condicion de bitrate --> borramos video, degradamos parámetro A y volvemos a crear video
			os.system(("rm "+self.outputA))
			# if (self.videoElegido == 'A'):
			# 	#if (self.heightA < self.res_step or self.crfA > 51):
			# 	#	break
			if (self.videoElegido == 'B'):
				self.fpsA = self.prefpsB
			elif (self.videoElegido == 'C'):
				self.crfA = self.precrfC
			elif (self.videoElegido == 'A=B'):
				#self.widthA , self.heightA = FFMPEG.reSize(self.widthA,self.heightA,self.res_step)
				#if (self.heightA < self.res_step or self.crfA > 51):
				#	break
				self.fpsA = self.prefpsB
			elif (self.videoElegido == 'A=C'):
				#self.widthA , self.heightA = FFMPEG.reSize(self.widthA,self.heightA,self.res_step)
				#if (self.heightA < self.res_step or self.crfA > 51):
				#	break
				self.crfA = self.precrfC
			elif (self.videoElegido == 'B=C'):
				self.fpsA = self.prefpsB
				self.crfA = self.precrfC
			elif (self.videoElegido == 'A=B=C'):
				#self.widthA , self.heightA = FFMPEG.reSize(self.widthA,self.heightA,self.res_step)
				#if (self.heightA < self.res_step or self.crfA > 51):
				#	break
				self.fpsA = self.prefpsB
				self.crfA = self.precrfC
			# else:
			# 	self.crfA=self.crfA+self.crf_step
			# 	if (self.crfA > 51):
			# 		break
			
			## Generacion video A
			#Lanzo ffmpeg paraq video A
			#self.outputA="A.mp4"
			#self.widthA , self.heightA = FFMPEG.reSize(self.widthA,self.heightA,res_step)
			FFMPEG.launchCommand(self.videoRef,str(self.fpsA),str(self.crfA),str(self.widthA)+":"+str(self.heightA),self.outputA)
			self.logFile.write("\n(Genero un nuevo video de A--> fps="+str(self.fpsA)+" crf="+str(self.crfA)+" resolution="+str(self.widthA)+"x"+str(self.heightA)+")")
			#Calculo bitrate del video A
			self.avg_bitrateA=FFMPEG.getBitrate(self.outputA)
			
			

	def genVideoB(self):
		while True:
			if (self.primerVideoB == 1):
				## Generacion video B
				#Lanzo ffmpeg paraq video B
				self.outputB="./tmp/B.mp4"
				#self.fpsB=self.fpsB-fps_step
				FFMPEG.launchCommand(self.videoRef,str(self.fpsB),str(self.crfB),str(self.widthB)+":"+str(self.heightB),self.outputB)
				self.logFile.write("\n(He generado el primer video de B)")
				#Calculo bitrate del video A
				self.avg_bitrateB=FFMPEG.getBitrate(self.outputB)
				self.primerVideoB=0

			#Si continuo cumpliendo el objetivo de bitrate no hago nada
			if (self.avg_bitrateB<float(self.target_bitrate)):
				print("#### Video B preparado: fps="+str(self.fpsB)+" crf="+str(self.crfB)+" resolution="+str(self.widthB)+"x"+str(self.heightB)+" bitrate="+str(self.avg_bitrateB)+" kbits/s")
				self.logFile.write("\n#### Video B preparado: fps="+str(self.fpsB)+" crf="+str(self.crfB)+" resolution="+str(self.widthB)+"x"+str(self.heightB)+" bitrate="+str(self.avg_bitrateB)+" kbits/s")
				self.prefpsB=self.fpsB
				self.precrfB=self.crfB
				self.prewidthB=self.widthB
				self.preheightB=self.heightB
				break
			else:
				self.fpsB=self.fpsB-self.fps_step
				if (self.fpsB < self.fps_step or self.crfB > 51):
					break


			#No se cumple condicion de bitrate --> borramos video, degradamos parámetro A y volvemos a crear video
			os.system(("rm "+self.outputB))
			if (self.videoElegido == 'A'):
				self.widthB = self.prewidthA
				self.heightB = self.preheightA
			# elif (self.videoElegido == 'B'):
			# 	#self.fpsB = self.prefpsB
			elif (self.videoElegido == 'C'):
				self.crfB = self.precrfC
			elif (self.videoElegido == 'A=B'):
				self.widthB = self.prewidthA
				self.heightB = self.preheightA
				#self.widthA , self.heightA = FFMPEG.reSize(self.widthA,self.heightA,self.res_step)
				#if (self.heightA < self.res_step or self.crfA > 51):
				#	break
				#self.fpsB = self.prefpsB
			elif (self.videoElegido == 'A=C'):
				self.widthB = self.prewidthA
				self.heightB = self.preheightA
				#self.widthA , self.heightA = FFMPEG.reSize(self.widthA,self.heightA,self.res_step)
				#if (self.heightA < self.res_step or self.crfA > 51):
				#	break
				self.crfB = self.precrfC
			elif (self.videoElegido == 'B=C'):
				#self.fpsB = self.prefpsB
				self.crfA = self.precrfC
			elif (self.videoElegido == 'A=B=C'):
				self.widthB = self.prewidthA
				self.heightB = self.preheightA
				#self.widthA , self.heightA = FFMPEG.reSize(self.widthA,self.heightA,self.res_step)
				#if (self.heightA < self.res_step or self.crfA > 51):
				#	break
				#self.fpsA = self.prefpsB
				self.crfA = self.precrfC



			## Generacion video B
			#Lanzo ffmpeg paraq video B
			#self.outputB="B.mp4"
			#self.fpsB=self.fpsB-fps_step
			FFMPEG.launchCommand(self.videoRef,str(self.fpsB),str(self.crfB),str(self.widthB)+":"+str(self.heightB),self.outputB)
			self.logFile.write("\n(Genero un nuevo video de B--> fps="+str(self.fpsB)+" crf="+str(self.crfB)+" resolution="+str(self.widthB)+"x"+str(self.heightB)+")")
			#Calculo bitrate del video A
			self.avg_bitrateB=FFMPEG.getBitrate(self.outputB)
				
			
	def genVideoC(self):
		while True:
			if (self.primerVideoC == 1):
				## Generacion video C
				#Lanzo ffmpeg paraq video C
				self.outputC="./tmp/C.mp4"
				#self.crfC=self.crfC+crf_step
				FFMPEG.launchCommand(self.videoRef,str(self.fpsC),str(self.crfC),str(self.widthC)+":"+str(self.heightC),self.outputC)
				self.logFile.write("\n(He generado el primer video de C)")
				#Calculo bitrate del video C
				self.avg_bitrateC=FFMPEG.getBitrate(self.outputC)
				self.primerVideoC=0

			#Si continuo cumpliendo el objetivo de bitrate no hago nada
			if (self.avg_bitrateC<float(self.target_bitrate)):
				print("#### Video C preparado: fps="+str(self.fpsC)+" crf="+str(self.crfC)+" resolution="+str(self.widthC)+"x"+str(self.heightC)+" bitrate="+str(self.avg_bitrateC)+" kbits/s")
				self.logFile.write("\n#### Video C preparado: fps="+str(self.fpsC)+" crf="+str(self.crfC)+" resolution="+str(self.widthC)+"x"+str(self.heightC)+" bitrate="+str(self.avg_bitrateC)+" kbits/s")
				self.prefpsC=self.fpsC
				self.precrfC=self.crfC
				self.prewidthC=self.widthC
				self.preheightC=self.heightC
				break
			else:
				self.crfC=self.crfC+self.crf_step
				if (self.crfC > 51):
					break

			#No se cumple condicion de bitrate --> borramos video, degradamos parámetro A y volvemos a crear video
			os.system(("rm "+self.outputC))
			if (self.videoElegido == 'A'):
				self.widthC = self.prewidthA
				self.heightC = self.preheightA
			elif (self.videoElegido == 'B'):
				self.fpsC = self.prefpsC
			# elif (self.videoElegido == 'C'):
			# 	#self.crfB = self.precrfC
			elif (self.videoElegido == 'A=B'):
				self.widthC = self.prewidthA
				self.heightC = self.preheightA
				#self.widthA , self.heightA = FFMPEG.reSize(self.widthA,self.heightA,self.res_step)
				#if (self.heightA < self.res_step or self.crfA > 51):
				#	break
				self.fpsC = self.prefpsB
			elif (self.videoElegido == 'A=C'):
				self.widthC = self.prewidthA
				self.heightC = self.preheightA
				#self.widthA , self.heightA = FFMPEG.reSize(self.widthA,self.heightA,self.res_step)
				#if (self.heightA < self.res_step or self.crfA > 51):
				#	break
				#self.crfB = self.precrfC
			elif (self.videoElegido == 'B=C'):
				self.fpsC = self.prefpsB
				#self.crfA = self.precrfC
			elif (self.videoElegido == 'A=B=C'):
				self.widthC = self.prewidthA
				self.heightC = self.preheightA
				#self.widthA , self.heightA = FFMPEG.reSize(self.widthA,self.heightA,self.res_step)
				#if (self.heightA < self.res_step or self.crfA > 51):
				#	break
				self.fpsC = self.prefpsB
				#self.crfA = self.precrfC
			
			## Generacion video C
			#Lanzo ffmpeg paraq video C
			#self.outputC="C.mp4"
			#self.crfC=self.crfC+crf_step
			FFMPEG.launchCommand(self.videoRef,str(self.fpsC),str(self.crfC),str(self.widthC)+":"+str(self.heightC),self.outputC)
			self.logFile.write("\n(Genero un nuevo video de C--> fps="+str(self.fpsC)+" crf="+str(self.crfC)+" resolution="+str(self.widthC)+"x"+str(self.heightC)+")")
			#Calculo bitrate del video C
			self.avg_bitrateC=FFMPEG.getBitrate(self.outputC)
			

	def startBar(self):
		self.timeout_id = GObject.timeout_add(100, self.on_time_out, None)

	#def on_time_out(self, progressbar_id, user_data):
	def on_time_out(self,user_data):
		new_value = self.progressbar.get_fraction()-0.01
		self.progressbar.set_fraction(new_value)
		#new_value = progressbar_id.get_fraction()-0.01
		#progressbar_id.set_fraction(new_value)
		if new_value>0:
			# print(new_value)
			return True
		else: 
			#self.progressbar.set_text("Time Over")
			self.on_Equal_clicked(self.buttonEqual)
			#self.on_A_clicked(None)#Si se agota el tiempo entendemos '=' y me quedo con el videoA 
			return False

	def create_VoteBoxAB(self):

		self.voteBoxAB=Gtk.VBox()

		self.voteBoxAB.set_halign(Gtk.Align.CENTER)
		self.voteBoxAB.set_valign(Gtk.Align.CENTER)

		voting_title=Gtk.Label()
		#self.voteBoxAB.pack_start(voting_title,False,True,20)
		voting_title.set_markup("<span font_desc='Sans 12' foreground='#555555' size=\'"+str(self.size_font[3])+"\'>Por favor, eliga que video le ha gustado más\no si en cambio le han gustado por igual</span>")
		##voting_title.set_markup("<span font_desc='Sans 12' foreground='#555555' size='10000'>Por favor, eliga que video le ha gustado más\no si en cambio le han gustado por igual</span>")
		voting_title.set_line_wrap(True)

		hbox1 = Gtk.HBox(spacing=50)
		self.progressbar = Gtk.ProgressBar()
		hbox1.pack_start (self.progressbar,  True ,True,0)
		self.progressbar.set_fraction(1)
		# self.self.progressbar.set_text("100")
		self.progressbar.set_show_text(False)


		hbox2 = Gtk.HBox(spacing=50)

		buttonA = Gtk.Button.new_with_label("A")
		buttonA.connect("clicked",self.on_A_clicked)
		hbox2.pack_start(buttonA,True,True,0)

		self.buttonEqual = Gtk.Button.new_with_label("=")
		self.buttonEqual.connect("clicked",self.on_Equal_clicked)
		#self.buttonEqual.connect("clicked",self.on_A_clicked) #Si pulsa '='' me quedo con el videoA 
		hbox2.pack_start(self.buttonEqual,True,True,0)		

		buttonB = Gtk.Button.new_with_label("B")
		buttonB.connect("clicked",self.on_B_clicked)
		hbox2.pack_start(buttonB,True,True,0)

		self.voteBoxAB.add(voting_title)
		self.voteBoxAB.add(hbox1)
		self.voteBoxAB.add(hbox2)

	def on_A_clicked(self, button):
		print('A')
		self.videoElegido='A'
		self.logFile.write("\nEn la primera votacion se ha elegido A")
		#Guarda las variables del video C
		self.bitrateFinal=self.avg_bitrateA;
		self.fpsFinal=self.fpsA
		self.crfFinal=self.crfA
		self.wFinal=self.widthA
		self.hFinal=self.heightA
		GObject.source_remove(self.timeout_id)
		self.progressbar.set_fraction(1)
		self.voteBoxAB.hide()
		#self.voteBoxAB.unmap()

		while Gtk.events_pending():
			print("Estoy pendiente de algun evento en A")
			Gtk.main_iteration()
		
		sleep(0.5) #Esperar un poco
		
		#FFMPEG.launchVideo(self.outputA, self.outputC)
		FFMPEG.launchVideo(self.outputA, self.outputC, self.widthMax, self.heightMax)
		#p = FFMPEG.reproducirVideos(self.outputA, self.outputC)
		#p.join()
		sleep(0.5) #Esperar mientras se reproduce el video
		
		self.voteBoxXC.show()
		self.startBar2()

	def on_Equal_clicked(self, button):
		print('A=B')
		self.videoElegido='A=B'
		self.logFile.write("\nEn la primera votacion se ha elegido A=B")
		#Guarda las variables del video A
		self.bitrateFinal=self.avg_bitrateA;
		self.fpsFinal=self.fpsA
		self.crfFinal=self.crfA
		self.wFinal=self.widthA
		self.hFinal=self.heightA
		GObject.source_remove(self.timeout_id)
		self.progressbar.set_fraction(1)
		self.voteBoxAB.hide()
		#self.voteBoxAB.unmap()

		while Gtk.events_pending():
			print("Estoy pendiente de algun evento en A=B")
			Gtk.main_iteration()
		
		sleep(0.5) #Esperar un poco
		
		#FFMPEG.launchVideo(self.outputA, self.outputC)
		FFMPEG.launchVideo(self.outputA, self.outputC, self.widthMax, self.heightMax)
		#p = FFMPEG.reproducirVideos(self.outputA, self.outputC)
		#p.join()
		sleep(0.5) #Esperar mientras se reproduce el video
		
		self.voteBoxXC.show()
		self.startBar2()

	def on_B_clicked(self, button):
		print("B")
		self.videoElegido='B'
		self.logFile.write("\nEn la primera votacion se ha elegido B")
		GObject.source_remove(self.timeout_id)
		self.progressbar.set_fraction(1)
		self.voteBoxAB.hide()

		while Gtk.events_pending():
			print("Estoy pendiente de algun evento en B")
			Gtk.main_iteration()
		
		sleep(0.5) #Esperar un poco

		#FFMPEG.launchVideo(self.outputB, self.outputC)
		FFMPEG.launchVideo(self.outputB, self.outputC, self.widthMax, self.heightMax)
		#p = FFMPEG.reproducirVideos(self.outputB, self.outputC)
		sleep(0.5) #Esperar mientras se reproduce el video
		
		self.voteBoxXC.show()
		self.startBar2()

		#self.continue_button_startTest(None) #Siguiente paso

	def create_VoteBoxXC(self):

		self.voteBoxXC=Gtk.VBox()

		self.voteBoxXC.set_halign(Gtk.Align.CENTER)
		self.voteBoxXC.set_valign(Gtk.Align.CENTER)

		voting_title=Gtk.Label()
		#self.voteBoxXC.pack_start(voting_title,False,True,20)
		voting_title.set_markup("<span font_desc='Sans 12' foreground='#555555' size=\'"+str(self.size_font[3])+"\'>Por favor, eliga que video le ha gustado más\no si en cambio le han gustado por igual</span>")
		##voting_title.set_markup("<span font_desc='Sans 12' foreground='#555555' size='10000'>Por favor, eliga que video le ha gustado más\no si en cambio le han gustado por igual</span>")
		voting_title.set_line_wrap(True)

		hbox1 = Gtk.HBox(spacing=50)
		self.progressbar2 = Gtk.ProgressBar()
		hbox1.pack_start (self.progressbar2,  True ,True,0)
		self.progressbar2.set_fraction(1)
		# self.self.progressbar2.set_text("100")
		self.progressbar2.set_show_text(False)


		hbox2 = Gtk.HBox(spacing=50)

		buttonA = Gtk.Button.new_with_label("A")
		buttonA.connect("clicked",self.on_A_clicked2)
		hbox2.pack_start(buttonA,True,True,0)

		self.buttonEqual2 = Gtk.Button.new_with_label("=")
		self.buttonEqual2.connect("clicked",self.on_Equal_clicked2)
		#self.buttonEqual2.connect("clicked",self.on_A_clicked2) #Si pulsa '='' me quedo con el videoA 
		hbox2.pack_start(self.buttonEqual2,True,True,0)		

		buttonB = Gtk.Button.new_with_label("B")
		buttonB.connect("clicked",self.on_B_clicked2)
		hbox2.pack_start(buttonB,True,True,0)

		self.voteBoxXC.add(voting_title)
		self.voteBoxXC.add(hbox1)
		self.voteBoxXC.add(hbox2)

	def startBar2(self):
		self.timeout_id2 = GObject.timeout_add(100, self.on_time_out2, None)

	#def on_time_out(self, progressbar_id, user_data):
	def on_time_out2(self, user_data):
		new_value2 = self.progressbar2.get_fraction()-0.01
		self.progressbar2.set_fraction(new_value2)
		#new_value = progressbar_id.get_fraction()-0.01
		#progressbar_id.set_fraction(new_value)
		if new_value2>0:
			# print(new_value)
			return True
		else: 
			#self.progressbar.set_text("Time Over")
			self.on_Equal_clicked2(self.buttonEqual2)
			#self.on_A_clicked2(None)#Si se agota el tiempo entendemos '=' y me quedo con el videoA 
			return False


	def on_A_clicked2(self, button):
		print('A o B')
		self.logFile.write("\nEn la segunda votacion se ha elegido A")
		if self.videoElegido == 'A=B':
			self.videoElegido='A=B'
			#Guarda las variables del video A y B
			#BBDD.writeTest(self.pruebaBBDD, self.avg_bitrateA,self.fpsA, self.crfA, self.widthA, self.heightA)
			#BBDD.writeTest(self.pruebaBBDD, self.avg_bitrateB,self.fpsB, self.crfB, self.widthB, self.heightB)
			#BBDD.writeTest(self.pruebaBBDD, self.target_bitrate,self.fpsA, self.crfA, self.widthA, self.heightA)
			#BBDD.writeTest(self.pruebaBBDD, self.target_bitrate,self.fpsB, self.crfB, self.widthB, self.heightB)
			BBDD.writeTest(self.pruebaBBDD, self.target_bitrate, self.avg_bitrateA, self.fpsA, self.crfA, self.widthA, self.heightA)
			BBDD.writeTest(self.pruebaBBDD, self.target_bitrate, self.avg_bitrateB, self.fpsB, self.crfB, self.widthB, self.heightB)
		if self.videoElegido == 'A':
			self.videoElegido='A'
			#Guarda las variables del video A
			#self.bitrateFinal=self.avg_bitrateA;
			#self.fpsFinal=self.fpsA
			#self.crfFinal=self.crfA
			#self.wFinal=self.widthA
			#self.hFinal=self.heightA
			#BBDD.writeTest(self.pruebaBBDD, self.avg_bitrateA,self.fpsA, self.crfA, self.widthA, self.heightA)
			#BBDD.writeTest(self.pruebaBBDD, self.target_bitrate,self.fpsA, self.crfA, self.widthA, self.heightA)
			BBDD.writeTest(self.pruebaBBDD, self.target_bitrate,self.avg_bitrateA,self.fpsA, self.crfA, self.widthA, self.heightA)
		if self.videoElegido == 'B':
			self.videoElegido='B'
			#Guarda las variables del video B
			self.bitrateFinal=self.avg_bitrateB;
			self.fpsFinal=self.fpsB
			self.crfFinal=self.crfB
			self.wFinal=self.widthB
			self.hFinal=self.heightB
			#BBDD.writeTest(self.pruebaBBDD, self.avg_bitrateB,self.fpsB, self.crfB, self.widthB, self.heightB)
			#BBDD.writeTest(self.pruebaBBDD,  self.target_bitrate,self.fpsB, self.crfB, self.widthB, self.heightB)
			BBDD.writeTest(self.pruebaBBDD, self.target_bitrate,self.avg_bitrateB,self.fpsB, self.crfB, self.widthB, self.heightB)

		GObject.source_remove(self.timeout_id2)
		self.voteBoxXC.hide()
		self.progressbar2.set_fraction(1)

		sleep(0.5) #Esperar un poco
		#print("Aquí se guarda los datos en la base de datos y comenzar de nuevo")
		#BBDD.writeTest(self.pruebaBBDD, self.bitrateFinal,self.fpsFinal, self.crfFinal, self.wFinal, self.hFinal)

		self.logFile.flush()

		self.continue_button_startTest(None)
		#self.hilo=threading.Thread(target=self.videoProcess)
		#self.hilo.start()


		#self.continue_button_startTest(None)#Siguiente paso


	def on_Equal_clicked2(self, button):
		print('AB=C')
		self.logFile.write("\nEn la segunda votacion se ha elegido AB=C")
		if self.videoElegido == 'A=B':
			self.videoElegido='A=B=C'
			#Guarda las variables del video A, B y C
			#BBDD.writeTest(self.pruebaBBDD, self.avg_bitrateA,self.fpsA, self.crfA, self.widthA, self.heightA)
			#BBDD.writeTest(self.pruebaBBDD, self.avg_bitrateB,self.fpsB, self.crfB, self.widthB, self.heightB)
			#BBDD.writeTest(self.pruebaBBDD, self.avg_bitrateC,self.fpsC, self.crfC, self.widthC, self.heightC)
			#BBDD.writeTest(self.pruebaBBDD, self.target_bitrate,self.fpsA, self.crfA, self.widthA, self.heightA)
			#BBDD.writeTest(self.pruebaBBDD, self.target_bitrate,self.fpsB, self.crfB, self.widthB, self.heightB)
			#BBDD.writeTest(self.pruebaBBDD, self.target_bitrate,self.fpsC, self.crfC, self.widthC, self.heightC)
			BBDD.writeTest(self.pruebaBBDD, self.target_bitrate,self.avg_bitrateA,self.fpsA, self.crfA, self.widthA, self.heightA)
			BBDD.writeTest(self.pruebaBBDD, self.target_bitrate,self.avg_bitrateB,self.fpsB, self.crfB, self.widthB, self.heightB)
			BBDD.writeTest(self.pruebaBBDD, self.target_bitrate,self.avg_bitrateC,self.fpsC, self.crfC, self.widthC, self.heightC)
		if self.videoElegido == 'A':
			self.videoElegido='A=C'	
			#Guarda las variables del video A y C
			#BBDD.writeTest(self.pruebaBBDD, self.avg_bitrateA,self.fpsA, self.crfA, self.widthA, self.heightA)
			#BBDD.writeTest(self.pruebaBBDD, self.avg_bitrateC,self.fpsC, self.crfC, self.widthC, self.heightC)
			#BBDD.writeTest(self.pruebaBBDD, self.target_bitrate,self.fpsA, self.crfA, self.widthA, self.heightA)
			#BBDD.writeTest(self.pruebaBBDD, self.target_bitrate,self.fpsC, self.crfC, self.widthC, self.heightC)
			BBDD.writeTest(self.pruebaBBDD, self.target_bitrate, self.avg_bitrateA,self.fpsA, self.crfA, self.widthA, self.heightA)
			BBDD.writeTest(self.pruebaBBDD, self.target_bitrate, self.avg_bitrateC,self.fpsC, self.crfC, self.widthC, self.heightC)
		if self.videoElegido == 'B':
			self.videoElegido='B=C'
			#Guarda las variables del video B y C
			self.bitrateFinal=self.avg_bitrateB;
			self.fpsFinal=self.fpsB
			self.crfFinal=self.crfB
			self.wFinal=self.widthB
			self.hFinal=self.heightB
			#BBDD.writeTest(self.pruebaBBDD, self.avg_bitrateB,self.fpsB, self.crfB, self.widthB, self.heightB)
			#BBDD.writeTest(self.pruebaBBDD, self.avg_bitrateC,self.fpsC, self.crfC, self.widthC, self.heightC)
			#BBDD.writeTest(self.pruebaBBDD, self.target_bitrate,self.fpsB, self.crfB, self.widthB, self.heightB)
			#BBDD.writeTest(self.pruebaBBDD, self.target_bitrate,self.fpsC, self.crfC, self.widthC, self.heightC)
			BBDD.writeTest(self.pruebaBBDD, self.target_bitrate,self.avg_bitrateB,self.fpsB, self.crfB, self.widthB, self.heightB)
			BBDD.writeTest(self.pruebaBBDD, self.target_bitrate,self.avg_bitrateC,self.fpsC, self.crfC, self.widthC, self.heightC)

		GObject.source_remove(self.timeout_id2)
		self.voteBoxXC.hide()
		self.progressbar2.set_fraction(1)

		sleep(0.5) #Esperar un poco
		#print("Aquí se guarda los datos en la base de datos y comenzar de nuevo")
		#BBDD.writeTest(self.pruebaBBDD, self.bitrateFinal,self.fpsFinal, self.crfFinal, self.wFinal, self.hFinal)

		self.logFile.flush()

		self.continue_button_startTest(None)
		#self.hilo=threading.Thread(target=self.videoProcess)
		#self.hilo.start()


	def on_B_clicked2(self, button):
		print("C")
		self.logFile.write("\nEn la segunda votacion se ha elegido B")
		self.videoElegido='C'
		#Guarda las variables del video C
		self.bitrateFinal=self.avg_bitrateC;
		self.fpsFinal=self.fpsC
		self.crfFinal=self.crfC
		self.wFinal=self.widthC
		self.hFinal=self.heightC
		GObject.source_remove(self.timeout_id2)
		self.voteBoxXC.hide()
		self.progressbar2.set_fraction(1)

		sleep(0.5) #Esperar un poco
		#print("Aquí se guarda los datos en la base de datos y comenzar de nuevo")
		#BBDD.writeTest(self.pruebaBBDD, self.bitrateFinal, self.fpsFinal, self.crfFinal, self.wFinal, self.hFinal)
		#BBDD.writeTest(self.pruebaBBDD, self.target_bitrate, self.fpsFinal, self.crfFinal, self.wFinal, self.hFinal)
		BBDD.writeTest(self.pruebaBBDD, self.target_bitrate,self.bitrateFinal, self.fpsFinal, self.crfFinal, self.wFinal, self.hFinal)

		self.logFile.flush()

		self.continue_button_startTest(None)
		#self.hilo=threading.Thread(target=self.videoProcess)
		#self.hilo.start()

	def create_finPruebaBox(self):
		self.finprueba_box = Gtk.VBox(spacing=10)
		#self.add(self.instructions_box)
		self.finprueba_box.set_border_width(200)

		self.finprueba_box.set_halign(Gtk.Align.CENTER)
		self.finprueba_box.set_valign(Gtk.Align.CENTER)

		self.finprueba_title=Gtk.Label()
		self.finprueba_title.set_markup("<span font_desc='Sans 12' foreground='#555555' size=\'"+str(self.size_font[2])+"\'>La prueba ha finalizado</span>")
		##self.finprueba_title.set_markup("<span font_desc='Sans 12' foreground='#555555' size='10000'>La prueba ha finalizado</span>")
		#self.finprueba_box.pack_start(self.finprueba_title,False,True,20)

		hbox3 = Gtk.HBox(spacing=50)		

		button_NewTest=Gtk.Button("Comenzar un nueva prueba")
		button_NewTest.connect("clicked",self.newTest)
		button_NewTest.set_size_request(80,20)
		hbox3.pack_start(button_NewTest,True,True,0)

		button_Salir=Gtk.Button("Salir")
		button_Salir.connect("clicked",self.salir)
		button_Salir.set_size_request(80,20)
		hbox3.pack_start(button_Salir,True,True,0)

		self.finprueba_box.add(self.finprueba_title)
		self.finprueba_box.add(hbox3)

	def newTest(self, button):
		self.finprueba_box.hide()
		self.videoSelect_box.show()

	def salir(self, button):
		self.logFile.close()
		sys.exit()


if __name__ == '__main__':

	win = Window()

	# screen = win.get_screen()
	# m = screen.get_monitor_at_window(screen.get_active_window())
	# monitor = screen.get_monitor_geometry(m)
	# h = monitor.height
	# #print(monitor.height)
	# w = monitor.width


	#print(monitor.width)
	#win.resize(w-200,h-100)
	#win.resize(1280,800)
	win.set_position(Gtk.WindowPosition.CENTER)
	win.connect("delete-event", Gtk.main_quit)
	win.show_all()
	win.videoSelect_box.hide()
	win.instructions_box.hide()
	win.spinnerBox.hide()
	win.voteBoxAB.hide()
	win.voteBoxXC.hide()
	win.finprueba_box.hide()
	Gtk.main()
	win.logFile.close()

