FROM ubuntu:18.04
MAINTAINER Ben Shealy <btsheal@g.clemson.edu>

# install dependencies
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update -qq \
	&& apt-get install -qq -y libopenmpi-dev python3-pip r-base ssh \
	&& pip3 install -q matplotlib mpi4py numpy pandas scikit-learn seaborn

# initialize default work directory
WORKDIR /workspace
