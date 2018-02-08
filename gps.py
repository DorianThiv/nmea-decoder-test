#!/usr/bin/env python3

""" GPS Frame Decoder

This module be able to decode NMEA (National Marine & Electronics Association) frame.
GPS is simple data transmission protocole. It provide details about electronic gear and devices.
Using NMEA-0183 standard.
This module is cannot be use to decode private frame

Example:
    Text...

        BaseGPS.getInstance(frame)

Text...

Attributes:
    module_level_variable1 (int): Module level variables may be documented in
        either the ``Attributes`` section of the module docstring, or in an
        inline docstring immediately following the variable.

        Either form is acceptable, but the two should not be mixed. Choose
        one convention to document module level variables and be consistent
        with it.

Todo:
    * Define GPS documentation
    * GPS Variable and decoder

.. Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""

import re

class GPSFormatError(Exception):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return "[GPSFormatError] : {}".format(self.message)

class GPSTypeError(Exception):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return "[GPSTypeError] : {}".format(self.message)

class BaseGPS:

    TYPE = ""

    ENCODING = "ascii"
    BAUD_RATE = 4800
    SIZE = 82
    START = "$"
    END = "*"
    SEP = ","
    CR = "CR"
    LF = "LF"

    IDX_REC_ID_S = 0
    IDX_REC_ID_E = 2

    IDX_FRAME_TYPE_S = 2
    IDX_FRAME_TYPE_E = 5

    RECEIVERS = {
        "GP": "Global Positioning System",
        "LC": "Loran-C receiver", 
        "OM": "Omega Navigation receiver", 
        "II": "Integrated Instrumentation"
        }
    
    FRAME_TYPE = {
        "GGA": "Permanent GPS and Date",
        "GLL": "Geographic Position Longitude-Latitude", 
        "GSA": "DOP and actif satellites", 
        "GSV": "Visible staellites",
        "VTG": "Direction and speed (Knots and Km/h)",
        "RMC": "Minimal and specifics data",
        }

    def __init__(self, frame):
        if frame[0] != '$': # and len(frame) != BaseGPS.SIZE:
            raise GPSFormatError("Lenght error : {}".format(len(frame)))
        self.data = self._split(frame)
        self.receiver = self.data[0][BaseGPS.IDX_REC_ID_S:BaseGPS.IDX_REC_ID_E]
        self.type = self.data[0][BaseGPS.IDX_FRAME_TYPE_S:BaseGPS.IDX_FRAME_TYPE_E]

    def _split(self, frame):
        if '*' in frame:
            frame = frame.rpartition('*')[0]
        frame = re.sub(r'[*$]', '', frame)
        data = frame.split(BaseGPS.SEP) 
        return data

    def __str__(self):
        return "receiver : {}, type : {}".format(self.receiver, self.type)

class GPSGGA(BaseGPS):

    """ GPS GGA format:

        * Time (123519)
        * Latitude (4807.038,N)
        * Longitude (01131.324,E)
        * Fix qualification (1) : 0 = none valide, 1 = Fix GPS, 2 = Fix DGPS
        * Satellites in poursuit (08)
        * Atitude in meters base on MSL (=mean see level) (545.4,M)
        * Highness correction géoïde in meters / ellipsoïde (46.9,M)
        * Second of last update (void) 
        * Id DGPS station(void)
        * CR & LF

        Exemple : $GPGGA,123519,4807.038,N,01131.324,E,1,08,545.4,M,46.9,M,,*42
    """
    
    TYPE = "GGA"

    IDX_TIME = 1
    IDX_LAT = (2, 4)
    IDX_LONG = (4, 6)
    IDX_QUAL = 6
    IDX_SAT = 7
    IDX_ALT = (8, 10)

    def __init__(self, frame):
        super().__init__(frame)
        if self.type not in list(BaseGPS.FRAME_TYPE.keys()):
            if self.type != GPSGGA.TYPE:
                raise GPSTypeError("not {} type".format(GPSGGA.TYPE))
            raise GPSFormatError("{} type is not support".format(self.type))
        self.time = self.data[GPSGGA.IDX_TIME]
        self.lattitude = self.data[GPSGGA.IDX_LAT[0]:GPSGGA.IDX_LAT[1]]
        self.longitude = self.data[GPSGGA.IDX_LONG[0]:GPSGGA.IDX_LONG[1]]
        self.quality = self.data[GPSGGA.IDX_QUAL]
        self.sattelites = self.data[GPSGGA.IDX_SAT]
        self.altitude = self.data[GPSGGA.IDX_ALT[0]:GPSGGA.IDX_ALT[1]]
        self.checksum = frame.rpartition('*')[2]

    def __str__(self):
        return "* Receiver: {}\n* Type: {}\n* Time: {}\n* Lattitude: {}\n* Longitude: {}\n* Quality: {}\n* Sattelites: {}\n* Altitude: {}\n* Checksum: {}\n".format(
        self.receiver,
        self.type,
        self.time,
        self.lattitude,
        self.longitude,
        self.quality,
        self.sattelites,
        self.altitude,
        self.checksum
    )
        

class GPSGLL(BaseGPS):
    
    """ GPS GLL format:

        * Latitude (4807.038,N)
        * Longitude (01131.324,E)
        * Time (123519)
        * Valid data (A)
        * CR & LF

        Exemple : $GPGLL,4807.038,N,01131.324,E,123519,A
    """

    TYPE = "GLL"

    IDX_LAT = (1, 3)
    IDX_LONG = (3, 5)
    IDX_TIME = 5
    IDX_DATA = 6
    
    def __init__(self, frame):
        super().__init__(frame)
        if self.type not in list(BaseGPS.FRAME_TYPE.keys()) and len(self.data) != 7:
            if self.type != GPSGLL.TYPE:
                raise GPSTypeError("not {} type".format(GPSGLL.TYPE))
            raise GPSFormatError("{} type is not support".format(self.type))
        self.lattitude = self.data[GPSGLL.IDX_LAT[0]:GPSGLL.IDX_LAT[1]]
        self.longitude = self.data[GPSGLL.IDX_LONG[0]:GPSGLL.IDX_LONG[1]]
        self.time = self.data[GPSGLL.IDX_TIME]
        self.data = self.data[GPSGLL.IDX_DATA]

    def __str__(self):
        return "* Receiver: {}\n* Type: {}\n* Lattitude: {}\n* Longitude: {}\n* Time: {}\n* Data: {}\n".format(
        self.receiver,
        self.type,
        self.lattitude,
        self.longitude,
        self.time,
        self.data
    )

class GPSGSA(BaseGPS):
    
    """ GPS GSA format:

        * Fix mode selection 2D or 3D (A = automatic, M = manuel)
        * Fix 3D (3 = 3D, 2 = 2D)
        * PRNs N°Ids satellites max 12 (04,05,09,,,,12 etc..)
        * PDOP dilution precision emmiting (2.5)
        * HDOP dilution Horizontal precision (1.3)
        * VDOP dilution Vertival precision (2.1)
        * Checksum (*39)
        * CR & LF

        Exemple : $GPGSA,A,3,04,05,,09,12,,,24,,,,,2.5,1.3,2.1*39
    """

    TYPE = "GSA"

    IDX_MODE = 1
    IDX_FIX = 2
    IDX_SAT_IDS = (3, 15)
    IDX_PDOP = 15
    IDX_HDOP = 16
    IDX_VDOP = 17

    def __init__(self, frame):
        super().__init__(frame)
        if self.type not in list(BaseGPS.FRAME_TYPE.keys()):
            if self.type != GPSGSA.TYPE:
                raise GPSTypeError("not {} type".format(GPSGSA.TYPE))
            raise GPSFormatError("{} type is not support".format(self.type))
        self.mode = self.data[GPSGSA.IDX_MODE]
        self.fix = self.data[GPSGSA.IDX_FIX]
        self.satellites = self.data[GPSGSA.IDX_SAT_IDS[0]:GPSGSA.IDX_SAT_IDS[1]]
        self.pdop = self.data[GPSGSA.IDX_PDOP]
        self.hdop = self.data[GPSGSA.IDX_HDOP]
        self.vdop = self.data[GPSGSA.IDX_VDOP]
        self.checksum = frame.rpartition('*')[2]

    def __str__(self):
        return "* Receiver: {}\n* Type: {}\n* Mode: {}\n* Fix: {}\n* Satellites: {}\n* PDOP: {}\n* HDOP: {}\n* VDOP: {}\n* Checksum: {}\n".format(
        self.receiver,
        self.type,
        self.mode,
        self.fix,
        self.satellites,
        self.pdop,
        self.hdop,
        self.vdop,
        self.checksum
    )

class GPSGSV(BaseGPS):
    
    """ GPS GSV format:

        It's possible to have max 3 frame in the same transsmition.

        * Frame number with complete data (2)
        * Frame number (1)
        * Visibles satellites (08)
        * Id number of the first satellite (01)
        * Elevation degrees (40)
        * Azimuth in degrees (083)
        * Signal force of th first satellite (46)
        * Checksum (*75)
        * CR & LF

        Exemple : $GPGSV,2,1,08,01,40,083,46*75
    """

    TYPE = "GSV"

    IDX_NBRS = 1
    IDX_CUR_NBR = 2
    IDX_SAT = 3
    IDX_FIRST_SAT_ID = 4
    IDX_ELEV = 5
    IDX_AZIM = 6
    IDX_SIGN = 7

    def __init__(self, frame):
        super().__init__(frame)
        if self.type not in list(BaseGPS.FRAME_TYPE.keys()):
            if self.type != GPSGSV.TYPE:
                raise GPSTypeError("not {} type".format(GPSGSV.TYPE))
            raise GPSFormatError("{} type is not support".format(self.type))
        self.total = self.data[GPSGSV.IDX_NBRS]
        self.current = self.data[GPSGSV.IDX_CUR_NBR]
        self.satellites = self.data[GPSGSV.IDX_SAT]
        self.first = self.data[GPSGSV.IDX_FIRST_SAT_ID]
        self.elevation = self.data[GPSGSV.IDX_ELEV]
        self.azimuth = self.data[GPSGSV.IDX_AZIM]
        self.checksum = frame.rpartition('*')[2]

    def __str__(self):
        return "* Receiver: {}\n* Type: {}\n* Total Frames: {}\n* Current Frame: {}\n* Satellites: {}\n* First Satellite ID: {}\n* Elevation: {}°\n* Azimuth: {}°\n* Checksum: {}\n".format(
        self.receiver,
        self.type,
        self.total,
        self.current,
        self.satellites,
        self.first,
        self.elevation,
        self.azimuth,
        self.checksum
    )

class GPSVTG(BaseGPS):
    
    """ GPS VTG format:

        * Track in degrees T = (True track made good) (054.7,T)
        * Track magnetic (034.4,M)
        * Speed move against floor in knots (005.5,N)
        * Speed move against floor in Km/h (010.3,K)
        * CR & LF

        Exemple : $GPVTG,054.7,T,034.4,M,005.5,N,010.3,K
    """

    TYPE = "VTG"

    IDX_TRACK_DEG = (1,3)
    IDX_TRACK_MAGN = (3,5)
    IDX_SPEED_KNOTS = (5,7)
    IDX_SPEED_KMH = (7,9)

    def __init__(self, frame):
        super().__init__(frame)
        if self.type not in list(BaseGPS.FRAME_TYPE.keys()):
            if self.type != GPSGGA.TYPE:
                raise GPSTypeError("not {} type".format(GPSGGA.TYPE))
            raise GPSFormatError("{} type is not support".format(self.type))
        self.dtrack = self.data[GPSVTG.IDX_TRACK_DEG[0]:GPSVTG.IDX_TRACK_DEG[1]]
        self.mtrack = self.data[GPSVTG.IDX_TRACK_MAGN[0]:GPSVTG.IDX_TRACK_MAGN[1]]
        self.nspeed = self.data[GPSVTG.IDX_SPEED_KNOTS[0]:GPSVTG.IDX_SPEED_KNOTS[1]]
        self.kspeed = self.data[GPSVTG.IDX_SPEED_KMH[0]:GPSVTG.IDX_SPEED_KMH[1]]
    
    def __str__(self):
        return "* Receiver: {}\n* Type: {}\n* Track Degrees: {}\n* Track Magnetic: {}\n* Speed Knots: {}\n* Speed Km/h: {}\n".format(
        self.receiver,
        self.type,
        self.dtrack,
        self.mtrack,
        self.nspeed,
        self.kspeed,
    )

class GPSRMC(BaseGPS):

    """ GPS RMC format:

        * Fix hours UTC (225446)
        * Software Alert (A = OK, V = Warning)
        * Latitude (4916.45,N)
        * Longitude (12311.12,W)
        * Speed move against floor in knots (000.5)
        * Track (054.7)
        * Fix date (191194)
        * Magnetic declin degrees (020.3,E) 
        * Checksum (*68) 
        * CR & LF

        Exemple : $GPRMC,225446,A,4916.45,N,12311.12,W,000.5,054.7,191194,020.3,E*68
    """
    
    TYPE = "RMC"

    IDX_HOUR = 1
    IDX_ALERT = 2
    IDX_LAT = (3, 5)
    IDX_LONG = (5, 7)
    IDX_SPEED_KNOTS = 7
    IDX_TRACK = 8
    IDX_DATE = 9
    IDX_MAGN = (10, 12)

    def __init__(self, frame):
        super().__init__(frame)
        print(self.type)
        if self.type not in list(BaseGPS.FRAME_TYPE.keys()):
            if self.type != GPSRMC.TYPE:
                raise GPSTypeError("not {} type".format(GPSRMC.TYPE))
            raise GPSFormatError("{} type is not support".format(self.type))
        self.hours = self.data[GPSRMC.IDX_HOUR]
        self.alert = self.data[GPSRMC.IDX_ALERT]
        self.latitude = self.data[GPSRMC.IDX_LAT[0]:GPSRMC.IDX_LAT[1]]
        self.longitude = self.data[GPSRMC.IDX_LONG[0]:GPSRMC.IDX_LONG[1]]
        self.speed = self.data[GPSRMC.IDX_SPEED_KNOTS]
        self.track = self.data[GPSRMC.IDX_TRACK]
        self.date = self.data[GPSRMC.IDX_DATE]
        self.magnetic = self.data[GPSRMC.IDX_MAGN[0]:GPSRMC.IDX_MAGN[1]]
        self.checksum = frame.rpartition('*')[2]

    def __str__(self):
        return "* Receiver: {}\n* Type: {}\n* Hours: {}\n* Alert: {}\n* Latitude: {}\n* Longitude: {}\n* Speed: {}\n* Track: {}\n* Date: {}\n* Magnetic: {}\n* Checksum: {}\n".format(
        self.receiver,
        self.type,
        self.hours,
        self.alert,
        self.latitude,
        self.longitude,
        self.speed,
        self.track,
        self.date,
        self.magnetic,
        self.checksum
    )
