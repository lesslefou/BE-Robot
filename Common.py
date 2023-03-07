# ******************************************************************************
# *   ______
# *  / _____) /|
# * | |      / /     Python RobX utility
# * | | /\  / /
# * | | \ \/ /  _
# * | |  \__/  | |
# * | |________| |
# *  \__________/    (c) KEOLABS 2016
# *
# ******************************************************************************
# *  @file  Common.py
# *  @brief Common functions for Robx
# ******************************************************************************
# *  Revision  | Date      | Author       | Description
# ******************************************************************************
# *  @version V1.2
# *  @note    Added Rob6x management
# *  @date    2016/12/15
# *  @version V1.1
# *  @note    Fixed S_GetVacuum exception
# *           Added S_SearchTarget function
# *  @date    2015/09/04
# *  @version V1.0
# *  @note    Initial version
# *  @date    2013/11/06
# *  @author  KEOLABS
# ******************************************************************************
import win32com.client
import winreg
import ctypes
import sys
global Robx
import MainWindow
import time
from oscilloscopeAcquisition import *
from bddScript import *


# global RobID

# Robx choice
RobID = 0

# debug traces
# 0 = no
# 1 = yes
debug = 0

MessageBox = ctypes.windll.user32.MessageBoxA
MB_OK = 0
MB_SYSTEMMODAL = 4096
MB_ICONERROR = 16
MB_ICONWARNING = 48
NoMoreCard = 0
ret = 0

# Error constants
ERR_OK = 0
ERR_COMMERROR = 1
ERR_ROBOT = 2
ERR_LIMIT = 3
ERR_TOOLPARAM = 4
ERR_VACUUM = 5
ERR_SOFT = 6

# speed definition
def speed5axis():
    global RobID
    RobID = 5
    MAX_SPEED = 65535
    DEFAULT_SPEED = 10000
    SLOW_SPEED = 200
    MIN_SPEED = 10
    MAX_ACCEL = 5000
    DEFAULT_ACCEL = 1000
    MIN_ACCEl = 100
    XuserIn = 213
    XuserOut = -215
    Zuser = 0
    print("5 axes!")

def speed6axis():
    global RobID
    RobID = 6
    MAX_SPEED = 10000
    DEFAULT_SPEED = 1000
    SLOW_SPEED = 200
    MIN_SPEED = 10
    MAX_ACCEL = 10000
    DEFAULT_ACCEL = 2000
    MIN_ACCEl = 100
    XuserIn = 220
    XuserOut = 220
    Zuser = 0
    print("6 axes!")

# Rob6x IP address
socket = "192.168.30.33"
# 1 = Eth, 0 = serial
ModeTCP = 0;

if (RobID == 5):
    XuserIn = 213
    XuserOut = -215
    Zuser = 0
else:
    XuserIn = 220
    XuserOut = 220
    Zuser = 0

NB_STEPS_MAX = 30  # to adapt
timeToSleep = 2 #time before getting the oscilloscope acquisition when the robot moove


# ----------------------------- Generic Functions -----------------------------
def S_LogError(msg):
    MessageBox(0, str(msg), "Error", MB_OK | MB_ICONERROR | MB_SYSTEMMODAL)


def S_LogDebug(msg):
    if (debug == 1):
        MessageBox(0, str(msg), "Debug", MB_OK | MB_ICONWARNING | MB_SYSTEMMODAL)


# Call Robx ActiveX

Robx = win32com.client.Dispatch("KEOLABS.RobX")

# Retrieve used COM port
# if (RobID == 5) or (ModeTCP == 0):
#     key = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
#     hkey = winreg.OpenKey(key, r"HARDWARE\DEVICEMAP\SERIALCOMM")
#     try:
#         COM = winreg.QueryValueEx(hkey, "\Device\VCP0")[0]
#     except Exception as detail:
#         S_LogError(detail)
# else:
#     COM = "SOCKET " + socket


