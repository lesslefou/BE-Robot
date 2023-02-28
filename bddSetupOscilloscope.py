"""
 * @file        bddSetupOscilloscope.py
 * @brief       Contains differents possible setup for the oscilloscope to set up
 * @author      Lisa Duterte
 * @version     0.1
 * @date        2023
"""

"""
 * @brief Acquisition 1 Values
"""
def acquisition1():
    #Set axes parameters
    ver_scale =  {
        'Channel_1' : 1,
        'Channel_2' : 0.1,
        'Channel_3' : 0.2
    }

    ver_offset =  {
        'Channel_1' : 0.065,
        'Channel_2' : 0.018,
        'Channel_3' : 0.02
    }

    # set analog channels parameters (label, ver_scale, ver_offset, bandwidth, coupling)
    analog_channels = {
        1: ('Channel_1',  ver_scale['Channel_1'],   ver_offset['Channel_1'],  '20MHz', 'DC1M'),
        2: ('Channel_2',  ver_scale['Channel_2'],   ver_offset['Channel_2'],  '20MHz', 'DC1M'),
        3: ('Channel_3',  ver_scale['Channel_3'],   ver_offset['Channel_3'],  '20MHz', 'DC1M')
    }

    # set measurement channels 
    measurement_channels = { 
        1:  ('C1', 'RMS'),
        2:  ('C2', 'RMS'),
        3:  ('C3', 'RMS'),
        4:  ('C1', 'pkpk'),
        5:  ('C2', 'pkpk'),
        6:  ('C3', 'pkpk')
    }
    
    return (ver_offset,analog_channels,measurement_channels)