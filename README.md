# rdf_simple
RDataFrame analysis framework for CMS data.
Examples using Displaced Di-photon analysis 
## Quick start
- Set up the environment
  ```
  voms_proxy_init --voms cms --valid 100:00
  source setup.sh
  ```
- Add samples in analysis/ddpSamples.py
- Modify the analysis code in the analysis/ddp.py. The running script is the `analysis()` function 
- Run interactive job in a sample
  ```
  python3 run.py -a VH ZH4G_M30_ctau1000

  ```
- Submit datasets to condor
```
python3 runCondor.py -a VH -o root://cmseos.fnal.gov//store/user/<your username>/analysis  
```
Make sure that you have write access to the EOS area you define with -o . This is where the output files will be stored 

After all the jobs finish running in condor do:

```
rm *condor* sandbox.*  
```

And then you can rerun the runCondor.py command. It will now submit only jobs that failed
After all the jobs are done you can properly merge samples by using the mergeOutput command:
```
python3 mergeOutput.py -o <eos directory>  -a VH -O <local_directory> -y <Years of data taking> -d <primary datasets>
```


