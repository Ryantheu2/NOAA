import glob
import sys
import numpy as np
import matplotlib as mpl
from matplotlib import pyplot as plt
from cartopy import crs as ccrs
from netCDF4 import Dataset
import os
from PIL import Image
import tarfile
mpl.rcParams['figure.figsize'] = 20, 10


def gdal_transform(img, output_folder):
    os.system("/data/starfs1/utils/geo2grid_v_1_0_1/bin/gdal_translate -of GTiff -a_srs EPSG:4326 -a_ullr -180 90 180 -90 " + img + " " + output_folder)
    os.remove(img)


def run_tiles(img_tif, output_folder):
    os.system("python /data/www/smcd/spb/aq/COVID_Dashboard/gdal2tiles.py -p mercator -z 2-7 --xyz " + img_tif +
              " /data/www/smcd/spb/aq/COVID_Dashboard/dist/satellite_image/" + output_folder)


def white_to_transparency(folder, img_path):
    img = Image.open(img_path)
    img = img.convert("RGBA")
    datas = img.getdata()

    newData = []
    for item in datas:
        if item[0] == 255 and item[1] == 255 and item[2] == 255:
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)

    img.putdata(newData)
    img.save(folder + "/img.png", "PNG")
    os.remove(img_path)


def check_folder_existence(output_folder, folder_name):
    check = os.path.isdir(output_folder + "/" + folder_name)
    return check


# color bar for CO and NO2

red = [252, 244, 236, 228, 219, 211, 204, 195, 187, 180, 170, 162, 154, 147,
       139, 129, 106,  77,  48,  19,  10,  33,  55,  77,  99, 124, 148, 170,
       192, 214, 236, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
       255, 255, 255, 255, 255, 255, 253, 244, 235, 225, 216, 205, 196, 186,
       177, 168, 156, 147, 137, 128, 119, 108, 102, 101, 101, 101, 100, 100,
       100, 100, 100, 100, 100, 100, 101, 102, 103, 104, 106, 107, 108, 110,
       111, 112, 113, 115, 116, 117, 119, 120, 122, 125, 129, 132, 137, 141,
       144, 148, 151, 156, 159, 163, 166, 171, 174, 178, 182, 185, 189, 193,
       197, 201, 205, 208, 212, 216, 220, 223, 227, 231, 235, 239, 243, 246]

green = [255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
         255, 254, 242, 225, 209, 192, 183, 190, 196, 202, 209, 216, 223, 229,
         235, 241, 248, 248, 234, 220, 206, 192, 177, 159, 146, 131, 117,  99,
         85,  71,  57,  42,  28,  10,   0,   0,   0,   0,   0,   0,   0,   0,
         0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
         0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
         0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
         0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
         0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0]

blue = [255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
        255, 253, 211, 153,  96,  38,   0,   0,   0,   0,   0,   0,   0,   0,
        0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
        0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
        0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   1,   2,   2,   3,
        4,   5,   6,   7,   8,   9,  18,  32,  46,  64,  79,  92, 107, 121,
        139, 153, 168, 182, 197, 211, 229, 243, 255, 255, 255, 255, 255, 255,
        255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
        255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255]


def no2_process(input_file, output_folder):
    date = input_file.split("_")[-2][0:6]

    if 'npp' in input_file.lower():
        folder_file_name = "OMPS_" + date
    else:
        folder_file_name = "TROPOMI_" + date

    print(folder_file_name)
    if not check_folder_existence(output_folder, folder_file_name):

        os.mkdir(output_folder + "/" + folder_file_name)

        rgb_list = [red, green, blue]
        rgb = list(map(list, zip(*rgb_list)))
        # print(rgb)

        hex_list = []
        for color in rgb:
            hex_list.append('#%02x%02x%02x' % (color[0], color[1], color[2]))

        fig = plt.figure()
        ax = fig.add_subplot(projection=ccrs.PlateCarree())
        ax.set_extent([-180, 180, -90, 90], crs=ccrs.PlateCarree())

        file_id = Dataset(input_file)
        no2 = file_id.variables['DT'][:, :]

        lat = file_id.variables['LAT'][:, :]
        lon = file_id.variables['LON'][:, :]

        contour_interval = 0.1
        data_range = np.arange(0, 300.1, contour_interval)

        # Create filled contour plot of AOD data
        cmap = mpl.colors.ListedColormap(hex_list)
        print('Begin')
        ax.contourf(lon, lat, no2, data_range, cmap=cmap)
        print('End')
        plt.savefig(output_folder + "/" + folder_file_name + '/no2.png', dpi=600, transparent=True, bbox_inches='tight',
                    pad_inches=0)

        white_to_transparency(output_folder + "/" + folder_file_name,
                              output_folder + "/" + folder_file_name + '/no2.png')
        # gdal_transform(img, output_folder)
        # run_tiles(img_tif, output_folder)

    else:
        print("Folder " + output_folder + "/" + folder_file_name + " already exists")