# ----------------------------- General Functions -----------------------------
def S_Open_Communication(COM_chose):
    print("COM_chose", COM_chose)
    # Open a communication session using port COM between PC and KEOLABS Robx
    err = Robx.OpenComm(COM_chose)
    if err != 0:
        mess = Robx.GetErrorInfo(err)
        print("Error COM!! ")
        #S_LogError(" An Error - %s - occurred during OpenComm using %s" % (mess, COM_chose))
    else:
        print("Communication ouverte")
        S_LogDebug("OpenComm Successfull, using %s" % COM_chose)
    return err


def S_Close_Communication():
    # Close the communication between PC and KEOLABS Robx
    err = Robx.CloseComm()
    if err != 0:
        mess = Robx.GetErrorInfo(err)
        S_LogError("An Error - %s - occurred during CloseComm using %s" % (mess, COM_chose))
    else:
        print("Communication fermée") #ajout pour test fonctionnalité
        S_LogDebug("CloseComm Successfull")


def S_Initialization_Engine():
    # Launch KEOLABS Robx Initialization Sequence
    try:
        err = S_SetToolParam(220)
        err = Robx.Calibrate(1)
        S_LogDebug("Initialization Successfull")
    except Exception as detail:
        S_LogError("An Error - %s - occurred during Initialization" % err)
    return err


def S_Energize(val):
    # Energize KEOLABS Robx
    # val: 0: De-energize - 1: Energize
    err = Robx.InitRobot()
    err = Robx.Energize(val)
    if err == 0:
        if val > 0:
            S_LogDebug("Energize Successfull")
        else:
            S_LogDebug("De-Energize Successfull")
    else:
        mess = Robx.GetErrorInfo(err)
        S_LogError("An Error - %s - occurred during Energize" % mess)
    return err



def S_SetSpeed(val):
    # Set KEOLABS Robx Speed
    # val: 0-65535 = 0-180 deg/s
    err = Robx.SetSpeed(val)
    if err == 0:
        S_LogDebug("Speed change Successfull")
    else:
        mess = Robx.GetErrorInfo(err)
        S_LogError("An Error - %s - occurred during S_SetSpeed" % mess)
    return err



def S_Initialization(COM_chose, RobID):
    # Robot choice
    print(RobID)
    err = Robx.RobotSelect(RobID);
    if err == 0:
        # Openning COM Port
        err = S_Open_Communication(COM_chose)
        if err == 0:
            err = Robx.InitRobot()
            if (RobID == 5):
                # Making sure Robot is correctly placed
                err = S_Energize(0)
                MessageBox(0, "Make sure Robot is approximately in Home Position", "User action required",
                           MB_OK | MB_SYSTEMMODAL)
                err = S_Energize(1)

            err = Robx.SetCartesianExtMode(0)

            # Initialisation
            if err == 0:
                err = S_Initialization_Engine()
                S_SetSpeed(10000)
    return err


# ------------------------- Tool Management Functions -------------------------
def S_SetToolParam(val):
    # Define the length of the mounted tool
    # val: length of the mounted tool in mm.
    S_LogDebug("val in S_SetToolParam = %s" % val)
    err = Robx.SetToolParam(val)
    if err != 0:
        mess = Robx.GetErrorInfo(err)
        S_LogError("An Error - %s - occurred during SetToolParam" % mess)
    return err


def S_GetToolParam():
    # Return the length of the mounted tool
    # ret tool_length: length of the mounted tool in mm.
    try:
        tool_length = Robx.GetToolParam()
        S_LogDebug("tool_length in S_GetToolParam = %s" % tool_length)
    except Exception as err:
        S_LogError("An Error - %s - occurred during GetToolParam" % err)
    return tool_length


# ----------------------------- Position Functions ----------------------------
def S_GoToHome(val):
    if val==False : val=6000
    print (val)
    #Move KEOLABS Robx to its Home Position
    #val: maximum time in milliseconds allowed for the move
    err = Robx.GotoHome(val)
    if err == 0:
        S_LogDebug("Home Position reached")
    else:
        mess = Robx.GetErrorInfo(err)
        S_LogError("An Error - %s - occurred during GotoHome" % mess)
    return err


