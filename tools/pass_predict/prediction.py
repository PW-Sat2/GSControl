import datetime

class Predicton:
    def __init__(self, start, end, maxElev, aosAzimuth):
        self.start = start
        self.end = end
        self.maxElev = maxElev
        self.aosAzimuth = aosAzimuth

    def _parseTimezonedelta(self, delta):
        sign = "+" if delta.days >= 0 else "-"
        seconds = delta.seconds
        if (delta.days < 0):
            seconds = abs(delta.days * 86400 + delta.seconds)

        hours, seconds = divmod(seconds, 3600)
        minutes, seconds = divmod(seconds, 60)
        diffString = '{}{:02d}:{:02d}'.format(sign, hours, minutes)
        return diffString

    def _makeDate(self, timestamp):
        utcDate = datetime.datetime.utcfromtimestamp(timestamp).replace(microsecond=0)
        localDate = datetime.datetime.fromtimestamp(timestamp).replace(microsecond=0) 
        diff = localDate - utcDate
        diffString = self._parseTimezonedelta(diff)

        return localDate.isoformat() + diffString

    def getIsoStartDateString(self):
        return self._makeDate(self.start)

    def getIsoEndDateString(self):
        return self._makeDate(self.end)
    
    def getIsoStartDate(self):
        return datetime.datetime.fromtimestamp(self.start).replace(microsecond=0)

    def getIsoEndDate(self):
        return datetime.datetime.fromtimestamp(self.stop).replace(microsecond=0)

    def __str__(self):
        return "Prediction: {}\t{}\t{}".format(self.getIsoStartDateString(), self.getIsoEndDateString(), self.maxElev)

    def __repr__(self):
        return self.__str__()