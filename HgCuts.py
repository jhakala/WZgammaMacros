# functions to define the selection cuts for 
import copy
from ROOT import TCut

def getCutValues():
  cutValues = {}
  cutValues["minInvMass"] = 600
  cutValues["photonEta"]  = 1.4442
  cutValues["jetEta"]     = 2.2
  cutValues["deltaR"]     = 1.1
  cutValues["ptOverM"]    = 0.35
  cutValues["Hbb"]        = 0.9
  return cutValues


def combineCuts(cutDict):
  combinedCut = TCut()
  for cut in cutDict.keys():
    combinedCut += cutDict[cut]
  return combinedCut

def getDefaultCuts(region):
    cutValues = getCutValues()

    cuts = {} 
    cuts["phEta"]    = TCut( "leadingPhAbsEta<%f"           % cutValues["photonEta"]  )
    cuts["ptOverM"]  = TCut( "phPtOverMgammaj>%f"           % cutValues["ptOverM"]    )
    if region is "higgs":
      cuts["turnon"]   = TCut( "phJetInvMass_pruned_higgs>%f" % cutValues["minInvMass"] )
      cuts["deltaR"]   = TCut( "phJetDeltaR_higgs>%f"         % cutValues["deltaR"]     )
      cuts["jetEta"]   = TCut( "higgsJet_pruned_abseta<%f"    % cutValues["jetEta"]     )
      cuts["btag"]     = TCut( "higgsJet_HbbTag>%f"           % cutValues["Hbb"]        )
      cuts["antibtag"] = TCut( "higgsJet_HbbTag<%f"           % cutValues["Hbb"]        )
    elif region is "side5070" or "side100110":
      if region is "side5070":
        index = "Three"
      else:
        index = "Four"
      cuts["turnon"]   = TCut( "phJetInvMass_pruned_sideLow%s>%f" % (index, cutValues["minInvMass"] ))
      cuts["deltaR"]   = TCut( "phJetDeltaR_sideLow%s>%f"         % (index, cutValues["deltaR"]     ))
      cuts["jetEta"]   = TCut( "sideLow%sJet_pruned_abseta<%f"    % (index, cutValues["jetEta"]     ))
      cuts["btag"]     = TCut( "sideLow%sJet_HbbTag>%f"           % (index, cutValues["Hbb"]        ))
      cuts["antibtag"] = TCut( "sideLow%sJet_HbbTag<%f"           % (index, cutValues["Hbb"]        ))
    else:
      print "Invalid region!!!"
      quit()
    return cuts
    
def getBtagComboCut(region):
    btagCuts = copy.deepcopy(getDefaultCuts(region))
    btagCuts.pop("antibtag")
    return combineCuts(btagCuts)
    
def getAntiBtagComboCut(region):
    antibtagCuts = copy.deepcopy(getDefaultCuts(region))
    antibtagCuts.pop("btag")
    return combineCuts(antibtagCuts)
