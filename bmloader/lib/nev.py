from . import *
from .utils import disk_cache
import os


class openNEV(BaseLoader):
    _cache_dir = os.path.join(os.curdir, '_bmcache_')

    def __init__(self, path=None):
        super(openNEV, self).__init__()
        self._path = path
        self._fileobj = None
        self._events_map = None
        self._events = dict()
        self._filesize = None

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
            self._parse_basic_header()
            self._parse_extended_header()
            self._parse_events_map()

    def load(self, path):
        import mmap
        with open(path, 'rb') as f:
            self._fileobj = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        self._filesize = len(self._fileobj)

    @property
    def avail_events(self):
        return sorted(list(self._events_map.keys()))

    def _parse_basic_header(self):
        if self._fileobj is None:
            raise Exception

        if self.BasicHeader is None:
            self.BasicHeader = dict()
            bh_size = NEURALEV.Bytes.sum()
            bh_data = self._fileobj[0:bh_size]
            loc = 0
            for i, row in NEURALEV.iterrows():
                c, loc = self.decoding(bh_data, row.Type, loc, row.Bytes)
                if row.Field is 'File_Spec':
                    c = "{}.{}".format(*c)
                elif row.Field is 'Time_Origin':
                    c = convert_winsystime_struct(c)
                self.BasicHeader[row.Field] = c
        else:
            pass

    def _parse_extended_header(self):
        if self._fileobj is None:
            raise Exception

        if self.BasicHeader is None:
            self._parse_basic_header()

        if self.ExtendedHeader is None:
            eh_start = NEURALEV.Bytes.sum()
            eh_end = self.BasicHeader['Bytes_in_Headers']

            eh_data = self._fileobj[eh_start:eh_end]

            self.ExtendedHeader = dict()
            self.OtherHeaders = dict()

            loc = 0
            for hdr in range(self.BasicHeader['Num_Extended_Headers']):
                packet_id = struct.unpack(PACKETID_DTYPE,
                                          eh_data[loc:loc + PACKETID_SIZE])[0].decode('utf-8')
                loc += PACKETID_SIZE

                section = globals()[packet_id]

                if packet_id in ['NEUEVWAV', 'NEUEVLBL', 'NEUEVFLT']:
                    header = dict()
                    for i, row in section.iterrows():
                        if row.Field != 'Empty_Bytes':
                            header[row.Field], loc = self.decoding(eh_data, row.Type, loc, row.Bytes)
                        else:
                            loc += row.Bytes

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
                            c = struct.unpack(row.Type, eh_data[loc:loc + row.Bytes])
                            if len(c) == 1:
                                if 's' in row.Type:
                                    c = remove_code(c)
                                else:
                                    c = c[0]
                            self.OtherHeaders[packet_id][row.Field] = c
                        loc += row.Bytes
        self.check_channel_map('Label')

    @disk_cache('_event_byte_loc', _cache_dir, method=True)
    def _parse_event_byte_loc(self, path):
        skip_size = self.BasicHeader['Bytes_in_Headers']
        dpacket_size = self.BasicHeader['Bytes_in_DataPackets']
        num_dpacket = int((self._filesize - skip_size) / dpacket_size)

        ev_b_loc = dict()
        for i in range(num_dpacket):
            loc = skip_size + i * dpacket_size
            packet_id = struct.unpack('<H', self._fileobj[loc + 4:loc + 6])[0]
            if packet_id == 0:
                # digital_input
                packet_id = 'Digital_Events'
            elif 1 <= packet_id <= 2048:
                # spike_event
                pass
            elif packet_id == 65535:
                # command_event
                packet_id = 'Comment_Events'

            # TODO: below cases are not yet integrated
            elif packet_id == 65534:  # Video sync event
                packet_id = 'Video_Sync_Event'
            elif packet_id == 65533:  # Tracking event
                packet_id = 'Tracking_Event'
            elif packet_id == 65532:  # Button trigger event
                packet_id = 'Button_Trigger_Event'
            elif packet_id == 65531:  # Log event
                packet_id = 'Log_Event'
            elif packet_id == 65530:  # Configuration event
                packet_id = 'Congiguration_Event'
            else:
                pass

            if packet_id not in ev_b_loc.keys():
                ev_b_loc[packet_id] = []
            ev_b_loc[packet_id].append(loc)
        return ev_b_loc

    def _parse_events_map(self):
        if self.ExtendedHeader is None:
            self._parse_extended_header()

        if self._events_map is None:
            self._events_map = self._parse_event_byte_loc(os.path.basename(self._path))

    @staticmethod
    def _parse_digital_input(output, data_packet):
        if not len(output.keys()):
            output = dict(Timestamp=[],
                          Packet_Insertion_Reason=[],
                          Reserved=[],
                          Digital_Input=[])
        output['Timestamp'].append(struct.unpack('<I', data_packet[:4])[0])
        output['Packet_Insertion_Reason'].append(struct.unpack('B', data_packet[6:7])[0])
        output['Reserved'].append(struct.unpack('B', data_packet[7:8])[0])
        output['Digital_Input'].append(struct.unpack('<H', data_packet[8:10])[0])
        return output

    @staticmethod
    def _parse_comment_event(output, data_packet):
        if not len(output.keys()):
            output = dict(Timestamp=[],
                          Char_Set=[],
                          Flag=[],
                          Data=[],
                          Comment=[])
        output['Timestamp'].append(struct.unpack('<I', data_packet[:4])[0])
        output['Char_Set'].append(struct.unpack('B', data_packet[6:7])[0])
        output['Flag'].append(struct.unpack('B', data_packet[7:8])[0])
        output['Data'].append(struct.unpack('<I', data_packet[8:12])[0])
        output['Comment'].append(bytes.decode(data_packet[12:], 'latin-1').split('\x00', 1)[0])
        return output

    def _parse_spike_event(self, output, data_packet):
        if not len(output.keys()):
            output = dict(Timestamp=[],
                          Unit_Classification=[],
                          Reserved=[],
                          Waveform=[])

        eid = struct.unpack('<H', data_packet[4:6])[0]
        output['Timestamp'].append(struct.unpack('<I', data_packet[:4])[0])
        # the classifier can be defined as string here
        output['Unit_Classification'].append(struct.unpack('B', data_packet[6:7])[0])
        output['Reserved'].append(struct.unpack('B', data_packet[7:8])[0])

        bytes_size = self.ExtendedHeader[eid]['Bytes_Per_Waveform']
        digit_factor = self.ExtendedHeader[eid]['Digitization_Factor']
        spike_width = self.ExtendedHeader[eid]['Spike_Width_Samples']

        if bytes_size <= 1:
            data_type = np.int8
        elif bytes_size == 2:
            data_type = np.int16
        else:
            raise Exception

        output['Waveform'].append(np.frombuffer(data_packet[8:],
                                                dtype=data_type,
                                                count=spike_width).astype(np.int32))
        return output

    @disk_cache('_event', _cache_dir, method=True)
    def _parse_events(self, packet_id, path):
        if packet_id not in self.avail_events:
            return None
        else:
            dpacket_size = self.BasicHeader['Bytes_in_DataPackets']
            output = dict()
            for loc in self._events_map[packet_id]:
                data_packet = self._fileobj[loc:loc + dpacket_size]
                if packet_id == 'Digital_Events':
                    output = self._parse_digital_input(output, data_packet)
                elif packet_id == 'Comment_Events':
                    output = self._parse_comment_event(output, data_packet)
                elif 1 <= packet_id <= 2048:
                    output = self._parse_spike_event(output, data_packet)
                else:
                    # Need integrate rest of event type
                    output = None
            return output

    def _set_events(self, packet_id):
        self._events[packet_id] = self._parse_events(packet_id, os.path.basename(self._path))

    def get_comment_events(self):
        # TODO: need more consistant output format
        if 'Comment_Events' not in self._events.keys():
            self._set_events('Comment_Events')
        return self._events['Comment_Events']

    def get_digital_events(self):
        # TODO: need more consistant output format
        if 'Digital_Events' not in self._events.keys():
            self._set_events('Digital_Events')
        return self._events['Digital_Events']

    def get_spike_unit_cls(self, ch_id):
        """ Spike Unit Classification
        Parameters:
            ch_id:
        Returns:
            unit_cls: Spike unit classification indices on given channel (unit: sec)
        """
        if ch_id not in self._events.keys():
            self._set_events(ch_id)
        return np.asarray(self._events[ch_id]['Unit_Classification'])

    def get_spike_timestamp(self, ch_id, idx=True):
        """
        Parameters:
            ch_id:
        Returns:
            tstamps: Event timestamps on given channel (unit: sec)
        """
        if ch_id not in self._events.keys():
            self._set_events(ch_id)
        fs = self.BasicHeader['TimeStamp_Resolution']
        if idx:
            return self._events[ch_id]['Timestamp']
        else:
            return np.asarray(self._events[ch_id]['Timestamp']) / fs

    def get_spike_waveforms(self, ch_id):
        """
        Parameters:
            ch_id:
        Returns:
            x: time axis (unit: msec)
            Y: Waveform (n_samples, n_features) (unit: nV)
        """
        if ch_id not in self._events.keys():
            self._set_events(ch_id)
        # TODO: x axis need to be returned
        time_resol = self.BasicHeader['Sample_Time_Resolution']
        n_sample = self.ExtendedHeader[ch_id]['Spike_Width_Samples']
        x = np.linspace(start=0, stop=n_sample / time_resol, num=n_sample) * 1000

        return x, np.asarray(self._events[ch_id]['Waveform'])

    def close(self):
        if self._fileobj is not None:
            self._fileobj.close()

    def __del__(self):
        self.close()


