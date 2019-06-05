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
bash into. It has vi installed to aid debugging.

```bash
% kubectl apply -f kube/invariant_mass.yaml
```

Once the pod is runing you can open a shell and run the script:
```bash
% kubectl exec -it invariant-mass-analysis bash
% python /servicex/invariant_mass.py  --broker servicex-kafka.kafka.svc.cluster.local
```

It will start from the beginning of the servicex topic and print out the
awkward arrays.


