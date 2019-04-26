import os
import json
import uuid

import boto3


from datasources.stac.query import STACQuery
from datasources.sources.base import Datasource

client = boto3.client('s3')
bucket = 'usgs-lidar-public'

class USGS3DEP(Datasource):

    stac_compliant = False
    tags = ['Elevation', 'Raster']

    def __init__(self, manifest):
        super().__init__(manifest)

    def search(self, spatial, temporal=None, properties=None, limit=10, **kwargs):
        from db import Database

        names = []
        stac_query = STACQuery(spatial, temporal, properties)
        # projects = stac_query.check_spatial(self.__class__.__name__)[:limit]

        with Database.load(read_only=True, deployed=True) as db:
            projects = db.spatial_query({"type": "Feature", "geometry": stac_query.spatial})

        searches = 0
        for item in projects:
            if item['name'] not in names:
                if temporal and item['year']:
                    if stac_query.temporal[0].year != item['year'] or stac_query.temporal[1].year != item['year']:
                        continue

                if properties:
                    item.update({'properties': stac_query})

                if searches < limit:
                    self.manifest.searches.append([self, item])
                    searches+=1



        # searches = 0
        # for item in projects:
        #     if item['name'] not in names:
        #     # Temporal check by checking year of start/end date
        #         if temporal and item['year']:
        #             if stac_query.temporal[0].year == item['year'] or stac_query.temporal[1].year == item['year']:
        #                 if properties:
        #                     item.update({'properties': stac_query})
        #                 self.manifest.searches.append([self, item])
        #                 names.append(item['name'])
        #         else:
        #             self.manifest.searches.append([self, item])
        #             names.append(item['name'])

    def execute(self, query):
        # Download metadata from query item
        response = client.get_object(Bucket=bucket, Key=os.path.join(query['name'], 'ept.json'))
        metadata = json.loads(response['Body'].read().decode('utf-8'))

        xvals = [x[0] for x in query['geometry']['coordinates'][0]]
        yvals = [y[1] for y in query['geometry']['coordinates'][0]]


        stac_item = {
            'id': str(uuid.uuid4()),
            'type': 'Feature',
            'bbox': [min(xvals), min(yvals), max(xvals), max(yvals)],
            'geometry': query['geometry'],
            'properties': {
                'datetime': f"{query['year']}-01-01T00:00:00.00Z",
                'eo:epsg': metadata['srs']['horizontal'],
                'pc:count': metadata['points'],
                'pc:type': 'lidar',
                'pc:encoding': metadata['dataType'],
                'pc:schema': metadata['schema'],
                'legacy:span': metadata['span'],
                'legacy:version': metadata['version'],
            },
            'assets': {
                's3path': {
                    'href': f"s3://{bucket}/{query['name']}",
                    'title': 'EPT data'
                }
            },
        }

        if "properties" in list(query):
            if query['properties'].check_properties(stac_item['properties']):
                return [stac_item]
        else:
            return [stac_item]