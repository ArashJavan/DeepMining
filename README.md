## Deep Mining ##

This [project](https://hdi-dai.lids.mit.edu/projects/deep-mining/) is part of the Human Data Interaction project at CSAIL, MIT. The [main repo](https://github.com/HDI-Project/DeepMining) is going through a lot of improvements and will be publicly available soon. This is a fork of the first version.

References:
- [Sample, Estimate, Tune: Scaling Bayesian Auto-Tuning of Data Science Pipelines](https://ieeexplore.ieee.org/document/8259796/)  
Alec Anderson ; Sebastien Dubois ; Alfredo Cuesta-infante ; Kalyan Veeramachaneni  
IEEE International Conference on Data Science and Advance Analytics, 2017
- [Deep Mining: Copula-based Hyper-Parameter Optimization for Machine Learning Pipelines ](http://sds-dubois.github.io/downloads/deepmining_thesis.pdf)  
Sebastien Dubois  - Research thesis


### Overview ###
---------------
The **Deep Mining** project aims at finding the best hyperparameter set for a Machine Learning pipeline. A pipeline example for the [handwritten digit recognition problem](http://yann.lecun.com/exdb/mnist/) is presented below. Some hyperparameters indeed need to be set carefully, as the degree for the polynomial kernel of the SVM. Choosing the value of such hyperparameters can be a very difficult task and this project's goal is to make it much easier.

**This software will test iteratively, and smartly, some hyperparameter sets in order to find as quickly as possible the best ones to achieve the best classification accuracy that a pipeline can offer.**

![Fig2](gcp_hpo/fig/DeepMining_workflow.png?raw=true)


### Methods ###
---------------
The folder **GCP-HPO** contains all the code implementing the **Gaussian Copula Process (GCP)** and a **hyperparameter optimization (HPO)** technique based on it. Gaussian Copula Process can be seen as an improved version of the Gaussian Process, that does not assume a Gaussian prior for the marginal distributions but lies on a more complex prior. This new technique is proved to outperform GP-based hyperparameter optimization, which is already far better than the randomized search.

A paper explaining the GCP approach as well as the hyperparameter process is currently being written and will be linked here as soon as possible. Please consider citing it if you use this work.  


### Contributors ###
-----
- [Sebastien Dubois](http://bit.do/sdubois)
