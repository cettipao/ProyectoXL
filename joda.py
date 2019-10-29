import sys
import PIL
import json
from PIL import Image, ImageDraw, ImageFont
import qrcode
from os import listdir
#Importar para escanear qr
import zbar
import numpy as np
import cv2
import hashlib
import os
#importar modulo tiempo
import time

from PyQt4 import QtCore, QtGui, uic
qtCreatorFile = "addGuest.ui" # Enter file here.
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

qtCreatorFileMain = "main.ui" # Enter file here.
Ui_MainWindowMain, QtBaseClassMain = uic.loadUiType(qtCreatorFileMain)

class Invitado:
    def __init__(self,nombre,apellido,sexo,dni,horaEntrada=None):
        self.nombre = nombre
        self.apellido = apellido
        self.sexo = sexo
        self.id = dni
        self.horaEntrada = horaEntrada

class GestorInvitados:
    def __init__(self, esperados = [], adentro = []):
        self.esperados = esperados
        self.adentro = adentro

    def isInvitadoEsperado(self,id_):
        for invitado in self.esperados:
            if(id_ == invitado.id):
                print (invitado.nombre + " " + invitado.apellido + " encontrado")
                return True
        return False
        
    def getInvitadoEsperadoById(self,id_):
        for invitado in self.esperados:
            if(id_ == invitado.id):
                return invitado
        return False

    def idInvitadoAdentro(self,id_):
        if not self.adentro:
            return
        for invitado in self.adentro:
            if(id_ == invitado.id):
                print (invitado.nombre + " " + invitado.apellido + " ya esta adentro")
                return True
        return False


    def addInvitadoEsperado(self,nombre,apellido,sexo,dni):
        invitado = Invitado(nombre,apellido,sexo,dni)
        self.esperados.append(invitado)
        print(invitado.nombre + " " + invitado.apellido + " agregado a espera")

    def removeInvitadoEsperado(self,invitado):
        index = None
        for i in range(len(self.esperados)):
            if invitado.id == self.esperados[i].id:
                index = i

        self.esperados.pop(index)

    def addInvitadoAdentro(self,invitado):
        index = None
        for i in range(len(self.esperados)):
            if invitado.id == self.esperados[i].id:
                index = i

        self.esperados.pop(index)
        ######


        self.adentro.append(invitado)
        print (invitado.nombre + " " + invitado.apellido + " agregado a Adentro y eliminado de Espera")

class FileManager():
    def __init__(self):
        self.gestorInvitados = GestorInvitados()

    def guardar(self):
        with open("invitadosEsperadosData.txt", "r") as f:
            data = json.loads(f.read())
            data["nombres"] = []
            data["apellidos"]= []
            data["sexos"]= []
            data["ids"]= []
            data["horaEntradas"]= []
####
      

            for invitado in self.gestorInvitados.esperados:
                data["nombres"].append(u'{}'.format(invitado.nombre))
                data["apellidos"].append(u'{}'.format(invitado.apellido))
                data["sexos"].append(u'{}'.format(invitado.sexo))
                data["ids"].append(u'{}'.format(invitado.id))
                data["horaEntradas"].append(u'{}'.format(invitado.horaEntrada))


        with open("invitadosEsperadosData.txt", "w") as f:
####
         
            f.write(json.dumps(data))

        with open("invitadosAdentroData.txt", "r") as f:
            data = json.loads(f.read())
            for invitado in self.gestorInvitados.adentro:
                if(invitado.id not in data["ids"]):
                    data["nombres"].append(u'{}'.format(invitado.nombre))
                    data["apellidos"].append(u'{}'.format(invitado.apellido))
                    data["sexos"].append(u'{}'.format(invitado.sexo))
                    data["ids"].append(u'{}'.format(invitado.id))
                    data["horaEntradas"].append(u'{}'.format(invitado.horaEntrada))


        with open("invitadosAdentroData.txt", "w") as f:
            f.write(json.dumps(data))

    def cargar(self):
        self.gestorInvitados = GestorInvitados([],[])

        with open("invitadosEsperadosData.txt", 'r') as f:
            data = json.loads(f.read())
            

            for i in range(len(data["nombres"])):
                nombre = data["nombres"][i]
                apellido = data["apellidos"][i]
                sexo = data["sexos"][i]
                horaEntrada = data["horaEntradas"][i]
                dni = data["ids"][i]
                invitado = Invitado(nombre,apellido,sexo,dni,horaEntrada)
                self.gestorInvitados.esperados.append(invitado)

            with open("invitadosAdentroData.txt", 'r') as f:
                data = json.loads(f.read())
                

                for i in range(len(data["nombres"])):
                    nombre = data["nombres"][i]
                    apellido = data["apellidos"][i]
                    sexo = data["sexos"][i]
                    dni = data["ids"][i]
                    horaEntrada = data["horaEntradas"][i]
                    invitado = Invitado(nombre,apellido,sexo,dni,horaEntrada)
                    self.gestorInvitados.adentro.append(invitado)
            
            #self.gestorInvitados = GestorInvitados(esperados,adentro)
            
