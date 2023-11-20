import subprocess
import ROOT

def load_meta_data(data):
    #Declare dataframe
    dataframe =ROOT.RDataFrame(data)
    #read the HLT string from the sample
    dataframe=dataframe.DefinePerSample('HLTstring','rdfsampleinfo_.GetS("trigger")')
    dataframe=dataframe.Define('HLT_passed','HLTstring.data()')
    #Check if it is MC
    dataframe=dataframe.DefinePerSample('sample_isMC','rdfsampleinfo_.GetI("isMC")')
    #get the list of meta keys
    meta_keys =data.GetMetaData()[0].GetS('meta_keys').split(',')
    for key in meta_keys:
        dataframe=dataframe.DefinePerSample('sample_'+key,'rdfsampleinfo_.GetD("{}")'.format(key))
    return dataframe


def loadSample(info,locator='root://cms-xrd-global.cern.ch//'):
    files=[]
    print(info['dataset'])
    p = subprocess.Popen('/cvmfs/cms.cern.ch/common/dasgoclient -dasmaps=./ -query="file dataset={}"'.format(info['dataset']), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in p.stdout.readlines():
        files.append(locator+(line.decode('ASCII').split('\n')[0]))
    retval = p.wait()
    triggerStr=[]
    for t in info['triggers']:
        triggerStr.append('{}==1'.format(t))
    for t in info['veto_triggers']:
        triggerStr.append('{}==0'.format(t))
    triggerDecision = '&&'.join(triggerStr)

    metaData = ROOT.RDF.Experimental.RMetaData()
    metaData.Add('trigger',triggerDecision)

    if 'SIM' in info['dataset']:
        metaData.Add('isMC',1)
    else:
        metaData.Add('isMC',0)
    # add custom user meta data e.g sigma or weights- assume float for now
    meta_keys=[]
    for tag, data in info.items():
        if tag not in ['dataset','triggers','veto_triggers']:
            metaData.Add(tag,float(data))
            meta_keys.append(tag)
    #add the list of keys as a new meta data entry (string)
    metaData.Add('meta_keys',','.join(meta_keys))    
    sample = ROOT.RDF.Experimental.RSample(info['dataset'],'Events',files,metaData)
    return sample


def createDataSet(samples,locator='root://cms-xrd-global.cern.ch//'):
    spec = ROOT.RDF.Experimental.RDatasetSpec()
    for s in samples:
        sl = loadSample(s,locator)
        spec.AddSample(sl)

    return spec
        