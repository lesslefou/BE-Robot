"""
 * @file        oscilloscopeAcquisition.py
 * @brief       Contains the functions specific to the oscilloscope's management
 * @author      Lisa Duterte
 * @version     0.1
 * @date        2023
"""

import win32com.client
import pyvisa
import time
from lecroy import *
from bddSetupOscilloscope import *
from bddScript import *
import datetime


"""
 * @brief Enable the connection to the oscilloscope
 * @param The Id of the Oscilloscope
 * @exception range_error If the oscilloscope is not connected 
"""
def oscilloscopeConnection(id_oscillo):
    global lecroy

    scope = win32com.client.Dispatch("LeCroy.ActiveDSOCtrl.1") #creates instances of the ActiveDSO Control
    scope.MakeConnection("USBTMC:" + id_oscillo)  #Connects to the oscilloscope

    rm = pyvisa.ResourceManager()
    print(rm.list_resources())
    lecroy = lecroy(pyvisa_instr=rm.open_resource(id_oscillo))
    
    return rm


"""
 * @brief Set the parameters of the oscilloscope depending on the desired acquisition 
"""
def setOscilloscopeParameters() :
    (ver_offset,analog_channels,measurement_channels) = acquisition1()
    lecroy.reset_scope()
    time.sleep(2)
    lecroy.set_date_and_time() # use system date and time to set the time on the oscilloscope

    #display channel waves and measurement setups
    lecroy.channel_setup(analog_ch_dict=analog_channels, numberOfAnalogChannels=3, numberOfMeasurementChannels=6)
    lecroy.measurement_setup(measurement_channels,numberOfAnalogChannels=3)

    lecroy.setGrid('Single') # set single|Dual|... grid mode 
    lecroy.setChannelOnGridNumber(channel="C1",grid="YT1")  #if Multiple mode YT1 | YT2 | ...
    lecroy.setChannelOnGridNumber(channel="C2",grid="YT1")
    lecroy.setChannelOnGridNumber(channel="C3",grid="YT1")

    hor_scale = 50*lecroy.unit_us  #50µS
    lecroy.horizontal_scale(scale=hor_scale)  #time/division
    lecroy.setHorizontal_delay(delay=-140*lecroy.unit_us)
  
    
  

idAcquisitionValue = (0,)
"""
 * @brief Get the configuration of the oscilloscope
"""
def getOscillocopeConfiguration():
    sampleRate = lecroy.getSampleRate()
    horizontal_scale = lecroy.get_horizontal_scale()
    C1VerticalScale = lecroy.getChannelVerticalScale("C1")
    C2VerticalScale = lecroy.getChannelVerticalScale("C2")
    C3VerticalScale = lecroy.getChannelVerticalScale("C3")
    
    global idAcquisitionValue
    #get the last idAcquisitionValue and idConfiguration
    idConfiguration = get_query('''SELECT idConfiguration FROM Configuration ORDER BY idConfiguration DESC LIMIT 1''')
    if (len(idConfiguration) == 0):
        idConfiguration = 0
    else:
        idConfiguration = idConfiguration[0][0]
        idConfiguration += 1
        
    
    idAcquisitionValue = get_query('''SELECT idAcquisitionValue FROM AcquisitionValue ORDER BY idAcquisitionValue DESC LIMIT 1''')
    if (len(idAcquisitionValue) == 0):
        idAcquisitionValue = 0
    else:
        idAcquisitionValue = idAcquisitionValue[0][0]
    
    print(sampleRate, horizontal_scale, C1VerticalScale, C2VerticalScale, C3VerticalScale)
    
    #envoie bdd 
    push_query(f"""INSERT INTO Configuration (idConfiguration, SH, SV1, SV2, SV3, Sample) values ({idConfiguration}, {horizontal_scale}, {C1VerticalScale}, {C2VerticalScale}, {C3VerticalScale}, {sampleRate})""")
    
    
    
"""
 * @brief Get six specifics variables mesured by the oscilloscope
"""
def getAcquisition(nomPoint):    
    #Get value of measurement channels
    RMS_C1 = "{:.4f}".format(lecroy.getValueOnChannel('P1', 'value')) if isinstance(lecroy.getValueOnChannel('P1', 'value'), (float, int)) else "{}".format(lecroy.getValueOnChannel('P1', 'value'))
    RMS_C2 = "{:.4f}".format(lecroy.getValueOnChannel('P2', 'value')) if isinstance(lecroy.getValueOnChannel('P2', 'value'), (float, int)) else "{}".format(lecroy.getValueOnChannel('P2', 'value'))
    RMS_C3 = "{:.4f}".format(lecroy.getValueOnChannel('P3', 'value')) if isinstance(lecroy.getValueOnChannel('P3', 'value'), (float, int)) else "{}".format(lecroy.getValueOnChannel('P3', 'value'))
    PKPK_C1 = "{:.4f}".format(lecroy.getValueOnChannel('P4', 'value')) if isinstance(lecroy.getValueOnChannel('P4', 'value'), (float, int)) else "{}".format(lecroy.getValueOnChannel('P4', 'value'))
    PKPK_C2 = "{:.4f}".format(lecroy.getValueOnChannel('P5', 'value')) if isinstance(lecroy.getValueOnChannel('P5', 'value'), (float, int)) else "{}".format(lecroy.getValueOnChannel('P5', 'value'))
    PKPK_C3 = "{:.4f}".format(lecroy.getValueOnChannel('P6', 'value')) if isinstance(lecroy.getValueOnChannel('P6', 'value'), (float, int)) else "{}".format(lecroy.getValueOnChannel('P6', 'value'))

    global idAcquisitionValue
    idAcquisitionValue += 1 
    
    print(nomPoint,RMS_C1, RMS_C2, RMS_C3, PKPK_C1, PKPK_C2, PKPK_C3)
    
    #Bdd Sending
    push_query(f"""INSERT INTO AcquisitionValue (idAcquisitionValue, RMSC1, RMSC2, RMSC3, PKPKC1, PKPKC2, PKPKC3, Name) values ({idAcquisitionValue}, {RMS_C1}, {RMS_C2}, {RMS_C3}, {PKPK_C1}, {PKPK_C2}, {PKPK_C3}, "{nomPoint}")""")


def sendMeshTypeToBdd(mesh):
    #get the last idAcquisition
    idAcquisition = get_query('''SELECT idAcquisition FROM Acquisition ORDER BY idAcquisition DESC LIMIT 1''')
    
    year =  datetime.datetime.now().year
    month =  datetime.datetime.now().month
    day =  datetime.datetime.now().day
    hour =  datetime.datetime.now().hour
    minute =  datetime.datetime.now().minute
    second =  datetime.datetime.now().second
        
    
    date = str(year) + '-' + str(month) + '-'  + str(day) + ' | ' + str(hour) + ':' + str(minute) + ':'  + str(second)
    print(date)
    
    
    if (len(idAcquisition) == 0):
        idAcquisition = 0
    else:
        idAcquisition = idAcquisition[0][0]
        idAcquisition += 1
        
    push_query(f"""INSERT INTO Acquisition (idAcquisition, Mesh, Time) values ({idAcquisition}, "{mesh}", "{date}")""")


