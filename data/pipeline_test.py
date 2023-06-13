import os


def test_pipeline():
    os.system("python pipeline.py")

    assert os.path.exists("streets.geojson")
    assert os.path.exists("trees.geojson")
    assert os.path.exists("tree_id_street_id_map.json")
    assert os.path.exists("data.db")
