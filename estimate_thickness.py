# Copyright 2020 Memphis Meats Inc.

# estimate_thickness.py: estimates the thickness of adherent tissue from microscopy data

import os
import sys
import math
import click
import xml.etree.ElementTree as ET
import cv2
from matplotlib import pyplot as plt


@click.command()
@click.option('--dir', type=click.Path(exists=True))
@click.option('--imageset', type=click.STRING)
def main(dir, imageset):
    '''
    Driver method for microscopy proof of concept
    :param dir: Main directory containing stereomicroscopy scans
    :param imageset: Specific image set's file prefix, e.g. substrate1_Series001_ICC
    :return:
    '''
    if not os.path.isfile(os.path.join(dir, 'MetaData',  imageset + '.xml')):
        print(f"No metadata found for file set {imageset} in {dir}.")
        sys.exit(-1)

    # Parse properties XML to find Z-slice thickness
    z_slice_thickness = None
    z_slice_count = None
    z_thickness_units = None

    properties_tree = ET.parse(os.path.join(dir, 'MetaData',  imageset + '_Properties.xml'))
    image_dimensions = properties_tree.findall('./Image/ImageDescription/Dimensions/DimensionDescription')
    for dimension in image_dimensions:
        if dimension.attrib['DimID'] == 'Z':
            z_slice_count = int(dimension.attrib['NumberOfElements'])
            z_thickness_units = dimension.attrib['Unit']
            z_thickness_length = float(dimension.attrib['Length'])
            z_slice_thickness = z_thickness_length / z_slice_count
            break

    if z_slice_thickness is None:
        print(f"Could not find Z dimension information in metadata.")
        sys.exit(-1)

    images = []
    titles = []
    for image_index in range(z_slice_count):
        image_filename = os.path.join(dir, imageset + f'_z{image_index:02}_ch00.tif')
        z_slice_image = cv2.imread(image_filename)
        z_slice_image_gray = cv2.cvtColor(z_slice_image, cv2.COLOR_BGR2GRAY)
        ret, z_slice_image_thresh = cv2.threshold(z_slice_image_gray, 100, 255, cv2.THRESH_BINARY)
        images.append(z_slice_image_thresh)
        titles.append(f'z{image_index:02}')

    estimated_thickness = z_slice_thickness * 8

    plot_panes_cols = math.ceil(math.sqrt(len(images)))
    plot_panes_rows = math.ceil(len(images) / plot_panes_cols)
    plt.figure(figsize=(12, 8))
    for i in range(len(images)):
        plt.subplot(plot_panes_cols, plot_panes_rows, i + 1), plt.imshow(images[i], 'gray')
        plt.title(titles[i])
        plt.xticks([]), plt.yticks([])
        plt.tight_layout()
        plt.suptitle(f'Estimated tissue thickness: {estimated_thickness:.2f} {z_thickness_units}')
    plt.show()


if __name__ == '__main__':
    main()
