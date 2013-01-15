#-------------------------------------------------------------------------------
# Name:        Reading polar volume data
# Purpose:
#
# Author:      heistermann
#
# Created:     14.01.2013
# Copyright:   (c) heistermann 2013
# Licence:     MIT
#-------------------------------------------------------------------------------
#!/usr/bin/env python

import wradlib
import numpy as np
import pylab as pl

if __name__ == '__main__':

    # read the data (sample file in wradlib/examples/data)
    raw = wradlib.io.read_OPERA_hdf5("data/knmi_polar_volume.h5")
    # this is the radar position tuple (latitude, longitude, altitude)
    sitecoords = (raw["where"]["lat"], raw["where"]["lon"],raw["where"]["height"])
    # define your cartesian reference system
    projstr = wradlib.georef.create_projstr("utm",zone=32, hemisphere="north")
    # containers to hold Cartesian bin coordinates and data
    xyz, data = np.array([]).reshape((-1,3)), np.array([])
    # iterate over 14 elevation angles
    for i in range(14):
        # get the scan metadata for each elevation
        where = raw["dataset%d/where"%(i+1)]
        what  = raw["dataset%d/data1/what"%(i+1)]
        # define arrays of polar coordinate arrays (azimuth and range)
        az = np.roll(np.arange(0.,360.,360./where["nrays"]), -where["a1gate"])
        r  = np.arange(where["rstart"], where["rstart"]+where["nbins"]*where["rscale"], where["rscale"])
        # derive 3-D Cartesian coordinate tuples
        xyz_ = wradlib.vpr.volcoords_from_polar(sitecoords, where["elangle"], az, r, projstr)
        # get the scan data for this elevation
        #   here, you can do all the processing on the 2-D polar level
        #   e.g. clutter elimination, attenuation correction, ...
        data_ = what["offset"] + what["gain"] * raw["dataset%d/data1/data"%(i+1)]
        # transfer to containers
        xyz, data = np.vstack( (xyz, xyz_) ), np.append(data, data_.ravel())
    # define regular Cartesian target coordinates
    trgx = np.linspace(xyz[:,0].min(), xyz[:,0].max(), 200)
    trgy = np.linspace(xyz[:,1].min(), xyz[:,1].max(), 200)
    trgz = np.arange(0,8000.,500.)
    trgxyz = wradlib.util.gridaspoints(trgx, trgy, trgz)
    cappishape = (len(trgx), len(trgy), len(trgz))
    # interpolate to Cartesian volume
    gridder = wradlib.vpr.CartesianVolume(xyz, trgxyz)
    cartvol = np.ma.masked_invalid( gridder(data).reshape(cappishape) )
    # diagnostic plot
    wradlib.vis.plot_max_plan_and_vert(trgx, trgy, trgz, cartvol, unit="dBZH", levels=range(-32,67))




