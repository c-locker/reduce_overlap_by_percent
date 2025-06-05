# reduce\_overlap\_by\_percent.py #

 is a python script for Agisoft Metashape Professional. It can be used to achieve a reduced overlap of cameras if you have a lot of photos. It works by projecting the sensor corner to the surface and picking the next points on the surface. Therefore it only works well with nadir images and a surface with low differences in height in comparison to flight altitude.

Usage:

    reduce\_overlap\_by\_percent.py --overlap \[--margin\¸]

    --overlap: (required) desired overlap in percent
    --margin: (optional) margin to desired overlap, default = 2

You need to select at least two cameras for this script to work. As a result of this script only a subset of the selected cameras needed to achieve the desired overlap get activated.
