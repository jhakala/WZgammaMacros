from math import sqrt
from ROOT import *
from pyrootTools import instance
from HgParameters import getSamplesDirs, getNormalizations, getMassWindows, getSigNevents
from recheckOptimization import MCbgGetSoverRootB


# Script for checking Hgamma expected limits
# Optimize using the CL95cms expected routine
# John Hakala, 5/11/2016

# Below is the documentation from Greg's CL95cms code.

# # Usage to get actual and expected limit respectively: 
# #        sigma95 = CL95(ilum, slum, eff, seff, bck, sbck, n, gauss = false, nuisanceModel = 0)
# #        sigma95A = CLA(ilum, slum, eff, seff, bck, sbck, nuisanceModel = 0)
# # 
# # Inputs:	ilum - Nominal integrated luminosity (pb^-1)
# #			slum - Absolute error on the integrated luminosity
# #			eff  - Nominal value of the efficiency times acceptance (in range 0 to 1)
# #			seff - Absolute error on the efficiency times acceptance
# #			bck  - Nominal value of the background estimate
# #			sbck - Absolute error on the background
# #			n    - Number of observed events (not used for the expected limit)
# #			gauss - if true, use Gaussian statistics for signal instead of Poisson; automatically false for n = 0. Always false for expected limit calculations
# #			nuisanceModel - distribution function used in integration over nuisance parameters: 
# #					   0 - Gaussian, 1 - lognormal, 2 - gamma; (automatically 0 when gauss == true)

testTwoMasses = False

ilum = 2700         # pb-1
slum = ilum * .027  # 2.7 percent lumi uncertainty
sbck = .2       # This is basically 1-|kfactor|, where kfactor is 0.8

uncertainties = {}
uncertainties["pileup"] = .05
uncertainties["JES"]    = .02
uncertainties["JER"]    = .02
uncertainties["Htag"]   = .05
uncertainties["btag"]   = .20   # this is a guess, follow up
print "Uncertainties are: ",
print uncertainties

sumSquares = 0.
for key in uncertainties.keys():
  sumSquares += (uncertainties[key])**2
quadratureUncertainties = sqrt(sumSquares)
print "overall uncertainty is: %f" % quadratureUncertainties




def getExpectedLimit(small3sDir, ddDir, mass, masswindow, HbbCutValue, compileOrLoad):
  instance("CL95cms", compileOrLoad)
  sigAndBGinfo = MCbgGetSoverRootB(small3sDir, ddDir, mass, massWindows[mass], HbbCutValue, compileOrLoad)
  print "for mass %i, mass window %i - %i, cut value %f, S is %s and B is %s" % (mass, massWindows[mass][0], massWindows[mass][1], HbbCutValue, sigAndBGinfo["S"], sigAndBGinfo["B"])
  nGenEvents = getSigNevents()[str(mass)] 
  print "Number of events for signal with mass %i is %i" % (mass, nGenEvents)
  eff = sigAndBGinfo["S"]/nGenEvents
  seff = eff*quadratureUncertainties
  bck = sigAndBGinfo["B"]
  sbck = sigAndBGinfo["B"]*quadratureUncertainties
  expectedLimit = CLA(ilum, slum, eff, seff, bck, sbck)
  print "expected limit is: %f" % expectedLimit
  compileOrLoad = "load"
  response = {}
  response["compileOrLoad"]="load"
  response["expectedLimit"]=expectedLimit
  return response
  


samplesDirs = getSamplesDirs()
small3sDir = samplesDirs["small3sDir"]
ddDir = samplesDirs["ddDir"]
massWindows = getMassWindows()
if testTwoMasses:
  del massWindows[1000]
  del massWindows[2000]
graphs = []
compileOrLoad = "compile"
for mass in massWindows.keys():
  graphs.append(TGraph())
  graphs[-1].SetNameTitle(str(mass), str(mass))
  for i in range(-10, 20):        # TODO make some reasonable way of chosing the step size and bounds for the optimization scan
    HbbCutValue = i/float(20)
  #for i in range(0, 4):
  #  HbbCutValue = (i/float(3))-0.1
    expectedLimitInfo = getExpectedLimit(small3sDir, ddDir, mass, massWindows[mass], HbbCutValue, compileOrLoad)
    compileOrLoad = expectedLimitInfo["compileOrLoad"]
    expectedLimit = expectedLimitInfo["expectedLimit"]
    graphs[-1].SetPoint(graphs[-1].GetN(), HbbCutValue, expectedLimit)

iColor = 0
canvas = TCanvas()
canvas.cd()
for graph in graphs:
  graph.SetLineColor(kRed + 2*iColor)
  if iColor == 0:
    graph.Draw()
  else:
    graph.Draw("SAME")
  print "Just drew graph with title %s and name %s" % (graph.GetTitle(), graph.GetName())
  print graph
  iColor+=1

canvas.Update()
outfile = TFile("HbbOpt_cl95.root", "RECREATE")
canvas.Write()
outfile.Close()



