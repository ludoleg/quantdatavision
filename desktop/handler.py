# -*- coding: utf-8 -*-
"""
Created on Fri Feb 12 11:36:53 2016

@author: philippe
"""

import conductor
import numpy as np

import plottool
import os
import time

def openXRD(filename):
    """
   Opens an XRD file and returns two 1D array for 2theta and Intensity
   possible formats: TXT, PLV, DIF, MDI   ....   more to come
    """

    if filename.endswith(".plv"): 
        jump=50
        XRDdata = open(filename, 'r').readlines()[jump:]
        angle, diff = np.loadtxt(XRDdata, unpack=True)
       
    elif filename.endswith(".txt"):
        jump=7
        XRDdata = open(filename, 'r').readlines()[jump:]
        angle, diff = np.loadtxt(XRDdata, unpack=True)
        
    elif filename.endswith(".dif") or filename.endswith(".mdi"):
        dif = open(filename, 'r').readlines()
        paramline = dif[1]
        start, step, unknown, target, Lambda, stop, number = paramline.split()
        start=float(start)
        step=float(step)
        stop=float(stop)
        angle = np.arange(start, stop+step, step)
        diff = np.zeros_like(angle)
        #loop bellow reads data values of all but last line which all contain 8 entries
        for i in range(2,len(dif)-1):
            dataline = dif[i]
            dataline=dataline.split()
            linenumber = i-2
            for j in range(0,8):
                diffindex = ((linenumber)*8)+j
                diff[diffindex]=float(dataline[j])
                
        # bellow reads last line which can contain less than 8 entries
        lastline = dif[len(dif)-1]
        lastline = lastline.split()

        for i in range(0,len(lastline)):
             diffindex = ((len(dif)-3)*8)+i
             diff[diffindex]=float(lastline[i])

    return zip(angle, diff) #, target, Lambda  needs to be coded in txt and plv

datafilepath='XRD_data'
# datafilename = "CalciteP-film.plv"
datafilename = "Mix3D-film.txt"
DBfilepath=''
DBname="../reduced_difdata.txt"
phaselistname = 'phaselistall.csv'

InstrParams = {"Lambda": 0, "Target": '', "FWHMa": -0.001348, "FWHMb": 0.352021}

# datafilepath, datafilename = os.path.split(askopenfilename(filetypes=[("TXT files","*.txt")], title="Open XRD .txt file"))

t0=time.time()
difdata = open((os.path.join(DBfilepath, DBname)), 'r').readlines()
phaselist = open(os.path.join(DBfilepath, phaselistname), 'r').readlines()
SelectedPhases = [('Pyrolusite', 4.63),
                  ('Pyrope', 1.82),
                  ('Pyrophyllite', 0.71),
                  ('PyrrhotiteMon', 1.54),
                  ('PyrrhotiteHex', 5.14),
                  ('Quartz', 4.59),
                  ('Realgar', 1.96),
                  ('Rhodochrosite', 3.95),
                  ('Richterite', 0.51),
                  ('Riebeckite', 1.92),
                  ('Rutile', 3.84),
                  ('Sanidine', 0.79),
                  ('Sapphirine', 0.46),
                  ('Scheelite',	14.0)]

