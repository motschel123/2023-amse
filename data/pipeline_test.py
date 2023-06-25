import os
import geopandas as gpd
import pytest


@pytest.fixture(scope='function', autouse=True)
def rename_files():
    original_files = ['streets.geojson', 'trees.geojson', 'tree_id_street_id_map.json', 'data.db']
    renamed_files = ['tmp_streets.geojson', 'tmp_trees.geojson', 'tmp_tree_id_street_id_map.json', 'tmp_data.db']

    # Renaming files
    for original, renamed in zip(original_files, renamed_files):
        if os.path.exists(original):
            os.rename(original, renamed)

    yield  # This is where the testing happens

    # Reverting back to original names even if test fails
    for original, renamed in zip(original_files, renamed_files):
        if os.path.exists(renamed):
            os.rename(renamed, original)

def test_pipeline():
    print("Running pipeline...")
    os.system("python pipeline.py")

    assert os.path.exists("streets.geojson")
    assert os.path.exists("trees.geojson")
    assert os.path.exists("tree_id_street_id_map.json")
    assert os.path.exists("data.db")
    
    print("Checking tree data...")
    trees = gpd.read_file("trees.geojson")

    assert "id" in trees.columns
    assert "street_id" in trees.columns
    assert "street_speed_limit" in trees.columns
    assert "gattung" in trees.columns
    assert "gattung_deutsch" in trees.columns

    print("Checking street data...")
    streets = gpd.read_file("streets.geojson")
    
    assert "id" in streets.columns
    assert "wert_ves" in streets.columns
    assert "geometry" in streets.columns