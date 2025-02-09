def save_terrain_data(terrain_map, filename="data_files/terrain_data.csv"):
    try:
        with open(filename, "w") as file:
            file.write("Row,Col,Elevation,Rainfall,Temperature, Fertility, Vegetation density, Water\n")  # Header

            for r in range(len(terrain_map)):
                for c in range(len(terrain_map[0])):
                    elevation, rainfall, temperature, fertility, vegetation, water,steepness = terrain_map[r][c]
                    file.write(f"{r},{c},{elevation},{rainfall},{temperature},{fertility},{vegetation},{water},{steepness}\n")

        print(f"Terrain data saved successfully to {filename}")
    
    except Exception as e:
        print(f"Error saving terrain data: {e}")

def save_colour_data(colour_map, filename="data_files/colour_data.csv"):
    try:
        with open(filename, "w") as file:
            file.write("Row,Col,Colour\n")  # Header

            for r in range(len(colour_map)):
                for c in range(len(colour_map[0])):
                    file.write(f"{r},{c},{colour_map[r][c]}\n")

        print(f"Colour data saved successfully to {filename}")
    
    except Exception as e:
        print(f"Error saving colour data: {e}")

def save_environment_data(environment_map, filename="data_files/environment_data.csv"):
    try:
        with open(filename, "w") as file:
            file.write("Row,Col,Traversal Cost, Desiribility, Water Proximity\n")  # Header

            for r in range(len(environment_map)):
                for c in range(len(environment_map[0])):
                    file.write(f"{r},{c},{environment_map[r][c][2]},{environment_map[r][c][3]},{environment_map[r][c][4]}\n")

        print(f"Colour data saved successfully to {filename}")
    
    except Exception as e:
        print(f"Error saving colour data: {e}")