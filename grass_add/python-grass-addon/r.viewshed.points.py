#!/usr/bin/env python

#%module
#% description: Compute and analyze viewsheds
#% keyword: raster
#% keyword: viewshed
#%end
#%option G_OPT_R_INPUT
#% key: elevation
#%end
#%option G_OPT_V_INPUT
#% key: points
#%end
#%option G_OPT_V_OUTPUT
#% key: output_points
#%end
#%option G_OPT_R_BASENAME_OUTPUT
#% key: viewshed_basename
#%end
#%option
#% key: observer_elevation
#% type: double
#% required: no
#% multiple: no
#% key_desc: value
#% description: Viewing elevation above the ground
#% answer: 1.75
#%end
#%option
#% key: max_distance
#% key_desc: value
#% type: double
#% description: Maximum visibility radius. By default infinity (-1)
#% answer: -1
#% multiple: no
#% required: no
#%end
#%flag
#% key: c
#% description: Consider the curvature of the earth (current ellipsoid)
#%end


import os
import atexit
import grass.script as gscript
from grass.pygrass.vector import VectorTopo


TMP_MAPS = []


def main():
    options, flags = gscript.parser()
    elevation = options['elevation']
    input_points = options['points']
    basename = options['viewshed_basename']
    output_points = options['output_points']
    observer_elev = options['observer_elevation']
    max_distance = float(options['max_distance'])
    flag_curvature = 'c' if flags['c'] else ''

    tmp_prefix = 'tmp_r_viewshed_points_' + str(os.getpid()) + '_'
    tmp_viewshed_name = tmp_prefix + 'viewshed'
    tmp_viewshed_vector_name = tmp_prefix + 'viewshed_vector'
    tmp_visible_points = tmp_prefix + 'points'
    tmp_point = tmp_prefix + 'current_point'
    TMP_MAPS.extend([tmp_viewshed_name, tmp_viewshed_vector_name, tmp_visible_points, tmp_point])

    columns = [('cat', 'INTEGER'),
               ('area', 'DOUBLE PRECISION'),
               ('n_points_visible', 'INTEGER'),
               ('distance_to_closest', 'DOUBLE PRECISION')]

    with VectorTopo(input_points, mode='r') as points, \
         VectorTopo(output_points, mode='w', tab_cols=columns) as output:

        for point in points:
            viewshed_id = str(point.cat)
            viewshed_name = basename + '_' + viewshed_id
            gscript.run_command('r.viewshed', input=elevation,
                                output=tmp_viewshed_name, coordinates=point.coords(),
                                max_distance=max_distance, flags=flag_curvature,
                                observer_elev=observer_elev, overwrite=True, quiet=True)
            gscript.mapcalc(exp="{viewshed} = if({tmp}, {vid}, null())".format(viewshed=viewshed_name,
                                                                               tmp=tmp_viewshed_name,
                                                                               vid=viewshed_id))

            # viewshed size
            cells = gscript.parse_command('r.univar', map=viewshed_name,
                                          flags='g')['n']
            area = float(cells) * gscript.region()['nsres'] * gscript.region()['nsres']

            # visible points
            gscript.run_command('r.to.vect', input=viewshed_name, output=tmp_viewshed_vector_name,
                                type='area', overwrite=True, quiet=True)
            gscript.run_command('v.select', ainput=input_points, atype='point',
                                binput=tmp_viewshed_vector_name, btype='area', 
                                operator='overlap', flags='t', 
                                output=tmp_visible_points, overwrite=True, quiet=True)
            n_points_visible = gscript.vector_info_topo(tmp_visible_points)['points'] - 1

            # distance to closest visible point
            if float(n_points_visible) >= 1:
                gscript.write_command('v.in.ascii', input='-', stdin='%s|%s' % (point.x, point.y),
                                      output=tmp_point, overwrite=True, quiet=True)
                distance = gscript.read_command('v.distance', from_=tmp_point, from_type='point', flags='p',
                                                to=tmp_visible_points, to_type='point', upload='dist',
                                                dmin=1, quiet=True).strip()

                distance = float(distance.splitlines()[1].split('|')[1])
            else:
                distance = 0

            #
            # write each point with its attributes
            #
            output.write(point, (area, n_points_visible, distance))
            output.table.conn.commit()

def cleanup():
    gscript.run_command('g.remove', type='raster', name=','.join(TMP_MAPS), flags='f')
    
if __name__ == '__main__':
    atexit.register(cleanup)
    main()
