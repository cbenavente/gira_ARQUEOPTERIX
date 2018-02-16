import mysql.connector
from datetime import datetime
import os


USER = 'fer'
PASS = 'fer'
HOST = '138.100.53.176'
BBDD = 'arqueopterix'
TIMEOUT = 10

nameDir = "results"

# Make directory if no exist (EN WINDOWS ES DOBLE SLASH)
#if ( not os.path.exists(os.getcwd()+"\\"+ nameDir)):
if ( not os.path.exists(os.getcwd()+"/"+ nameDir)): #En ubuntu
    os.mkdir(nameDir)


#dirfich = os.getcwd() +"\\"+ nameDir
dirfich = os.getcwd() +"/"+ nameDir
dateFich = str(datetime.utcnow().strftime("%d-%m-%Y")) +"_"+  str(datetime.utcnow().strftime("%H-%M-%S"))


def writeUser(name):
    
    try:
        # Create connection with BBDD
        db = mysql.connector.connect(user=USER, password=PASS, host=HOST, database=BBDD, connection_timeout=TIMEOUT)
        cur = db.cursor()
        
        # Check if the user already exist and Insert new user if there is not previos regisrter
        query = "SELECT idUser FROM arqueopterix.Users WHERE name = '"+ name +"';"
        cur.execute(query)
        idUser = cur.fetchall()
        
        if (len(idUser) == 1):
            idUser = idUser[0][0]
        else:
            query = "INSERT INTO arqueopterix.Users (name) VALUES ('"+ name +"');"
            cur.execute(query)
            # Get the id of the user
            idUser = cur.lastrowid
            db.commit()
        db.close()
        
    except mysql.connector.Error as err:
        print(err)
        idUser = 0
        
    #Escribir en el fichero:
    global aux_n
    #aux_n = (dirfich+"\\"+ name +"_"+ dateFich + ".txt") #En windows
    aux_n = (dirfich+"/"+ name +"_"+ dateFich + ".txt") #En linux
    f = open(aux_n, "w")
    f.write(" \nUser name: "+ str(name) + " \n\n")     
    f.close()
    
    return idUser

def writePrueba(idUser, startDate, videoName,):
    
    if (idUser != 0):
        # Create connection with BBDD
        db = mysql.connector.connect(user=USER, password=PASS, host=HOST, database=BBDD)
        cur = db.cursor()
        
        #Insert Prueba
        query = ("INSERT INTO arqueopterix.Prueba (idUser, startDate, videoName) VALUES ('"+ 
                 str(idUser) +"','"+ str(startDate) +"','"+ videoName +"');")
        cur.execute(query)
        
        #Get the id of the Prueba
        idPrueba = cur.lastrowid
        
        db.commit()
        db.close()
    else:
        idPrueba = 0
    
    #Escribir en el fichero:
    f = open(aux_n, "a")
    f.write("_________________________________________________________________________\n")
    f.write("\nStart time: "+ str(startDate) + "\n")
    f.write("Video name: "+ str(videoName) + "\n\n")           
    f.write("#targetRate\tbitRate\tfps\tcrf\twidth\theight\n")   
    f.close()
            
    return idPrueba

def writeTest(idPrueba, targetRate, bitRate, fps, crf, width, height):
    
    if (idPrueba != 0):
        # Create connection with BBDD
        db = mysql.connector.connect(user=USER, password=PASS, host=HOST, database=BBDD)
        cur = db.cursor()
        
         #Insert test results
        query = ("INSERT INTO arqueopterix.testResult (idPrueba, targetRate, bitRate, fps, crf, width, height)" +
                 "VALUES ('"+ str(idPrueba) +"','"+ str(targetRate) +"','"+ str(bitRate) +"','"+ str(fps) +"','"+ str(crf) +"','"+ str(width) +"','"+ str(height) +"');")
        cur.execute(query)
        
        db.commit()
        db.close()
    
    #Escribir en el fichero:
    f = open(aux_n, "a")
    f.write("  "+str(targetRate) +"    \t"+str(bitRate) +"    \t"+ str(fps) +" \t"+ str(crf) +" \t"+ str(width) +" \t"+ str(height) +"\n")    
    f.close()
    
def writeEndDate(idPrueba, endDate):
    
    if (idPrueba != 0):
        # Create connection with BBDD
        db = mysql.connector.connect(user=USER, password=PASS, host=HOST, database=BBDD)
        cur = db.cursor()
        
        #Insert endDate
        query = ("UPDATE arqueopterix.Prueba SET endDate ='"+ str(endDate) +"' WHERE idPrueba = "+ str(idPrueba) +";")
        cur.execute(query)
        db.commit()
        db.close()
     
    #Escribir en el fichero:
    f = open(aux_n, "a")
    f.write("\nEnd time: "+ str(endDate) +"\n")
    f.close() 
               


    