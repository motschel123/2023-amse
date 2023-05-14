import requests
from xml.etree import ElementTree as ET
import geopandas as gpd
import io


def get_capabilities(wfs_url) -> list:
    # Define the parameters for the GetCapabilities request
    params = {
        'service': 'WFS',
        'version': '2.0.0',
        'request': 'GetCapabilities'
    }

    # Send request to get the Capabilities document
    response = requests.get(wfs_url, params=params)

    # Check if the request was successful
    if response.status_code != 200:
        raise Exception("Request failed with status code: {response.status_code}")

    # Parse the XML response
    root = ET.fromstring(response.content)

    # Find all FeatureType elements
    # Note: The exact path may vary depending on the WFS version and specific service.
    # The following is an example for WFS 2.0.0. Adjust as necessary.
    namespaces = {'wfs': 'http://www.opengis.net/wfs/2.0'}
    typenames = []
    for feature_type in root.findall('.//wfs:FeatureType', namespaces=namespaces):
        # Find the Name element within each FeatureType
        name = feature_type.find('wfs:Name', namespaces=namespaces)
        if name is not None:
            typenames.append(name.text)

    return typenames


def get_feature(wfs_url, typename) -> io.BytesIO:
    params = {
        'service': 'WFS',
        'version': '2.0.0',
        'request': 'GetFeature',
        'typenames': typename,
        'outputFormat': 'application/json'
    }

    response = requests.get(wfs_url, params=params)

    # Check if the request was successful
    if response.status_code != 200:
        raise Exception(f"Request failed with status code: {response.status_code}: {response.text}")

    # Create a file-like object from the response content
    data = io.BytesIO(response.content)
    return data


# URL of the WFS service
wfs_urls = [
    "https://fbinter.stadt-berlin.de/fb/wfs/data/senstadt/s_wfs_baumbestand_an",
    "https://fbinter.stadt-berlin.de/fb/wfs/data/senstadt/s_vms_tempolimits_spatial"
]


for wfs_url in wfs_urls:
    typenames = get_capabilities(wfs_url)

    for typename in typenames:
        data = get_feature(wfs_url, typename)
        gdf = gpd.read_file(data)

        gdf.to_file(f"{typename}.geojson", driver="GeoJSON")
