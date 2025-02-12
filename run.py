import ROOT
import importlib
#Enable multi-threading
#ROOT.ROOT.EnableImplicitMT()
#ROOT.ROOT.DisableImplicitMT()
ROOT.gInterpreter.Declare('#include "common/chelpers.h"')
from common.pyhelpers import *
from optparse import OptionParser





parser = OptionParser()
parser.add_option("-a", "--analysis", dest="analysis",
                  help="Split the sample in N sub samples",type='str',default='VH')
parser.add_option("-s", "--splitFactor", dest="splitFactor",
                  help="Split the sample in N sub samples",type='int',default=0)
parser.add_option("-p", "--processPart", dest="processPart",
                  help="process the i-th sample if you decide to split ",type='int',default=0)
(options, args) = parser.parse_args()



an = importlib.import_module('analysis.{}'.format(options.analysis))
samp = importlib.import_module('analysis.{}samples'.format(options.analysis))
#root://xrootd-cms.infn.it//
#root://cmsxrootd.fnal.gov//
actions=[]
for sample in args:
    data=createDataSet(samp.samples[sample],options.splitFactor,options.processPart,'root://cmsxrootd.fnal.gov//')
    actions.extend(an.analysis(data,sample))
ROOT.RDF.RunGraphs(actions)

