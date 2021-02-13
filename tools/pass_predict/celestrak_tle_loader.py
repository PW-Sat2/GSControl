import urllib2

class CelestrakTleLoader():
    def __init__(self):
        self._urlPattern = 'https://celestrak.com/NORAD/elements/gp.php?CATNR={}&FORMAT=tle'

    def loadTle(self, noradId):
        url = self._urlPattern.format(noradId)
        response = urllib2.urlopen(url)
        tle = response.read()
        tleLines = tle.strip().split('\n')
        tleLines = [line.strip() for line in tleLines]

        return tleLines