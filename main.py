import maup
import time
import geopandas as gpd

maup.progress.enabled = True

# Load the data
start_time = time.time()
ohio = gpd.read_file("Ohio.shp")
end_time = time.time()
print("The time to import il_pl2020_p2_b.shp is:", (end_time - start_time) / 60, "mins")
