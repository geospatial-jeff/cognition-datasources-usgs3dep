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

    def test_spatial_search(self):
        # Overwriting default spatial test cases because outputs are multipart polygons
        # Default spatial test case only handles singlepart polygons
        self.manifest.flush()
        self.manifest['USGS3DEP'].search(self.spatial)
        response = self.manifest.execute()
        self.assertEqual(list(response), ['USGS3DEP'])

        # Confirming that each output feature intersects the input
        for feat in response['USGS3DEP']['features']:
            mp = MultiPolygon([Polygon(x[0]) for x in feat['geometry']['coordinates']])
            self.assertTrue(mp.intersects(self.spatial_geom))