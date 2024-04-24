FROM continuumio/miniconda3:23.10.0-1
FROM condaforge/mambaforge:23.11.0-0

RUN apt clean \
&& apt-get update \
&& apt-get install -yq --no-install-recommends \
	wget \
	unzip \
    git \
    gcc \ 
    g++ \
    libtiff5 \
    python3-pip && \
    apt-get purge && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# RUN wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh
# RUN bash Miniforge3-Linux-x86_64.sh

RUN wget https://github.com/ZarnackGroup/racoon_clip/archive/refs/tags/vVERSION_PLACEHOLDER.zip
RUN unzip vVERSION_PLACEHOLDER.zip

WORKDIR /racoon_clip-VERSION_PLACEHOLDER/ 

# RUN conda install --quiet --yes -n base --override-channels -c conda-forge mamba 'python_abi=*=*cp*' && \
#     conda create --yes -n racoon_clip python=3.9.2 pip botocore  && \
#     echo "conda activate racoon_clip" >> ~/.bashrc
# SHELL ["/bin/bash", "--login", "-c"]
# ENV PATH /opt/conda/envs/racoon_clip/bin:$PATH

WORKDIR /racoon_clip-VERSION_PLACEHOLDER/racoon_clip.egg-info
RUN sed -i -e 's/snakemake>=7.22/snakemake==7.29.0/g' requires.txt
#RUN sed -i '1s/^/pulp==2.7.0 /' requires.txt
RUN pip install pulp==2.7.0
#RUN pip install botocore

WORKDIR /racoon_clip-VERSION_PLACEHOLDER/
RUN pip install -e .
RUN racoon_clip -h



# WORKDIR /racoon_clip-VERSION_PLACEHOLDER/racoon_clip/minimal_examples
# RUN unzip minimal_example_eCLIP.zip


# WORKDIR /racoon_clip-1.0.8/racoon_clip/workflow/envs
# RUN sed -i '$i\  - pandoc' racoon_R_v0.1.yml
# RUN sed -i '$i\  - r-cairo' racoon_R_v0.1.yml     
