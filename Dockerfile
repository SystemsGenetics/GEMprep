FROM ubuntu:18.04
MAINTAINER Ben Shealy <btsheal@clemson.edu>

# install dependencies
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update -qq \
	&& apt-get install -qq -y mpich python3-pip r-base ssh \
	&& pip3 install -q matplotlib mpi4py numpy pandas scikit-learn seaborn

# install R packages
COPY scripts/install-deps.R .

RUN Rscript install-deps.R \
	&& rm -f install-deps.R

# initialize default work directory
WORKDIR /workspace