class LectorQr:
    def __init__(self):
        print("Lector Incializado")
    def escaneo(self):

        # Inicializar la camara
        
        capture = cv2.VideoCapture(0)
        # Cargar la fuente
        font = cv2.FONT_HERSHEY_SIMPLEX

        while 1:
            # Capturar un frame
            val, frame = capture.read()

            if val:
                # Capturar un frame con la camara y guardar sus dimensiones
                frame_gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                dimensiones = frame_gris.shape  # 'dimensiones' sera un array que contendra el alto, el ancho y los canales de la imagen en este orden.

                # Convertir la imagen de OpenCV a una imagen que la libreria ZBAR pueda entender
                imagen_zbar = zbar.Image(dimensiones[1], dimensiones[0], 'Y800', frame_gris.tobytes())

                # Construir un objeto de tipo scaner, que permitira escanear la imagen en busca de codigos QR
                escaner = zbar.ImageScanner()

                # Escanear la imagen y guardar todos los codigos QR que se encuentren
                escaner.scan(imagen_zbar)

                for codigo_qr in imagen_zbar:
                    loc = codigo_qr.location  # Guardar las coordenadas de las esquinas
                    dat = codigo_qr.data[:-2]  # Guardar el mensaje del codigo QR. Los ultimos dos caracteres son saltos de linea que hay que eliminar
                    # Convertir las coordenadas de las cuatro esquinas a un array de numpy
                    cv2.destroyAllWindows()
                    return codigo_qr.data


                # Mostrar la imagen
                cv2.imshow('Imagen', frame)

            # Salir con 'ESC'
            k = cv2.waitKey(5) & 0xFF
            if k == 27:
                break

        cv2.destroyAllWindows()

class MyAppMain(QtGui.QMainWindow, Ui_MainWindowMain):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        Ui_MainWindowMain.__init__(self)
        self.setupUi(self)

        self.fileManager = FileManager()
        self.fileManager.cargar()

        self.escan.triggered.connect(self.escanear)
        self.agre.triggered.connect(self.abrirAdd)
        self.resu.triggered.connect(self.resum)
        self.ingreList.triggered.connect(self.ingreLista)
        self.delet.triggered.connect(self.removeInvitado)
        self.actualizarTablas()

    def warning(self, title, message):
        msgBox = QtGui.QMessageBox()
        msgBox.setIcon(QtGui.QMessageBox.Warning)
        msgBox.setWindowTitle(title)
        msgBox.setText(message)
        msgBox.setStandardButtons(QtGui.QMessageBox.Ok)
        msgBox.exec_()

    def removeInvitado(self):
        self.fileManager.cargar()
        dni = raw_input("Ingrese DNI de usuario a eliminar")
        if self.fileManager.gestorInvitados.getInvitadoEsperadoById(dni)==False:
            print "Invitado no encotrado"
            return
        invitado = self.fileManager.gestorInvitados.getInvitadoEsperadoById(dni)
        self.fileManager.gestorInvitados.removeInvitadoEsperado(invitado)
        print "{} {}, DNI: {} eliminado de espera".format(invitado.nombre,invitado.apellido,invitado.id)
        self.fileManager.guardar()
        self.actualizarTablas()
        self.warning("AVISO", "Recuerda eliminar la foto")

    def ingreLista(self):
        lista = raw_input("Ingresa la lista")
        nombres =[]
        apellidos = []
        dnis = []
        nombre = ""
        apellido = ""
        dni = ""
        i = 0
        
        for letra in lista:
            if(letra == " "):
                print i
                print nombre
                print apellido
                print dni
                if(i==0):
                    nombres.append(nombre)
                    nombre = ""
                    i=1
                elif(i==1):
                    apellidos.append(apellido)
                    apellido = ""
                    i=2
                elif(i==2):
                    dnis.append(dni)
                    dni = ""
                    i=0
                pass
            else:
                if(i==0):
                    nombre+=letra
                elif(i==1):
                    apellido+=letra
                elif(i==2):
                    dni+= letra

        print nombres, apellidos, dnis
        
        for i in range(len(nombres)):
            print("{}. Nombre: {}, Apellido: {}, Dni: {}".format(i+1,nombres[i],apellidos[i],dnis[i]))

        self.actualizarTablas()

            


    def resum(self):
        print ("Invitados Esperados")
        print("")
        varones = 0
        mujeres = 0
        i = 1
        for invitado in self.fileManager.gestorInvitados.esperados:
            print ("{}. Nombre: {}, Apellido: {}, Sexo: {}, ID: {}".format((i),invitado.nombre,invitado.apellido,invitado.sexo,invitado.id))
            i+=1
            if(invitado.sexo == "Hombre"):
                varones += 1
            else:
                mujeres+=1
        print ("Resumen: {} totales, {} varones y {} mujeres".format((i-1),varones,mujeres))
        print("***********************************************")
        print ("Invitados Adentro")
        print("")
        varones = 0
        mujeres = 0
        i = 1
        for invitado in self.fileManager.gestorInvitados.adentro:
            hora = "None"
            if (invitado.horaEntrada != None):
                hora = invitado.horaEntrada
            print ("{}. Nombre: {}, Apellido: {}, Sexo: {}, ID: {}, Hora entrada: {}".format((i),invitado.nombre,invitado.apellido,invitado.sexo,invitado.id,hora))
            i+=1
            if(invitado.sexo == "Hombre"):
                varones += 1
            else:
                mujeres+=1
        print ("Resumen: {} totales, {} varones y {} mujeres".format((i-1),varones,mujeres))

    def abrirAdd(self):
        print("Abriendo")
        window2.show()
        window2.setFileManager(self.fileManager,self)

    def orden(self, lista):
        apellidos = []
        for invitado in lista:
            apellidos.append(invitado.apellido)
        
        apellidos.sort()

        invitados = []
        for invitado in range(len(apellidos)):
            for inv in lista:
                if(inv.apellido == apellidos[invitado]):
                    invitados.append(inv)

        return invitados


    def actualizarTablas(self):

        self.fileManager.cargar()

        entries = []
        
        for invitado in self.orden(self.fileManager.gestorInvitados.esperados):
            entries.append(invitado.apellido + " " + invitado.nombre)

        model = QtGui.QStandardItemModel()
        self.listView.setModel(model)

        for i in entries:
            item = QtGui.QStandardItem(i)
            model.appendRow(item)

        entries = []
        for invitado in self.orden(self.fileManager.gestorInvitados.adentro):
            
            entries.append(invitado.apellido + " " + invitado.nombre)

        model = QtGui.QStandardItemModel()
        self.listView2.setModel(model)

        for i in entries:
            item = QtGui.QStandardItem(i)
            model.appendRow(item)


    def escanear(self):
        lector = LectorQr()
        id = lector.escaneo()
        print(id)
        if self.fileManager.gestorInvitados.idInvitadoAdentro(id):
            self.warning('Aviso', '{} ya esta adentro'.format(id))
        elif self.fileManager.gestorInvitados.isInvitadoEsperado(id) != False:
            invitado = self.fileManager.gestorInvitados.getInvitadoEsperadoById(id)
            

            #Invitado Hora de entrada
            tiempo_entrada = time.localtime()

            invitado.horaEntrada = str(time.asctime(tiempo_entrada))

            print("{} {} ingreso a la joda a las {}".format(invitado.nombre,invitado.apellido,str(time.asctime(tiempo_entrada))))
           
            self.fileManager.gestorInvitados.addInvitadoAdentro(invitado)
            #Etiquetas
            self.lblName.setText(invitado.nombre)
            self.lblSur.setText(invitado.apellido)
            self.lblId.setText(invitado.id)
            self.lblSex.setText(invitado.sexo)
            self.lblTim.setText(str(time.asctime(tiempo_entrada)))

            
            self.fileManager.guardar()

            self.actualizarTablas()
        else:
            self.warning("Aviso","{} no existe".format(id))


