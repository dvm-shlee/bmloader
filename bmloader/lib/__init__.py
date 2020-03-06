from pandas import DataFrame
import struct
import numpy as np


# Global variables
HEADER_COLUMNS = ['Field', 'Type', 'Bytes']
TIME_UNIT = 's'
PACKETID_SIZE = 8
PACKETID_DTYPE = '8s'

# NSx File Format
# Section 1 - Basic Header
# NEURALCD
NSX_BASIC = \
    DataFrame([['File_Type_ID',                      '8s',   8   ],
               ['File_Spec',                         '2B',   2   ],
               ['Bytes_in_Headers',                  'I',    4   ],
               ['Label',                             '16s',  16  ],
               ['Comment',                           '256s', 256 ],
               ['Period',                            'I',    4   ],
               ['Time_Resolution_of_Time_Stamps',    'I',    4   ],
               ['Time_Origin',                       '8H',   16  ],
               ['Channel_Count',                     'I',    4   ]],
              columns = HEADER_COLUMNS)

# Section 2 - Extended Header
NSX_EXTENDED = \
    DataFrame([['Type',                              '2s',   2   ],
               ['Electrode_ID',                      'H',    2   ],
               ['Electrode_Label',                   '16s',  16  ],
               ['Physical_Connector',                'B',    1   ],
               ['Connector_Pin',                     'B',    1   ],
               ['Min_Digital_Value',                 'h',    2   ],
               ['Max_Digital_Value',                 'h',    2   ],
               ['Min_Analog_Value',                  'h',    2   ],
               ['Max_Analog_Value',                  'h',    2   ],
               ['Units',                             '16s',  16  ],
               ['High_Freq_Corner',                  'I',    4   ],
               ['High_Freq_Order',                   'I',    4   ],
               ['High_Filter_Type',                  'H',    2   ],
               ['Low_Freq_Corner',                   'I',    4   ],
               ['Low_Freq_Order',                    'I',    4   ],
               ['Low_Filter_Type',                   'H',    2   ]],
              columns = HEADER_COLUMNS)

# Section 3 - Data Packets
NSX_DATA = \
    DataFrame([['Header',                            'B',    1   ],
               ['Timestamp',                         'I',    4   ],
               ['Number_of_Data_Points',             'I',    4   ],
               ['Data_Point',                        'h',    2   ]],
              columns = HEADER_COLUMNS)

# NEV File Format
# Section 1 - Basic Header
NEURALEV = \
    DataFrame([['File_Type_ID',                      '8s',   8   ],
               ['File_Spec',                         '2B',   2   ],
               ['Add_Flags',                         'H',    2   ],
               ['Bytes_in_Headers',                  'I',    4   ],
               ['Bytes_in_DataPackets',              'I',    4   ],
               ['TimeStamp_Resolution',              'I',    4   ],
               ['Sample_Time_Resolution',            'I',    4   ],
               ['Time_Origin',                       '8H',   16  ],
               ['Creating_Application',              '32s',  32  ],
               ['Comment',                           '256s', 256 ],
               ['Num_Extended_Headers',              'I',    4   ]],
              columns = HEADER_COLUMNS)

# Section 2 - Extended Header
ARRAYNME = \
    DataFrame([['Array_Name',                        '24s',  24  ]],
              columns = HEADER_COLUMNS)

ECOMMENT = \
    DataFrame([['Extra_Comment',                     '24s',  24  ]],
              columns = HEADER_COLUMNS)

CCOMMENT = \
    DataFrame([['Cont_Comment',                      '24s',  24  ]],
              columns = HEADER_COLUMNS)

MAPFILE = \
    DataFrame([['Map_File',                          '24s',  14  ]],
              columns = HEADER_COLUMNS)

NEUEVWAV = \
    DataFrame([['Electrode_ID',                      'H',    2   ],
               ['Physical_Connector',                'B',    1   ],
               ['Connector_Pin',                     'B',    1   ],
               ['Digitization_Factor',               'H',    2   ],
               ['Energy_Threshold',                  'H',    2   ],
               ['High_Threshold',                    'h',    2   ],
               ['Low_Threshold',                     'h',    2   ],
               ['Num_Sorted_Units',                  'B',    1   ],
               ['Bytes_Per_Waveform',                'B',    1   ],
               ['Spike_Width_Samples',               'H',    2   ],
               ['Empty_Bytes',                       '8s',   8   ]],
               columns = HEADER_COLUMNS)

NEUEVLBL = \
    DataFrame([['Electrode_ID',                      'H',    2   ],
               ['Label',                             '16s',  16  ],
               ['Empty_Bytes',                       '6s',   6   ]],
               columns = HEADER_COLUMNS)

NEUEVFLT = \
    DataFrame([['Electrode_ID',                      'H',    2   ],
               ['High_Freq_Corner',                  'I',    4   ],
               ['High_Freq_Order',                   'I',    4   ],
               ['High_Freq_Type',                    'H',    2   ],
               ['Low_Freq_Corner',                   'I',    4   ],
               ['Low_Freq_Order',                    'I',    4   ],
               ['Low_Freq_Type',                     'H',    2   ],
               ['Empty_Bytes',                       '2s',   2   ]],
               columns = HEADER_COLUMNS)