def S_GoToUser(val):
    if val==False : val=3000
    # Move KEOLABS Robx to its User Position
    # val: maximum time in milliseconds allowed for the move
    err = Robx.GotoUserPosition(val)
    if err == 0:
        S_LogDebug("User Position reached")
    else:
        mess = Robx.GetErrorInfo(err)
        S_LogError("An Error - %s - occurred during GotoUser" % mess)
    return err


def S_GoTo(X, Y, Z, W, P, timeout):
    # Move KEOLABS Robx to the specified coordonates
    # X: (-500,500 mm): from left to right
    # Y: (-500,500 mm): from back to front
    # Z: (-500,500 mm): from down to up
    # W: (-360,360 degree): angle of wrist
    # P: (-360,360 degree): angle of pitch
    X = int(X)
    
    Y = int(Y)
    Z = int(Z)
    W = int(W)
    P = int(P)

    err = Robx.GotoPosition(X, Y, Z, W, P, timeout)
    if err != 0:
        S_LogDebug(err)
        mess = Robx.GetErrorInfo(err)
        S_LogError("An Error - %s - occurred during S_GoTo" % mess)
    else:
        S_LogDebug("GoTo: %s,%s,%s,%s,%s" % (X, Y, Z, W, P))
    return err


def S_GetCurrentPosition():
    
    # Get KEOLABS Robx Current Coordinates
    try:
        err = Robx.GetCurrentPositionStatus()
        if (err == 0):
            coordinates_str = Robx.GetCurrentPositionStr()
            coordinates = coordinates_str.split(",")
            S_LogDebug("Current Coordinates are: X = %s, Y = %s, Z = %s, W = %s, P = %s" % (
            coordinates[0], coordinates[1], coordinates[2], coordinates[3], coordinates[4]))
        else:
            S_LogError("Current position could not be retrieved" % err)
    except:
        S_LogError("An Error - %s - occurred during GetCurrentPosition" % err)
        print(coordinates)
    return coordinates

# ------------ Project-specific functions ------------
"""
 * @file        Common.py
 * @brief       Contains the functions launching the specifics desired Acquisitions 
 * @author      Lisa Duterte | Romain Derrien | Clement Rouvier | Elsa Della Valle 
 * @version     0.1
 * @date        2023
"""
    


"""
 * @brief Bring the card out of the rf field in order to unload it
"""
def goHorsChamp(Temps_limit):
    S_GoTo(0, 386, 161, -77, 57, Temps_limit) #sort du champs d'alimentation
    