class MyApp(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

    def setFileManager(self,fileManager,myAppMain):
        self.fileManager = fileManager
        self.myAppMain = myAppMain

    def addGuest(self):
        name = self.txtName.text()
        surname = self.txtSurname.text()
        sexo = self.comboBox.currentText()
        dni = self.txtDni.text()

        if (len(dni)!=8):
            print "DNI no valido"
            return

        if(self.fileManager.gestorInvitados.getInvitadoEsperadoById(str(dni))!= False):
            print"Invitado ya agregado"
            return

        print(dni)
        print(str(dni))

        logo = qrcode.make(dni)
        logo = logo.resize((200,200))
        logo = logo.crop((15, 15, 185, 185))

        #f = open('qr/'+ str(name+surname) + '.png', 'wb')
        #img.save(f)
        #f.close()

        img = Image.open("flyer.png")

        #Escribe el Nombre
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype("arial.ttf", 60)
        texto = str(name + " " + surname)

        # Centrar texto vertical y horizontalmente.
        lines = texto.splitlines()
        w = font.getsize(max(lines, key=lambda s: len(s)))[0]
        h = font.getsize(texto)[1] * len(lines)
        x, y = img.size
        x /= 2
        x -= w / 2
        y /= 2
        y -= h / 2

            
        draw.multiline_text((x, 460), texto, font=font, fill="white",align="center")


        #Pega el Qr
        
        #log = Image.open("qr/" + (name+surname)+".png")
        img.convert('RGBA')
        img.paste(logo, (190, 540), logo)

        

        #guarda
        f = open('invitaciones/'+ str(name+surname) + '.png', 'wb')
        img.save(f)
        f.close()

        self.txtName.setText("")
        self.txtSurname.setText("")
        self.txtDni.setText("")

        #Crea invitado
        
        self.fileManager.gestorInvitados.addInvitadoEsperado(str(name),str(surname),str(sexo),str(dni))
        self.fileManager.guardar()
        self.fileManager.cargar()
        self.myAppMain.actualizarTablas()


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MyAppMain()
    window2 = MyApp()
    window.show()
    sys.exit(app.exec_())
