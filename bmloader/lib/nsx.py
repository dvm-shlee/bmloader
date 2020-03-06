import pandas as pd
from . import *


class openNSx():
    def __init__(self, path=None, *args, **kargs):
        self._fileobj = None

        # References
        self.NEURALCD = NSX_BASIC
        self.CC = NSX_EXTENDED
        self.Data = NSX_DATA

        # Headers
        self.BasicHeader = None
        self.ExtendedHeader = None

        # Attributes
        self.SamplingFreq = None
        self.TimeStamp = None
        self.NumDataPoints = None
        self.TotalDataPoints = None
        self.ChannelMap = None
        self.NumChannels = None

        if path != None:
            self.load(path)
            self.parse_basic_header()
            self.parse_extended_header()
            self.parse_data_header()

    def load(self, path):
        self._fileobj = open(path, 'rb')

    def parse_basic_header(self):
        if self._fileobj == None:
            raise Exception

        if self.BasicHeader == None:
            self._fileobj.seek(0, 0)
            self.BasicHeader = dict()
            f = self._fileobj
            for i, row in self.NEURALCD.iterrows():
                c = decoding(f, row.Type, row.Bytes)
                if row.Field == 'File_Spec':
                    c = "{}.{}".format(*c)
                elif row.Field == 'Time_Origin':
                    c = convert_winsystime_struct(c)
                self.BasicHeader[row.Field] = c
            self.SamplingFreq = self.BasicHeader['Time_Resolution_of_Time_Stamps'] / self.BasicHeader['Period']
        else:
            pass

    def parse_extended_header(self):
        if self._fileobj == None:
            raise Exception

        if self.BasicHeader == None:
            self.parse_basic_header()

        if self.ExtendedHeader == None:
            self._fileobj.seek(self.NEURALCD.Bytes.sum(), 0)
            f = self._fileobj
            self.ExtendedHeader = dict()
            for ch in range(self.BasicHeader['Channel_Count']):
                header = dict()
                for i, row in self.CC.iterrows():
                    header[row.Field] = decoding(f, row.Type, row.Bytes)

                eid = header['Electrode_ID']
                self.ExtendedHeader[eid] = header
        self.check_channel_map()

    def parse_data_header(self):
        if self.ExtendedHeader == None:
            self.parse_extended_header()

        self._fileobj.seek(self.BasicHeader['Bytes_in_Headers'])

        f = self._fileobj
        for i, row in self.Data.iterrows():
            if row.Field == 'Data_Point':
                pass
            else:
                c = struct.unpack(row.Type, f.read(int(row.Bytes)))[0]
                if row.Field == 'Header':
                    if c != 1:
                        print(c)
                        raise Exception
                if row.Field == 'Timestamp':
                    self.TimeStamp = c
                elif row.Field == 'Number_of_Data_Points':
                    self.NumDataPoints = c
        self.TotalDataPoints = self.TimeStamp + self.NumDataPoints

    def check_channel_map(self):
        if self.ExtendedHeader == None:
            raise Exception

        self.ChannelMap = pd.DataFrame(columns=['ID', 'Label'])
        for idx in self.ExtendedHeader.keys():
            label = self.ExtendedHeader[idx]['Electrode_Label']
            ident = self.ExtendedHeader[idx]['Electrode_ID']
            row = dict(ID=ident, Label=label)
            self.ChannelMap = self.ChannelMap.append(row, ignore_index=True)
        self.NumChannels = len(self.ChannelMap)

    def get_data_from_channel(self, ch_id, start=None, stop=None,
                              down_sampling=None):
        if ch_id not in self.ChannelMap['ID'].values:
            raise Exception

        dp_size = self.Data.Bytes[3]
        dp_type = self.Data.Type[3]

        loc = self.BasicHeader['Bytes_in_Headers'] + self.Data.Bytes[:3].sum()
        f = self._fileobj

        ch_index = self.ChannelMap.index[self.ChannelMap['ID'] == ch_id].tolist()[0]

        f.seek(loc + ch_index * dp_size, 0)  # set first location
        if start == None:
            start = 0
        else:
            if start >= self.NumDataPoints:
                raise Exception
            f.seek(start * self.NumChannels * dp_size, 1)

        if stop == None:
            stop = self.TotalDataPoints
        else:
            if stop > self.TotalDataPoints:
                raise Exception
        if down_sampling == None:
            down_sampling = 1
        else:
            if not isinstance(down_sampling, int):
                raise Exception

        new_data_points = int((stop - start - self.TimeStamp) / down_sampling)
        data = []

        n_zpad = int((self.TimeStamp - start) / down_sampling)
        if n_zpad < 0:
            n_zpad = 0
        if n_zpad != 0:
            data.extend([0] * n_zpad)

        for dp in range(new_data_points):
            data.append(struct.unpack(dp_type, f.read(dp_size))[0])
            f.seek((self.NumChannels * down_sampling * dp_size) - dp_size, 1)

        fs = float(self.SamplingFreq)

        xp = np.linspace(start / fs, stop / fs, new_data_points + n_zpad)
        yp = np.asarray(data)

        max_dv = self.ExtendedHeader[ch_id]['Max_Digital_Value']
        min_dv = self.ExtendedHeader[ch_id]['Min_Digital_Value']
        bias_dv = (max_dv + min_dv) / 2.0

        max_av = self.ExtendedHeader[ch_id]['Max_Analog_Value']
        min_av = self.ExtendedHeader[ch_id]['Min_Analog_Value']
        bias_av = (max_av + min_av) / 2.0

        centered_max_dv = max_dv - bias_dv
        centered_max_ac = max_av - bias_av

        yp = ((yp - bias_av) / (float(centered_max_dv) / float(centered_max_ac))) + bias_av
        return xp, yp

    def get_unit_from_channel(self, ch_id):
        x_units = TIME_UNIT
        y_units = self.ExtendedHeader[ch_id]['Units']
        return x_units, y_units

    def close(self):
        if self._fileobj != None:
            self._fileobj.close()

    def __del__(self):
        self.close()