"""
 * @brief NFC Acquisition
"""
def nfc(x_ptr, y_ptr, z_ptr, speed):
    print(x_ptr, y_ptr, z_ptr)
    h_nfc = 5
    rb_nfc = 5
    rh_nfc_nfc = 10
    
    h_horsChamps_nfc=150
    Temps_limit = 6000
    
    S_SetSpeed(speed)
    
    
    #bdd opening
    open_ssh_tunnel()
    mysql_connect()
    
    sendMeshTypeToBdd("nfc")
    
    #getOscillocopeConfiguration()
    print('NFC Start')
    
    S_GoTo(x_ptr, y_ptr, z_ptr, 0, 90, Temps_limit) #go to the reference point  point(0,0,0)
    S_GoTo(x_ptr-rb_nfc, y_ptr, z_ptr, 0, 90, Temps_limit) # first move from the reference point   point(-1,0,0)

    #Bdd closing
    mysql_disconnect()
    close_ssh_tunnel()
    
    
    ''' S_GoTo(x_ptr, y_ptr, z_ptr, 0, 90, Temps_limit) #go to the reference point  point(0,0,0)
    time.sleep(timeToSleep)
    getAcquisition("(0,0,0)")
    goHorsChamp(Temps_limit)
    
    S_GoTo(x_ptr-rb_nfc, y_ptr, z_ptr, 0, 90, Temps_limit) # first move from the reference point   point(-1,0,0)
    time.sleep(timeToSleep)
    getAcquisition("(-1,0,0)")
    goHorsChamp(Temps_limit)
    
    S_GoTo(x_ptr, y_ptr+rb_nfc, z_ptr, 0, 90, Temps_limit) #point(0,1,0)
    time.sleep(timeToSleep)
    getAcquisition("(0,1,0)")
    goHorsChamp(Temps_limit)
    
    S_GoTo(x_ptr+rb_nfc, y_ptr, z_ptr, 0, 90, Temps_limit) #point(1,0,0)
    time.sleep(timeToSleep)
    getAcquisition("(1,0,0)")
    goHorsChamp(Temps_limit)
    
    S_GoTo(x_ptr, y_ptr-rb_nfc, z_ptr, 0, 90, Temps_limit) #point(0,-1,0)
    time.sleep(timeToSleep)
    getAcquisition("(0,-1,0)")
    goHorsChamp(Temps_limit)

    S_GoTo(x_ptr-rh_nfc_nfc, y_ptr, z_ptr+h_nfc, 0, 90, Temps_limit) #point(-1,0,1)
    time.sleep(timeToSleep)
    getAcquisition("(-1,0,1)")
    goHorsChamp(Temps_limit)
    
    S_GoTo(x_ptr, y_ptr+rh_nfc_nfc, z_ptr+h_nfc, 0, 90, Temps_limit) #point(0,1,1)
    time.sleep(timeToSleep)
    getAcquisition("(0,1,1)")
    goHorsChamp(Temps_limit)

    S_GoTo(x_ptr+rh_nfc_nfc, y_ptr, z_ptr+h_nfc, 0, 90, Temps_limit) #point(1,0,1)
    time.sleep(timeToSleep)
    getAcquisition("(1,0,1)")
    goHorsChamp(Temps_limit)
    
    S_GoTo(x_ptr, y_ptr-rh_nfc_nfc, z_ptr+h_nfc, 0, 90, Temps_limit) #point(0,-1,1)
    time.sleep(timeToSleep)
    getAcquisition("(0,-1,1)")
    goHorsChamp(Temps_limit)
    
    S_GoTo(x_ptr, y_ptr, z_ptr+h_nfc, 0, 90, Temps_limit) #point(0,0,1)
    time.sleep(timeToSleep)
    getAcquisition("(0,0,1)")
    goHorsChamp(Temps_limit)
    
    
    #Bdd closing
    mysql_disconnect()
    close_ssh_tunnel()'''
    
    
