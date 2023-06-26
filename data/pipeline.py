import requests
from xml.etree import ElementTree as ET
import geopandas as gpd
import pandas as pd
import io
from rtree import index
import json
import sqlite3


# URL of the WFS service
CONFIG = {
    "use_cached": True,
    "max_distance_to_street": 5,
    "epsg": 4326,
    "equidistant_epsg": 32633,
}

DATASET_INFO = {
    "trees": {
        "wfs_url": "https://fbinter.stadt-berlin.de/fb/wfs/data/senstadt/s_wfs_baumbestand",
        "expected_typename": "fis:s_wfs_baumbestand",
    },
    "streets": {
        "wfs_url": "https://fbinter.stadt-berlin.de/fb/wfs/data/senstadt/s_vms_detailnetz_spatial_gesamt",
        "expected_typename": "fis:s_vms_detailnetz_spatial_gesamt",
    },
    "speed_limits": {
        "wfs_url": "https://fbinter.stadt-berlin.de/fb/wfs/data/senstadt/s_vms_tempolimits_spatial",
        "expected_typename": "fis:s_vms_tempolimits_spatial",
    },
}


def get_data(
    dataset_name, CONFIG=CONFIG, DATASET_INFO=DATASET_INFO
) -> gpd.GeoDataFrame:
    def confirm_typename(wfs_url, expected_typename):
        # Define the parameters for the GetCapabilities request
        params = {"service": "WFS", "version": "2.0.0", "request": "GetCapabilities"}

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
        namespaces = {"wfs": "http://www.opengis.net/wfs/2.0"}
        typenames = []
        for feature_type in root.findall(".//wfs:FeatureType", namespaces=namespaces):
            # Find the Name element within each FeatureType
            name = feature_type.find("wfs:Name", namespaces=namespaces)
            if name is not None:
                typenames.append(name.text)

        if expected_typename not in typenames:
            raise Exception(
                f"Expected typename: {expected_typename}, but found: {typenames}"
            )

    def get_data_for_typename(wfs_url, typename) -> gpd.GeoDataFrame:
        params = {
            "service": "WFS",
            "version": "2.0.0",
            "request": "GetFeature",
            "typenames": typename,
            "outputFormat": "application/geo+json",
        }

        print(f"Downloading data for typename: {typename}...")

        response = requests.get(wfs_url, params=params)

        # Check if the request was successful
        if response.status_code != 200:
            raise Exception(
                f"Request failed with status code: {response.status_code}: {response.text}"
            )

        # Create a file-like object from the response content
        data = io.BytesIO(response.content)
        return gpd.read_file(data)

    wfs_url: str
    expected_typename: str
    try:
        wfs_url = DATASET_INFO[dataset_name]["wfs_url"]
        expected_typename = DATASET_INFO[dataset_name]["expected_typename"]
    except KeyError:
        raise Exception(f"Unknown name: {dataset_name}, make sure it is in the config")

    confirm_typename(wfs_url, expected_typename)

    print(f"Typename confirmed, loading {dataset_name} data...")

    if CONFIG["use_cached"]:
        try:
            with open(f"{dataset_name}.geojson", "r") as f:
                return gpd.read_file(f)
        except FileNotFoundError:
            pass

    gdf = get_data_for_typename(wfs_url, expected_typename)

    gdf.to_crs(epsg=CONFIG["epsg"], inplace=True)
    assert gdf.crs.to_epsg() == CONFIG["epsg"]
    return gdf


def clean_data(trees_gdf, streets_gdf, speed_limits_gdf) -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame, gpd.GeoDataFrame]:
    # Remove all streets that are not relevant for the analysis
    # (F)ußwege, (P)rivatstraßen, (W)aldwege, (N)icht-Klassifizierte Straßen, Radwege, (X) Fuß+Radwege,  (Z) Fußgängerzone, (Y) Planung, (Q) Straßenquerung
    irrelevant_street_types = ['F', 'P', 'W', 'N', 'R', 'X', 'Z', 'Y', 'Q']
    streets_gdf = streets_gdf[~streets_gdf['strassenklasse'].isin(irrelevant_street_types)]
    
    # Select only relevant columns
    trees_gdf = trees.dropna(subset=["strname"])
    trees_gdf = trees_gdf.loc[:, ["id", "strname", "gattung", "gattung_deutsch", "geometry"]]
    speed_limits_gdf = speed_limits_gdf.rename(columns={"wert_ves": "speed_limit"})
    speed_limits_gdf = speed_limits_gdf.loc[:, ["id", "elem_nr", "speed_limit", "geometry"]]
    streets_gdf = streets_gdf.rename(columns={"element_nr": "elem_nr"})
    streets_gdf = streets_gdf.loc[:, ["id", "strassenname", "strassenklasse", "elem_nr", "geometry"]]
    
    # make speed_limits_gdf["elem_nr"] unique
    # Remove all duplicated rows in speed_limits_gdf (streets can have multiple speed limits, but to keep it simple we only use the first one)
    speed_limits_gdf = speed_limits_gdf[~speed_limits_gdf["elem_nr"].duplicated(keep="last")]
    assert speed_limits_gdf["elem_nr"].is_unique
    
    return trees_gdf, streets_gdf, speed_limits_gdf
    
    