selectedphases = ['Actinolite','Aegirine','Alabandite','Albite','Almandine','Aluminotaramite','Alunite','Analcime','Andalusite','Andesine','Andradite','Anhydrite','AnhydriteGamma','Ankerite','Annite','Anorthite','Anorthoclase','Anthophyllite','Antigorite','Apatite','Aragonite','Arfvedsonite','Arsenic','Arsenopyrite','Augite','Autunite','Azurite','Barite','Barroisite','Beryl','Biotite','Bismuth','Bismuthinite','Bornite','Brannerite','Brucite','Bytownite','Calcio-olivine','Calcite','Carnotite','Carpholite','Cassiterite','Celadonite','Celsian','Cerussite','Chabazite','Chamosite','Chalcanthite','Chalcocite-alpha','Chalcocite','Chalcopyrite','Chromite','Cinnabar','Clinochlore','Clinoenstatite','Clinoferrosilite','Clinozoisite','Coffinite','Copper','Cordierite','Corundum','Covellite','Cubanite','Cummingtonite','Davidite-(La)','Diaspore','Dickite','Diopside','Dolomite','Dravite','Eckermannite','Elbaite','Enstatite','Epidote','Epsomite','Fayalite','Ferri-clinoholmquistite','Ferrohornblende','Ferrosilite','Fluorite','Fluor-liddicoatite','Fluorocannilloite','Fluoroleakeite','Foitite','Forsterite','Galena','Geikielite','Gersdorffite','Gibbsite','Glaucophane','Goethite','Gold','Graphite','Grossular','Grunerite','Gypsum','Halite','Halloysite-7A','Halloysite-10A','Hastingsite','Hedenbergite','Hematite','Hercynite','Holmquistite','Illite','Ilmenite','Iron','Jadeite','Jarosite','Kaersutite','Kaolinite','Kyanite','Labradorite','Laumontite','Lawsonite','Leucite','Lizardite','Magnesiofoitite','Magnesiohornblende','Magnesiosadanagaite','Magnesite','Magnetite','Malachite','Manganite','Margarite','Marialite','Meionite','Melanterite','Microcline','Millerite','Molybdenite','Molybdite','Monazite','Monticellite','Montmorillonite','Muscovite','Natrolite','Nepheline','Nyboite','Olenite','Oligoclase','Omphacite','Orpiment','Orthoclase','Pargasite','Pedrizite','Pentlandite','Periclase','Phlogopite','Prehnite','Pumpellyite','Pyrite','Pyrolusite','Pyrope','Pyrophyllite','PyrrhotiteMon','PyrrhotiteHex','Quartz','Realgar','Rhodochrosite','Richterite','Riebeckite','Rutile','Sanidine','Sapphirine','Scheelite','Schorl','Siderite','Sillimanite','Silver','Smithsonite','Sodalite','Spessartine','Sphalerite','Spinel','Spodumene','Staurolite','Stibnite','Stilbite','Strontianite','Sudoite','Sylvanite','Sylvite','Talc','Tephroite','Tetrahedrite','Thenardite','Thorianite','Thorite','Titanite','Topaz','Tremolite','Tschermakite','Uraninite','Uranophane-alpha','Uranophane-beta','Uvarovite','Uvite','Vesuvianite','Winchite','Xenotime','Zincite','Zircon','Zoisite']
#selectedphases = ['Actinolite','Albite','Almandine','Andalusite','Andesine','Anhydrite','Ankerite','Anorthite','Anthophyllite','Apatite','Aragonite','Augite','Barite','Beryl','Biotite','Calcite','Cerussite','Chabazite','Chamosite','Chalcopyrite','Chromite','Clinochlore','Cordierite','Corundum','Dickite','Diopside','Dolomite','Epsomite','Fayalite','Ferrohornblende','Fluorite','Forsterite','Galena','Gibbsite','Goethite','Grossular','Gypsum','Halite','Hematite','Illite','Ilmenite','Kaolinite','Labradorite','Lizardite','Magnesiofoitite','Magnesiohornblende','Magnesiosadanagaite','Magnesite','Magnetite','Microcline','Montmorillonite','Muscovite','Oligoclase','Periclase','Pyrite','Quartz']
#selectedphases = ['Iron']

#print "number of phase: ", len(selectedphases)

userData = openXRD(os.path.join(datafilepath, datafilename))

results, BG, calcdiff = conductor.Qanalyze(userData, difdata, SelectedPhases, InstrParams)
print "Total computation  time = %.2fs" %(time.time()-t0)
plot = plottool.overplotgraph(userData,BG,calcdiff, results[0:min(10,len(results))], datafilename)

#print plot, results