"""
 * @brief EMVCO Acquisition
"""
def emvco(x_ptr, y_ptr, z_ptr, speed):
    print(speed)
    h_emvco = 10
    rp_emvco = 15
    rg_emvco = 25
    h_horsChamps=100
    
    Temps_limit = 6000
    
    #bdd opening
    open_ssh_tunnel()
    mysql_connect()
    

    S_SetSpeed(speed)
    
    sendMeshTypeToBdd("emvco")    
    
    getOscillocopeConfiguration()
    print('emvco start')
    
    S_GoTo(x_ptr, y_ptr, z_ptr, 0, 90, Temps_limit) #point(0,0,0)
    time.sleep(timeToSleep)
    getAcquisition("(0,0,0)")
    goHorsChamp(Temps_limit)
    
    S_GoTo(x_ptr-rg_emvco, y_ptr, z_ptr, 0, 90, Temps_limit) #point(-1,0,0)
    time.sleep(timeToSleep)
    getAcquisition("(-1,0,0)")
    goHorsChamp(Temps_limit)
    
    S_GoTo(x_ptr, y_ptr+rg_emvco, z_ptr, 0, 90, Temps_limit) #point(0,1,0)
    time.sleep(timeToSleep)
    getAcquisition("(0,1,0)")
    goHorsChamp(Temps_limit)
    
    S_GoTo(x_ptr+rg_emvco, y_ptr, z_ptr, 0, 90, Temps_limit) #point(1,0,0)
    time.sleep(timeToSleep)
    getAcquisition("(1,0,0)")
    goHorsChamp(Temps_limit)
    
    S_GoTo(x_ptr, y_ptr-rg_emvco, z_ptr, 0, 90, Temps_limit) #point(0,-1,0)
    time.sleep(timeToSleep)
    getAcquisition("(0,-1,0)")
    goHorsChamp(Temps_limit)
    
    
    S_GoTo(x_ptr, y_ptr, z_ptr+h_emvco, 0, 90, Temps_limit) #point(0,0,1)
    time.sleep(timeToSleep)
    getAcquisition("(0,0,1)")
    goHorsChamp(Temps_limit)
    
    S_GoTo(x_ptr, y_ptr+rg_emvco, z_ptr+h_emvco, 0, 90, Temps_limit) #point(0,1,1)
    time.sleep(timeToSleep)
    getAcquisition("(0,1,1)")
    goHorsChamp(Temps_limit)
    
    S_GoTo(x_ptr-rg_emvco, y_ptr, z_ptr+h_emvco, 0, 90, Temps_limit) #point(-1,0,1)
    time.sleep(timeToSleep)
    getAcquisition("(-1,0,1)")
    goHorsChamp(Temps_limit)
    
    S_GoTo(x_ptr+rg_emvco, y_ptr, z_ptr+h_emvco, 0, 90, Temps_limit) #point(1,0,1)
    time.sleep(timeToSleep)
    getAcquisition("(1,0,1)")
    goHorsChamp(Temps_limit)
    
    S_GoTo(x_ptr, y_ptr-rg_emvco, z_ptr+h_emvco, 0, 90, Temps_limit) #point(0,-1,1)
    time.sleep(timeToSleep)
    getAcquisition("(0,-1,1)")
    goHorsChamp(Temps_limit)
    
    
    S_GoTo(x_ptr, y_ptr, z_ptr+2*h_emvco, 0, 90, Temps_limit) #point(0,0,2)
    time.sleep(timeToSleep)
    getAcquisition("(0,0,2)")
    goHorsChamp(Temps_limit)
    
    S_GoTo(x_ptr, y_ptr+rp_emvco, z_ptr+2*h_emvco, 0, 90, Temps_limit) #point(0,1,2)
    time.sleep(timeToSleep)
    getAcquisition("(0,1,2)")
    goHorsChamp(Temps_limit)
    
    S_GoTo(x_ptr-rp_emvco, y_ptr, z_ptr+2*h_emvco, 0, 90, Temps_limit) #point(-1,0,2)
    time.sleep(timeToSleep)
    getAcquisition("(-1,0,2)")
    goHorsChamp(Temps_limit)
    
    S_GoTo(x_ptr, y_ptr-rp_emvco, z_ptr+2*h_emvco, 0, 90, Temps_limit) #point(0,-1,2)
    time.sleep(timeToSleep)
    getAcquisition("(0,-1,2)")
    goHorsChamp(Temps_limit)
    
    S_GoTo(x_ptr+rp_emvco, y_ptr, z_ptr+2*h_emvco, 0, 90, Temps_limit) #point(1,0,2)
    time.sleep(timeToSleep)
    getAcquisition("(1,0,2)")
    goHorsChamp(Temps_limit)
    
    
    S_GoTo(x_ptr, y_ptr, z_ptr+3*h_emvco, 0, 90, Temps_limit) #point(0,0,3)
    time.sleep(timeToSleep)
    getAcquisition("(0,0,3)")
    goHorsChamp(Temps_limit)
    
    S_GoTo(x_ptr-rp_emvco, y_ptr, z_ptr+3*h_emvco, 0, 90, Temps_limit) #point(-1,0,3)
    time.sleep(timeToSleep)
    getAcquisition("(-1,0,3)")
    goHorsChamp(Temps_limit)
    
    S_GoTo(x_ptr, y_ptr+rp_emvco, z_ptr+3*h_emvco, 0, 90, Temps_limit) #point(0,1,3)
    time.sleep(timeToSleep)
    getAcquisition("(0,1,3)")
    goHorsChamp(Temps_limit)
    
    S_GoTo(x_ptr+rp_emvco, y_ptr, z_ptr+3*h_emvco, 0, 90, Temps_limit) #point(1,0,3)
    time.sleep(timeToSleep)
    getAcquisition("(1,0,3)")
    goHorsChamp(Temps_limit)
    
    S_GoTo(x_ptr, y_ptr-rp_emvco, z_ptr+3*h_emvco, 0, 90, Temps_limit) #point(0,-1,3)
    time.sleep(timeToSleep)
    getAcquisition("(0,-1,3)")
    goHorsChamp(Temps_limit)
    
    
    S_GoTo(x_ptr, y_ptr, z_ptr+4*h_emvco, 0, 90, Temps_limit) #point(0,0,4)
    time.sleep(timeToSleep)
    getAcquisition("(0,0,4)")
    goHorsChamp(Temps_limit)
    
    S_GoTo(x_ptr-rg_emvco, y_ptr, z_ptr+4*h_emvco, 0, 90, Temps_limit) #point(-1,0,4)
    time.sleep(timeToSleep)
    getAcquisition("(-1,0,4)")
    goHorsChamp(Temps_limit)
    
    S_GoTo(x_ptr, y_ptr+rg_emvco, z_ptr+4*h_emvco, 0, 90, Temps_limit) #point(0,1,4)
    time.sleep(timeToSleep)
    getAcquisition("(0,1,4)")
    goHorsChamp(Temps_limit)
    
    S_GoTo(x_ptr+rg_emvco, y_ptr, z_ptr+4*h_emvco, 0, 90, Temps_limit) #point(1,0,4)
    time.sleep(timeToSleep)
    getAcquisition("(1,0,4)")
    goHorsChamp(Temps_limit)
    
    S_GoTo(x_ptr, y_ptr-rg_emvco, z_ptr+4*h_emvco, 0, 90, Temps_limit) #point(0,-1,4)
    time.sleep(timeToSleep)
    getAcquisition("(0,-1,4)")
    goHorsChamp(Temps_limit) 
    
    #Bdd closing
    mysql_disconnect()
    close_ssh_tunnel()
    