def get_tree_to_street_map(
    trees_gdf, streets_gdf
) -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
    def store_tree_to_street_map(tree_id_street_id_map):
        with open("tree_id_street_id_map.json", "w") as f:
            json.dump(tree_id_street_id_map, f)

    def load_tree_to_street_map() -> dict:
        with open("tree_id_street_id_map.json", "r") as f:
            return json.load(f)

    # Try to load the map from a file
    if CONFIG["use_cached"]:
        try:
            print("Loading tree to street map from file...")
            return load_tree_to_street_map()
        except FileNotFoundError:
            print("No tree to street map found, creating a new one...")
            pass

    # Create a spatial index of the streets
    idx = index.Index()
    for street_index, street in streets_gdf.iterrows():
        idx.insert(street_index, street["geometry"].bounds)

    # Resulting Map of tree id to street id
    tree_id_street_id_map = {}
    # Temporary map of tree index to street index
    tree_index_street_index_map = {}

    length = len(trees_gdf)
    percentile = 0
    # For each tree, find the closest street
    for tree_index, tree in trees_gdf.iterrows():
        if tree_index % (length // 100) == 0:
            print(f"Done with {percentile}%")
            percentile += 1

        closest_street_index = None
        closest_street = None
        # Get the id of the closest street in the spatial index
        for street_index in idx.nearest(
            tree.geometry.bounds, 5
        ):  # Check the 5 closest streets, for example
            street = streets_gdf.loc[street_index].geometry
            if closest_street_index is None:
                closest_street_index = street_index
                closest_street = street
            elif tree.geometry.distance(street) < tree.geometry.distance(
                closest_street
            ):
                closest_street = street
                closest_street_index = street_index

        tree_index_street_index_map[tree_index] = closest_street_index

    for tree_index, street_index in tree_index_street_index_map.items():
        tree = trees_gdf.loc[tree_index]
        street = streets_gdf.loc[street_index]
        tree_id_street_id_map[tree["id"]] = street["id"]

    store_tree_to_street_map(tree_id_street_id_map)

    return tree_id_street_id_map


if __name__ == "__main__":
    # Load the data
    trees = get_data("trees")
    streets = get_data("streets")
    speed_limits = get_data("speed_limits")
    
    # Clean the data
    trees, streets, speed_limits = clean_data(trees, streets, speed_limits)
    
    # Store the data
    trees.to_file("trees.geojson", driver="GeoJSON")
    streets.to_file("streets.geojson", driver="GeoJSON")
    speed_limits.to_file("speed_limits.geojson", driver="GeoJSON")

    # Merge streets and speed_limits
    streets["speed_limit"] = streets["elem_nr"].map(speed_limits.set_index("elem_nr")["speed_limit"]).fillna(50.0)
    # Update streets.geojson with speed limits
    streets.to_file("streets.geojson", driver="GeoJSON")
    
    # Merge streets and trees
    merged_data = pd.merge(streets, trees.drop(columns="geometry"), left_on="strassenname", right_on="strname", how="inner")
    # merged_data = (
    #     streets.to_crs(epsg=CONFIG["equidistant_epsg"])
    #     .sjoin_nearest(trees.to_crs(epsg=CONFIG["equidistant_epsg"]), how="left", distance_col="distance")#, max_distance=CONFIG["max_distance_to_street"])
    # ).to_crs(epsg=CONFIG["epsg"])
    
    merged_data.to_file("merged_data.geojson", driver="GeoJSON")
    
    # Create a map of tree id to street id
    # tree_id_street_id_map = get_tree_to_street_map(trees, streets)

    # Udapte the trees dataframe to include the street id and speed limit
    # trees["street_id"] = trees["id"].map(tree_id_street_id_map)
    # trees.dropna(subset=["street_id"], inplace=True)
    
    # Merge treea and streets for easier analysis
    # merged_gdf = pd.merge(streets, trees.drop(columns="geometry"), left_on="id", right_on="street_id", how="inner")

    # merged_gdf.to_file("merged_data.geojson", driver="GeoJSON")