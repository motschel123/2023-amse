import os
import geopandas as gpd
import pytest


@pytest.fixture(scope='function', autouse=True)
def rename_files():
    original_files = ['streets.geojson', 'trees.geojson', 'speed_limits.geojson', 'merged_data.geojson']
    renamed_files = ['tmp_streets.geojson', 'tmp_trees.geojson', 'tmp_speed_limits.geojson', 'tmp_merged_data.geojson']

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

    assert os.path.exists("trees.geojson")
    assert os.path.exists("streets.geojson")
    assert os.path.exists("speed_limits.geojson")
    assert os.path.exists("merged_data.geojson")
    
    print("Checking tree data...")
    trees = gpd.read_file("trees.geojson")

    assert "id" in trees.columns
    assert "strname" in trees.columns
    assert "gattung" in trees.columns
    assert "gattung_deutsch" in trees.columns
    assert "geometry" in trees.columns

    print("Checking street data...")
    streets = gpd.read_file("streets.geojson")
    
    assert "id" in streets.columns
    assert "strassenname" in streets.columns
    assert "strassenklasse" in streets.columns
    assert "elem_nr" in streets.columns
    assert "speed_limit" in streets.columns
    assert "geometry" in streets.columns
    
    print("Checking speed_limit data...")
    speed_limits = gpd.read_file("speed_limits.geojson")
    
    assert "id" in speed_limits.columns
    assert "elem_nr" in speed_limits.columns
    assert "speed_limit" in speed_limits.columns
    assert "geometry" in speed_limits.columns
    
    print("Checking merged data...")
    merged_data = gpd.read_file("merged_data.geojson")
    
    assert "id_x" in merged_data.columns
    assert "strassenname" in merged_data.columns
    assert "strassenklasse" in merged_data.columns
    assert "elem_nr" in merged_data.columns
    assert "speed_limit" in merged_data.columns
    assert "id_y" in merged_data.columns
    assert "strname" in merged_data.columns
    assert "gattung" in merged_data.columns
    assert "gattung_deutsch" in merged_data.columns
    assert "geometry" in merged_data.columns