# ------------------------------ Vacuum Functions -----------------------------
def S_Pump(val):
    # Activate/Deactivate the KEOLABS Robx Pump
    # val: 0: Deactivate - other: Activate
    err = Robx.Pump(val)
    if err == 0:
        if val > 0:
            S_LogDebug("Activating Pump Successfull")
        else:
            S_LogDebug("Deactivating Pump Successfull")
    else:
        mess = Robx.GetErrorInfo(err)
        S_LogError("An Error - %s - occurred during Pump Management" % mess)


def S_Valve(val):
    # Activate/Deactivate the KEOLABS Robx Valve
    # val: 0: Deactivate - other: Activate
    err = Robx.Valve(val)
    if err == 0:
        if val > 0:
            S_LogDebug("Activating Valve Successfull")
        else:
            S_LogDebug("Deactivating Valve Successfull")
    else:
        mess = Robx.GetErrorInfo(err)
        S_LogError("An Error - %s - occurred during Valve Management" % err)


def S_GetVacuum():
    # Return Vacuum state
    # ret: 0: no vacuum - 1: reached
    try:
        err = Robx.GetVacuumStatus()
        if err == 0:
            vacuum = Robx.GetVacuumNum()
            if vacuum == 0:
                S_LogDebug("Vacuum is not reached")
            else:
                S_LogDebug("Vacuum is reached")
        else:
            S_LogDebug("Vacuum status could not be retrieved during S_GetVacuum")
    except Exception as detail:
        S_LogError("An Error - %s - occurred during S_GetVacuum" % err)
    return vacuum


