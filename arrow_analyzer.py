#!/usr/bin/env python

import numpy as np
import ROOT
import awkward
import pyarrow
import uproot_methods



def compute_m(vList):
    v1 = ROOT.TLorentzVector()
    for i in vList:
        v1 += i
    return v1.M()



def find_m(arrow_data):
    sw = ROOT.TStopwatch()
    sw.Start()
    
    object_table = awkward.fromarrow(arrow_data)
    new_object_table = object_table['Electrons_pt'] * object_table['Electrons_eta']
    # print(new_object_table.flatten())
    
    v_particles = uproot_methods.TLorentzVectorArray.from_ptetaphi(
        object_table['Electrons_pt'], object_table['Electrons_eta'],
        object_table['Electrons_phi'], object_table['Electrons_e'],
        )
    
    print(v_particles[v_particles.counts > 0][0].eta.tolist())

    sw.Stop()
    print('Real time: ' + str(round(sw.RealTime() / 60.0, 2)) + ' minutes')
    print('CPU time:  ' + str(round(sw.CpuTime() / 60.0, 2)) + ' minutes')
