#!/usr/bin/env python3

""" GPS Frame Decoder

This module be able to decode NMEA (National Marine & Electronics Association) frame.
GPS is simple data transmission protocole. It provide details about electronic gear and devices.
Using NMEA-0183 standard.
This module cannot be use to decode private frame

Example:
    run.py provide getInstance method to get an instance of the right 
    gps frame.

        Use: GPS.getInstance(frame)

Return an instance inherited from BaseGPS

classes:
    * GPS

Attributes:
    * getInstance (str)

Exception:
    * GPSFormatError(Exception)
        args: str => message

    * GPSTypeError(Exception)
        args: str => message

This a Theoric decoder !!! It will be test in real situation 

"""

import sys
import inspect

from frames import BaseGPS, GPSGGA, GPSGLL, GPSGSA, GPSGSV, GPSRMC, GPSVTG, GPSFormatError, GPSTypeError

class GPS:

    CLASSES = inspect.getmembers(sys.modules[__name__], inspect.isclass)

    @staticmethod
    def getInstance(frame):
        if not isinstance(frame, str):
            raise GPSFormatError("expected string parameter")
        base = BaseGPS(frame)
        for clss in GPS.CLASSES:
            if issubclass(clss[1], BaseGPS):
                if base.type == clss[1].TYPE:
                    return clss[1](frame)


if __name__ == "__main__":
    
    try:
        print(GPS.getInstance("$GPGGA,123519,4807.038,N,01131.324,E,1,08,545.4,M,46.9,M,,*42"))
        print(GPS.getInstance("$GPGLL,4807.038,N,01131.324,E,123519,1"))
        print(GPS.getInstance("$GPGSA,A,3,04,05,,09,12,,,24,,,,,2.5,1.3,2.1*39"))
        print(GPS.getInstance("$GPGSV,2,1,08,01,40,083,46*75"))
        print(GPS.getInstance("$GPVTG,054.7,T,034.4,M,005.5,N,010.3,K"))
        print(GPS.getInstance("$GPRMC,225446,A,4916.45,N,12311.12,W,000.5,054.7,191194,020.3,E*68"))
    except GPSFormatError as e:
        print(e)
    except GPSTypeError as e:
        print(e)
    except Exception as e:
        print(e)