def S_CatchCard(Xcard, Ycard, Zcard, Wcard, Pcard):
    global preparation

    i = 1
    VacuumTest = []

    ret = Robx.GotoUserPosition(2000)
    if (ret):
        MessageBox(0, Robx.GetErrorInfo(ret), "User action required", MB_OK | MB_SYSTEMMODAL)
        return ret

    # Goto intermediate position
    ret = Robx.GotoPosition(XuserIn, Ycard, Zuser, Wcard, Pcard, 5000)
    if ret:
        MessageBox(0, Robx.GetErrorInfo(ret), "User action required", MB_OK | MB_SYSTEMMODAL)
        return ret

    # Move over the storehouse
    ret = Robx.GotoPosition(Xcard, Ycard, Zcard, Wcard, Pcard, 5000)
    if (ret):
        MessageBox(0, Robx.GetErrorInfo(ret), "User action required", MB_OK | MB_SYSTEMMODAL)
        return ret

    # Move to the top of the storehouse
    ret = Robx.Move(0, 0, -10, 2000)
    if (ret):
        MessageBox(0, Robx.GetErrorInfo(ret), "User action required", MB_OK | MB_SYSTEMMODAL)
        return ret

    #	if (preparation == 1) :
    #		MessageBox(0,"Verify the position","User action required", MB_OK | MB_SYSTEMMODAL)

    #	if ( vacuum ):

    # Close the blowdown valve
    ret = Robx.Valve(0)
    if (ret):
        MessageBox(0, Robx.GetErrorInfo(ret), "User action required", MB_OK | MB_SYSTEMMODAL)
        return ret

    ret = Robx.SetSpeed(SLOW_SPEED)
    if (ret):
        MessageBox(0, Robx.GetErrorInfo(ret), "User action required", MB_OK | MB_SYSTEMMODAL)
        return ret

    ret = Robx.SetAccel(MAX_ACCEL)
    if (ret):
        MessageBox(0, Robx.GetErrorInfo(ret), "User action required", MB_OK | MB_SYSTEMMODAL)
        return ret

    # Start the vacuum pump
    ret = Robx.Pump(1)
    if (ret):
        MessageBox(0, Robx.GetErrorInfo(ret), "User action required", MB_OK | MB_SYSTEMMODAL)
        return ret

    # Close the blowdown valve
    if (RobID == 6):
        ret = Robx.Valve(1)
        if (ret):
            MessageBox(0, Robx.GetErrorInfo(ret), "User action required", MB_OK | MB_SYSTEMMODAL)
            return ret

    # Test the presence of vacuum

    VacuumStatus = 0
    NoMoreCard = 0
    while ((VacuumStatus == 0) and (ret == ERR_OK)):
        # Go down to find the card with 1 mm steps
        ret = Robx.Move(0, 0, -1, 5000)
        if (ret):
            MessageBox(0, Robx.GetErrorInfo(ret), "User action required", MB_OK | MB_SYSTEMMODAL)
            return ret

        # Test the presence of vacuum
        err = Robx.GetVacuumStatus()
        if err == 0:
            VacuumStatus = Robx.GetVacuumNum()
        #			print VacuumStatus

        i = i + 1
        if (i > NB_STEPS_MAX):
            NoMoreCard = 1
            ret = Robx.Pump(0)
            ret = Robx.Valve(0)
            break

    # Go back higher in low speed
    ret = Robx.GotoPosition(Xcard, Ycard, Zcard - 25, Wcard, Pcard, 10000)
    if (ret):
        MessageBox(0, Robx.GetErrorInfo(ret), "User action required", MB_OK | MB_SYSTEMMODAL)
        return ret

    ret = Robx.SetSpeed(DEFAULT_SPEED)
    if (ret):
        MessageBox(0, Robx.GetErrorInfo(ret), "User action required", MB_OK | MB_SYSTEMMODAL)
        return ret

    ret = Robx.SetAccel(DEFAULT_ACCEL)
    if (ret):
        MessageBox(0, Robx.GetErrorInfo(ret), "User action required", MB_OK | MB_SYSTEMMODAL)
        return ret

    # Return to upper position in high speed
    ret = Robx.GotoPosition(Xcard, Ycard, Zcard + 10, Wcard, Pcard, 2000)
    if (ret):
        MessageBox(0, Robx.GetErrorInfo(ret), "User action required", MB_OK | MB_SYSTEMMODAL)
        return ret

    # Goto intermediate position
    ret = Robx.GotoPosition(XuserIn, Ycard, Zuser, Wcard, Pcard, 5000)
    if (ret):
        MessageBox(0, Robx.GetErrorInfo(ret), "User action required", MB_OK | MB_SYSTEMMODAL)
        return ret

    ret = Robx.GotoUserPosition(5000)
    if (ret):
        MessageBox(0, Robx.GetErrorInfo(ret), "User action required", MB_OK | MB_SYSTEMMODAL)
        return ret


