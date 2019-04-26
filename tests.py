from datasources import tests

from shapely.geometry import Polygon, MultiPolygon

from USGS3DEP import USGS3DEP

class USGS3DEPTestCases(tests.BaseTestCases):

    def _setUp(self):

        self.spatial_mode = 'extent'
        self.datasource = USGS3DEP
        self.spatial = {
                    "type": "Polygon",
                    "coordinates": [
                      [
                        [
                          -120.673828125,
                          32.509761735919426
                        ],
                        [
                          -115.1806640625,
                          32.509761735919426
                        ],
                        [
                          -115.1806640625,
                          36.35052700542763
                        ],
                        [
                          -120.673828125,
                          36.35052700542763
                        ],
                        [
                          -120.673828125,
                          32.509761735919426
                        ]
                      ]
                    ]
                    }
        self.temporal = ("2007-01-01", "2007-12-31")
        self.properties = {'pc:encoding': {'eq': 'laszip'}}
        self.limit = 10