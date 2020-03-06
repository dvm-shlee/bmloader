import pandas as pd
from . import *


class openNEV():
    def __init__(self, path=None, *args, **kargs):
        self._fileobj = None
        self._events = None

        # Headers
        self.BasicHeader = None
        self.ExtendedHeader = None
        self.OtherHeaders = None

        # Attributes
        self.ChannelMap = None
        self.NumChannels = None
        self.Unit_Waveform = 'nV'

        if path is not None:
            self.load(path)
            self.parse_basic_header()
            self.parse_extended_header()
            self.parse_events()

    def load(self, path):
        self._fileobj = open(path, 'rb')

    def parse_basic_header(self):
        if self._fileobj is None:
            raise Exception

        if self.BasicHeader is None:
            self._fileobj.seek(0, 0)
            self.BasicHeader = dict()
            f = self._fileobj
            for i, row in NEURALEV.iterrows():
                c = decoding(f, row.Type, row.Bytes)
                if row.Field is 'File_Spec':
                    c = "{}.{}".format(*c)
                elif row.Field is 'Time_Origin':
                    c = convert_winsystime_struct(c)
                self.BasicHeader[row.Field] = c
        else:
            pass

    def parse_extended_header(self):
        if self._fileobj is None:
            raise Exception

        if self.BasicHeader is None:
            self.parse_basic_header()

        if self.ExtendedHeader is None:
            loc = NEURALEV.Bytes.sum()
            f = self._fileobj
            self.ExtendedHeader = dict()
            self.OtherHeaders = dict()
            for hdr in range(self.BasicHeader['Num_Extended_Headers']):
                self._fileobj.seek(loc, 0)
                packet_id = struct.unpack(PACKETID_DTYPE,
                                          f.read(PACKETID_SIZE))[0].decode('utf-8')
                section = globals()[packet_id]
                loc += PACKETID_SIZE + section.Bytes.sum()
                if packet_id in ['NEUEVWAV', 'NEUEVLBL', 'NEUEVFLT']:
                    header = dict()
                    for i, row in section.iterrows():
                        if row.Field != 'Empty_Bytes':
                            header[row.Field] = decoding(f, row.Type, row.Bytes)

                    eid = header['Electrode_ID']
                    if eid not in self.ExtendedHeader.keys():
                        self.ExtendedHeader[eid] = dict()

                    for key, value in header.items():
                        if key not in self.ExtendedHeader[eid].keys():
                            self.ExtendedHeader[eid][key] = value
                else:
                    if packet_id not in self.OtherHeaders.keys():
                        self.OtherHeaders[packet_id] = dict()
                    for i, row in section.iterrows():
                        if row.Field != 'Empty_Bytes':
                            c = struct.unpack(row.Type, f.read(row.Bytes))
                            if len(c) == 1:
                                if 's' in row.Type:
                                    c = remove_code(c)
                                else:
                                    c = c[0]
                            self.OtherHeaders[packet_id][row.Field] = c
        self.check_channel_map()

    def parse_events(self):
        if self.ExtendedHeader is None:
            self.parse_extended_header()

        if self._events is None:
            self._fileobj.seek(self.BasicHeader['Bytes_in_Headers'])
            f = self._fileobj
            step = self.BasicHeader['Bytes_in_DataPackets']
            output = dict()

            while True:
                data_packet = f.read(step)
                if len(data_packet) < step:
                    break
                packet_id = struct.unpack('<H', data_packet[4:6])[0]
                if packet_id == 0:
                    output = parse_digital_input(output, data_packet)
                elif 1 <= packet_id <= 2048:
                    output = parse_spike_event(output, packet_id, data_packet, self.ExtendedHeader)
                elif packet_id == 65535:
                    output = parse_comment_event(output, data_packet)
                # TODO: below cases are not yet integrated
                elif packet_id == 65534:  # Video sync event
                    pass
                elif packet_id == 65533:  # Tracking event
                    pass
                elif packet_id == 65532:  # Button trigger event
                    pass
                elif packet_id == 65531:  # Log event
                    pass
                elif packet_id == 65530:  # Configuration event
                    pass
                else:
                    pass
            self._events = output

    def check_channel_map(self):
        if self.ExtendedHeader is None:
            raise Exception

        self.ChannelMap = pd.DataFrame(columns=['ID', 'Label'])
        for idx in self.ExtendedHeader.keys():
            label = self.ExtendedHeader[idx]['Label']
            ident = self.ExtendedHeader[idx]['Electrode_ID']
            row = dict(ID=ident, Label=label)
            self.ChannelMap = self.ChannelMap.append(row, ignore_index=True)
        self.NumChannels = len(self.ChannelMap)

    def get_event_timestamp(self, ch_id):
        fs = self.BasicHeader['TimeStamp_Resolution']
        return np.asarray(self._events[ch_id]['Timestamp'])/fs

    def close(self):
        if self._fileobj is not None:
            self._fileobj.close()

    def __del__(self):
        self.close()
