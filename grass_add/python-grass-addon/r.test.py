#!/usr/bin/python
#
############################################################################
#
# MODULE:       r.viewshed.sum.py
# AUTHOR(S):    Anna, Luca, Markus, Vaclav, Pietro
# PURPOSE:      Performs a "cumulative viewshed analysis" using a vector points map as input
#               "viewing" locations, and calls r.viewshed to calculate the individual viewsheds.
# COPYRIGHT:    (C) 2015 by GRASS GIS development team
# REFERENCES:   Uses r.viewshed
#
#               This program is free software under the GNU General Public
#               License (>=v2). Read the file COPYING that comes with GRASS
#               for details.
#
#############################################################################

#%module
#% description: Performs a "cumulative viewshed analysis" using a vector points map as input "viewing" locations, and calls r.viewshed to calculate the individual viewsheds.
#% keyword: raster
#% keyword: viewshed
#%end

#%option G_OPT_R_INPUT
#%end
#%option G_OPT_V_INPUT
#% key: vector
#% description: Name of input vector points map containg the set of viewpoints
#%end
#%option G_OPT_R_OUTPUT
#% key: output
#% description: Output cumulative viewshed raster map
#%end

#%option
#% key: observer_elevation
#% type: double
#% description: Viewing elevation above the ground
#%answer: 1.75
#% required : no
#%end
#%option
#% key: target_elevation
#% type: double
#% description: Offset for target elevation above the ground
#%answer: 0.0
#% required : no
#%end

#%flag
#% key: k
#% label: Keep all interim viewshed maps
#% description:  Keep all interim viewshed maps (maps will be named "vshed_'name'", where 'name' is the value in "name_column" for each input point. If no value specified in "name_column", cat value will be used instead)
#%end
####################################################
# from future import module for python2 backward compatibility
from __future__ import print_function

# import modules and functions from the standard library
from pprint import pprint

# import modules and function from GRASS
import grass.script as gscript


def main(opts, flgs):
    print('Options:')
    pprint(opts)
    print('Flags:')
    pprint(flgs)


if __name__ == "__main__":
    import sys
    options, flags = gscript.parser()
    sys.exit(main(options, flags))-en 


