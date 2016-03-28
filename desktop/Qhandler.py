# -*- coding: utf-8 -*-
"""
Created on Fri Feb 12 11:36:53 2016

@author: philippe
"""

import Conductor
import numpy as np
import os
import time

datafilepath='XRD_data'
datafilename = "Mix1A-film.txt"
DBfilepath=''
DBname="../reduced_difdata.txt"
phaselistname = 'phaselistall.csv'
Lambda = 0
Target = ''


#datafilepath, datafilename = os.path.split(askopenfilename(filetypes=[("TXT files","*.txt")], title="Open XRD .txt file"))

t0=time.time()
difdata = open((os.path.join(DBfilepath, DBname)), 'r').readlines()
phaselist = open(os.path.join(DBfilepath, phaselistname), 'r').readlines()
selectedphases = ['Actinolite','Aegirine','Alabandite','Albite','Almandine','Aluminotaramite','Alunite','Analcime','Andalusite','Andesine','Andradite','Anhydrite','AnhydriteGamma','Ankerite','Annite','Anorthite','Anorthoclase','Anthophyllite','Antigorite','Apatite','Aragonite','Arfvedsonite','Arsenic','Arsenopyrite','Augite','Autunite','Azurite','Barite','Barroisite','Beryl','Biotite','Bismuth','Bismuthinite','Bornite','Brannerite','Brucite','Bytownite','Calcio-olivine','Calcite','Carnotite','Carpholite','Cassiterite','Celadonite','Celsian','Cerussite','Chabazite','Chamosite','Chalcanthite','Chalcocite-alpha','Chalcocite','Chalcopyrite','Chromite','Cinnabar','Clinochlore','Clinoenstatite','Clinoferrosilite','Clinozoisite','Coffinite','Copper','Cordierite','Corundum','Covellite','Cubanite','Cummingtonite','Davidite-(La)','Diaspore','Dickite','Diopside','Dolomite','Dravite','Eckermannite','Elbaite','Enstatite','Epidote','Epsomite','Fayalite','Ferri-clinoholmquistite','Ferrohornblende','Ferrosilite','Fluorite','Fluor-liddicoatite','Fluorocannilloite','Fluoroleakeite','Foitite','Forsterite','Galena','Geikielite','Gersdorffite','Gibbsite','Glaucophane','Goethite','Gold','Graphite','Grossular','Grunerite','Gypsum','Halite','Halloysite-7A','Halloysite-10A','Hastingsite','Hedenbergite','Hematite','Hercynite','Holmquistite','Illite','Ilmenite','Iron','Jadeite','Jarosite','Kaersutite','Kaolinite','Kyanite','Labradorite','Laumontite','Lawsonite','Leucite','Lizardite','Magnesiofoitite','Magnesiohornblende','Magnesiosadanagaite','Magnesite','Magnetite','Malachite','Manganite','Margarite','Marialite','Meionite','Melanterite','Microcline','Millerite','Molybdenite','Molybdite','Monazite','Monticellite','Montmorillonite','Muscovite','Natrolite','Nepheline','Nyboite','Olenite','Oligoclase','Omphacite','Orpiment','Orthoclase','Pargasite','Pedrizite','Pentlandite','Periclase','Phlogopite','Prehnite','Pumpellyite','Pyrite','Pyrolusite','Pyrope','Pyrophyllite','PyrrhotiteMon','PyrrhotiteHex','Quartz','Realgar','Rhodochrosite','Richterite','Riebeckite','Rutile','Sanidine','Sapphirine','Scheelite','Schorl','Siderite','Sillimanite','Silver','Smithsonite','Sodalite','Spessartine','Sphalerite','Spinel','Spodumene','Staurolite','Stibnite','Stilbite','Strontianite','Sudoite','Sylvanite','Sylvite','Talc','Tephroite','Tetrahedrite','Thenardite','Thorianite','Thorite','Titanite','Topaz','Tremolite','Tschermakite','Uraninite','Uranophane-alpha','Uranophane-beta','Uvarovite','Uvite','Vesuvianite','Winchite','Xenotime','Zincite','Zircon','Zoisite']
#selectedphases = ['Actinolite','Albite','Almandine','Andalusite','Andesine','Anhydrite','Ankerite','Anorthite','Anthophyllite','Apatite','Aragonite','Augite','Barite','Beryl','Biotite','Calcite','Cerussite','Chabazite','Chamosite','Chalcopyrite','Chromite','Clinochlore','Cordierite','Corundum','Dickite','Diopside','Dolomite','Epsomite','Fayalite','Ferrohornblende','Fluorite','Forsterite','Galena','Gibbsite','Goethite','Grossular','Gypsum','Halite','Hematite','Illite','Ilmenite','Kaolinite','Labradorite','Lizardite','Magnesiofoitite','Magnesiohornblende','Magnesiosadanagaite','Magnesite','Magnetite','Microcline','Montmorillonite','Muscovite','Oligoclase','Periclase','Pyrite','Quartz']
#selectedphases = ['Albite','Microcline','Quartz']

#print "number of phase: ", len(selectedphases)

twoT, diff = Conductor.openXRD(os.path.join(datafilepath, datafilename))
results, plot = Conductor.Qanalyze(twoT, diff ,difdata, phaselist, selectedphases, Lambda, Target)


#print plot, results

print "time of computation = %.2fs" %(time.time()-t0)