def S_DropCard(Xcard, Ycard, Zcard, Wcard, Pcard):
    global preparation
    global XcardOut
    VacuumTest = []

    ret = Robx.GotoUserPosition(2000)
    if (ret):
        MessageBox(0, Robx.GetErrorInfo(ret), "User action required", MB_OK | MB_SYSTEMMODAL)
        return ret

    # Goto intermediate position
    ret = Robx.GotoPosition(XuserOut, Ycard, Zuser, Wcard, Pcard, 5000)
    if (ret):
        MessageBox(0, Robx.GetErrorInfo(ret), "User action required", MB_OK | MB_SYSTEMMODAL)
        return ret

    # Move over the storehouse
    ret = Robx.GotoPosition(Xcard, Ycard, Zcard, Wcard, Pcard, 5000)
    if (ret):
        MessageBox(0, Robx.GetErrorInfo(ret), "User action required", MB_OK | MB_SYSTEMMODAL)
        return ret

    # Move to the top of the storehouse
    ret = Robx.Move(0, 0, -10, 5000)
    if (ret):
        MessageBox(0, Robx.GetErrorInfo(ret), "User action required", MB_OK | MB_SYSTEMMODAL)
        return ret

    #	if (preparation == 1) :
    #		MessageBox(0,"Verify the position","User action required", MB_OK | MB_SYSTEMMODAL)
    #		preparation = 0

    #	if ( vacuum ):
    # Stop the vacuum pump
    ret = Robx.Pump(0)
    if (ret):
        MessageBox(0, Robx.GetErrorInfo(ret), "User action required", MB_OK | MB_SYSTEMMODAL)
        return ret

    # Open the blowdown valve
    if (RobID == 6):
        ret = Robx.Valve(0)
    else:
        ret = Robx.Valve(1)

    if (ret):
        MessageBox(0, Robx.GetErrorInfo(ret), "User action required", MB_OK | MB_SYSTEMMODAL)
        return ret

    # Test the absence of vacuum
    VacuumStatus = 0
    while ((VacuumStatus == 1) and (ret == ERR_OK)):

        err = Robx.GetVacuumStatus()
        if err == 0:
            VacuumStatus = Robx.GetVacuumNum()
    #			print VacuumStatus

    Robx.Wait(200)

    # Close the blowdown valve
    ret = Robx.Valve(0)
    if (ret):
        MessageBox(0, Robx.GetErrorInfo(ret), "User action required", MB_OK | MB_SYSTEMMODAL)
        return ret

    # Move over the storehouse
    ret = Robx.Move(0, 0, +10, 5000)
    if (ret):
        MessageBox(0, Robx.GetErrorInfo(ret), "User action required", MB_OK | MB_SYSTEMMODAL)
        return ret

    # Goto intermediate position
    ret = Robx.GotoPosition(XuserOut, Ycard, Zuser, Wcard, Pcard, 5000)
    if (ret):
        MessageBox(0, Robx.GetErrorInfo(ret), "User action required", MB_OK | MB_SYSTEMMODAL)
        return ret

    ret = Robx.GotoUserPosition(5000)
    if (ret):
        MessageBox(0, Robx.GetErrorInfo(ret), "User action required", MB_OK | MB_SYSTEMMODAL)
        return ret