def aod_process(input_file, output_folder):

    date = input_file.split("_")[-2][0:6]

    if 'npp' in input_file.lower():
        folder_file_name = "SNPP_" + date
    else:
        date = input_file.split("_")[-1][0:6]
        folder_file_name = "NOAA-20_" + date

    if not check_folder_existence(output_folder, folder_file_name):

        os.mkdir(output_folder + "/" + folder_file_name)

        fig = plt.figure()
        ax = fig.add_subplot(projection=ccrs.PlateCarree())
        ax.set_extent([-180, 180, -90, 90], crs=ccrs.PlateCarree())

        bar = 'rainbow'
        max_color = 'darkred'
        color_map = plt.get_cmap(bar)
        color_map.set_over(max_color)

        file_id = Dataset(input_file)

        data_range = np.arange(0, 1.1, .001)

        aod = file_id.variables['aod'][:, :]

        lat = file_id.variables['lat'][:]
        lon = file_id.variables['lon'][:]

        ax.contourf(lon, lat, aod, data_range, cmap=color_map, extend='both')

        plt.savefig(output_folder + "/" + folder_file_name + '/aod.png', dpi=600, transparent=True,
                    bbox_inches='tight', pad_inches=0)

        white_to_transparency(output_folder + "/" + folder_file_name,
                                output_folder + "/" + folder_file_name + '/aod.png')

    else:
        print("Folder " + output_folder + "/" + folder_file_name + " already exists")


def co_process(input_file, output_folder):

    name = input_file.split("\\")[-1]
    # folder_name = name.split("_")[-2]

    year = name.split("_")[-3]
    month = name.split("_")[-2][-2:]

    folder_file_name = "CO_" + year + month

    if not check_folder_existence(output_folder, folder_file_name):

        os.mkdir(output_folder + "/" + folder_file_name)

        my_tar = tarfile.open(input_file)
        my_tar.extractall(output_folder + '/' + folder_file_name)  # specify which folder to extract to
        my_tar.close()

        folder_list = glob.glob(output_folder + '/' + folder_file_name + '/*')

        # print(file_list)
        file_count = 0
        print(folder_list)
        print(len(folder_list))
        for folder in folder_list:
            file_list = glob.glob(folder + "\\*")
            for file in file_list:
                if file_count == 0:
                    file_id = Dataset(file)
                    CO_data = file_id.variables['CO'][:, :]
                else:
                    file_id = Dataset(file)
                    CO_data = CO_data + file_id.variables['CO'][:, :]

            file_count += len(file_list)

        print(file_count)
        CO = CO_data / file_count
        print('Done')

        lat = file_id.variables['XLAT'][:, :]
        lon = file_id.variables['XLONG'][:, :]

        rgb_list = [red, green, blue]
        rgb = list(map(list, zip(*rgb_list)))
        # print(rgb)

        hex_list = []
        for color in rgb:
            hex_list.append('#%02x%02x%02x' % (color[0], color[1], color[2]))

        fig = plt.figure()
        ax = fig.add_subplot(projection=ccrs.PlateCarree())
        ax.set_extent([-180, 180, -90, 90], crs=ccrs.PlateCarree())

        data_range = np.arange(0, 1.1, .0001)

        # Create filled contour plot of CO data
        cmap = mpl.colors.ListedColormap(hex_list)
        print('Begin')
        ax.contourf(lon, lat, CO[0], data_range, cmap=cmap)
        print('End')
        plt.savefig(output_folder + '/' + folder_file_name + '/co.png', dpi=900, transparent=True,
                    bbox_inches='tight', pad_inches=0)

        white_to_transparency(output_folder + '/' + folder_file_name,
                                output_folder + '/' + folder_file_name + 'co.png')

    else:
        print("Folder " + output_folder + "/" + folder_file_name + " already exists")


if __name__ == "__main__":
    # input_folder = sys.argv[1]
    # output_folder = sys.argv[2]
    print(os.getcwd())
    input_folder = "F:/Zigang Data/test/*"
    output_folder = "E:/Output/"

    file_list = glob.glob(input_folder)
    print(file_list)
    for file in file_list:
        if "no2" in file.lower():
            no2_process(file, output_folder)
        elif "aod" in file.lower():
            aod_process(file, output_folder)
        elif "onroad" in file.lower():
            co_process(file, output_folder)
        else:
            print(file + ": file not recognized as NO2, AOD, or CO")
