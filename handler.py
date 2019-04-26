from datasources import Manifest

def USGS3DEP(event, context):
    manifest = Manifest()
    manifest['USGS3DEP'].search(**event)
    response = manifest.execute()
    return response


