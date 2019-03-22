import os
import json
import uuid

import boto3


from datasources.stac.query import STACQuery
from datasources.stac.item import STACItem
from datasources.sources.base import Datasource

client = boto3.client('s3')
bucket = 'usgs-lidar-public'

class USGS3DEP(Datasource):

    stac_compliant = False
    tags = ['Elevation', 'Raster']

    # @staticmethod
    # def query_3dep_reference(bbox):
    #     idx = index.Rtree(rtree_location)
    #     return [x.object for x in idx.intersection(bbox, objects=True)]
    #
    # @staticmethod
    # def check_properties(asset, properties):
    #     for item in properties:
    #         equality = next(iter(properties[item]))
    #         comparison_operator = getattr(operator, equality)
    #         if not comparison_operator(asset[item], properties[item][equality]):
    #             return False
    #     return True

    def __init__(self, manifest):
        super().__init__(manifest)

    def search(self, spatial, temporal=None, properties=None, limit=10, **kwargs):
        names = []
        stac_query = STACQuery(spatial, temporal, properties)
        projects = stac_query.check_spatial(self.__class__.__name__)[:limit]
        for item in projects:
            if item['project_name'] not in names:
            # Temporal check by checking year of start/end date
                if temporal and item['year']:
                    if stac_query.temporal[0].year == item['year'] or stac_query.temporal[1].year == item['year']:
                        if properties:
                            item.update({'properties': stac_query})
                        self.manifest.searches.append([self, item])
                        names.append(item['project_name'])
                else:
                    self.manifest.searches.append([self, item])
                    names.append(item['project_name'])

    def execute(self, query):
        # Download metadata from query item
        response = client.get_object(Bucket=bucket, Key=os.path.join(query['project_name'], 'ept.json'))
        metadata = json.loads(response['Body'].read().decode('utf-8'))

        geometry = json.loads(query['geom'])
        xvals = [[x[0] for x in y] for y in geometry['coordinates'][0]]
        xflat = [item for sublist in xvals for item in sublist]
        yvals = [[y[0] for y in x] for x in geometry['coordinates'][0]]
        yflat = [item for sublist in yvals for item in sublist]


        stac_item = {
            'id': str(uuid.uuid4()),
            'type': 'Feature',
            'bbox': [min(xflat), min(yflat), max(xflat), max(yflat)],
            'geometry': geometry,
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
                    'href': f"s3://{bucket}/{query['project_name']}",
                    'title': 'EPT data'
                }
            },
        }


        # print(stac_item['bbox'])

        if "properties" in list(query):
            if query['properties'].check_properties(stac_item['properties']):
                return [stac_item]
        else:
            return [stac_item]