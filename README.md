# ServiceX_analyzer
Repo for analyzer code for ServiceX output. 

For now this is a simple Kafka client that just connects to the broker,
consumes messages and deserializes them to awkward arrays.

# How to Build
Build and publish the docker image as:
```bash
% docker build -t sslhep/servicex-analysis:latest .
% docker push sslhep/servicex-analysis:latest
```

# Run inside cluster
There is a standalone pod that can be deployed to Kubernetes that you can
bash into. It has vi installed and a persistent volume to aid debugging.

```bash
% kubectl apply -f kube/dev_volume_pv.yaml
% kubectl apply -f kube/invariant_mass.yaml
```

Once the pod is runing you can open a shell:
```bash
% kubectl exec -it invariant-mass-analysis bash
```

and run the script:
```bash
% python /servicex/invariant_mass.py  --broker servicex-kafka.kafka.svc.cluster.local
```

It will start from the beginning of the servicex topic and print out the
awkward arrays.

# Development of Analyses in Cluster
The Analysis pod has been furnished with a few things to make running and 
debugging analysis more pleasant.

1. vi is installed so you can make quick changes to the script
2. git is installed so you can clone this repo and push commits back and forth
3. The pod has a persistent volume mounted as `/devl` so you can copy plots down to your
workstation, or copy new python files directly into the pod:
```bash
% kubectl cp invariant-mass-analysis:/devl/myplot.png ~/myplot.png
```

# Running as a Job
We have a spec that deploys the analyzer as a job inside the cluster. For 
now it still depends on a read-write-once volume which means only one instance 
of the job pod can run at a time.

To launch the job
```bash
% kubectl apply -f kube/invariant_mass_job.yaml
```

When it runs, it stores the output as text in the persistent volume