DIGLABEL = \
    DataFrame([['Label',                             '16s',  16  ],
               ['Mode',                              '?',    1   ],
               ['Empty_Bytes',                       '7s',   7   ]],
               columns = HEADER_COLUMNS)

NSASEXEV = \
    DataFrame([['Frequency',                         'H',    2   ],
               ['DigitalInputConfig',                'B',    1   ],
               ['AnalogCh1Config',                   'B',    1   ],
               ['AnalogCh1DetectVal',                'h',    2   ],
               ['AnalogCh2Config',                   'B',    1   ],
               ['AnalogCh2DetectVal',                'h',    2   ],
               ['AnalogCh3Config',                   'B',    1   ],
               ['AnalogCh3DetectVal',                'h',    2   ],
               ['AnalogCh4Config',                   'B',    1   ],
               ['AnalogCh4DetectVal',                'h',    2   ],
               ['AnalogCh5Config',                   'B',    1   ],
               ['AnalogCh5DetectVal',                'h',    2   ],
               ['EmptyBytes',                        '8s',   8   ]],
               columns = HEADER_COLUMNS)

VIDEOSYN = \
    DataFrame([['VideoSourceID',                     'H',    2   ],
               ['VideoSource',                       '16s',  16  ],
               ['FrameRate',                         'f',    4   ],
               ['EmptyBytes',                        '2s',   2   ]],
               columns = HEADER_COLUMNS)

TRACKOBJ = \
    DataFrame([['TrackableType',                     'H',    2   ],
               ['TrackableID',                       'H',    2   ],
               ['PointCount',                        'H',    2   ],
               ['VideoSource',                       '16s',  16  ],
               ['EmptyBytes',                        '2s',   2   ]],
               columns = HEADER_COLUMNS)


# Helper functions
def remove_code(data, code='\x00'):
    return data[0].decode('latin-1').split(code, 1)[0]


def convert_winsystime_struct(date):
    wmonth = {1:'Jan',  2:'Feb',  3:'Mar',  4:'Apr',  5:'May',  6:'Jun',
              7:'Jul',  8:'Aug',  9:'Sep', 10:'Oct', 11:'Nov', 12:'Dec'}
    wdow = {1:'Mon', 2:'Tue', 3:'Wed', 4:'Thr', 5:'Fri', 6:'Sat', 7:'Sun'}
    return "{}.{}.{}({}), {}:{}:{}.{}".format(wmonth[date[1]],
                                              date[3],
                                              date[0],
                                              wdow[date[2]],
                                              *date[4:])


def decoding(file_obj, type, num_bytes):
    output = struct.unpack(type, file_obj.read(num_bytes))
    if len(output) == 1:
        if 's' in type:
            output = remove_code(output)
        else:
            output = output[0]
    return output


def parse_digital_input(output, data_packet):
    packet_id = 'Digital_Events'
    if packet_id not in output.keys():
        output[packet_id] = dict(Timestamp=[],
                                 Packet_Insertion_Reason=[],
                                 Reserved=[],
                                 Digital_Input=[])
    output[packet_id]['Timestamp'].append(struct.unpack('<I', data_packet[:4])[0])
    output[packet_id]['Packet_Insertion_Reason'].append(struct.unpack('B', data_packet[6:7])[0])
    output[packet_id]['Reserved'].append(struct.unpack('B', data_packet[7:8])[0])
    output[packet_id]['Digital_Input'].append(struct.unpack('<H', data_packet[8:10])[0])
    return output


def parse_spike_event(output, packet_id, data_packet, ext_header):
    if packet_id not in output.keys():
        output[packet_id] = dict(Timestamp=[],
                                 Unit_Classification=[],
                                 Reserved=[],
                                 Waveform=[])

    output[packet_id]['Timestamp'].append(struct.unpack('<I', data_packet[:4])[0])
    output[packet_id]['Unit_Classification'].append(struct.unpack('B', data_packet[6:7])[0])
    output[packet_id]['Reserved'].append(struct.unpack('B', data_packet[7:8])[0])

    bytes_size = ext_header[packet_id]['Bytes_Per_Waveform']
    digit_factor = ext_header[packet_id]['Digitization_Factor']
    spike_width = ext_header[packet_id]['Spike_Width_Samples']

    if bytes_size <= 1:
        data_type = np.int8
    elif bytes_size == 2:
        data_type = np.int16
    else:
        raise Exception

    output[packet_id]['Waveform'].append(np.frombuffer(data_packet[8:],
                                                       dtype=data_type,
                                                       count=spike_width) * digit_factor)
    return output


def parse_comment_event(output, data_packet):
    packet_id = 'Comment_Events'
    if packet_id not in output.keys():
        output[packet_id] = dict(Timestamp=[],
                                 Char_Set=[],
                                 Flag=[],
                                 Data=[],
                                 Comment=[])
    output[packet_id]['Timestamp'].append(struct.unpack('<I', data_packet[:4])[0])
    output[packet_id]['Char_Set'].append(struct.unpack('B', data_packet[6:7])[0])
    output[packet_id]['Flag'].append(struct.unpack('B', data_packet[7:8])[0])
    output[packet_id]['Data'].append(struct.unpack('<I', data_packet[8:12])[0])
    output[packet_id]['Comment'].append(bytes.decode(data_packet[12:], 'latin-1').split('\x00', 1)[0])
    return output