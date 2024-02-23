FROM continuumio/miniconda3:23.10.0-1

RUN apt-get update \
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

RUN wget https://github.com/ZarnackGroup/racoon_clip/archive/refs/tags/v1.0.9.zip
RUN unzip v1.0.9.zip

WORKDIR /racoon_clip-1.0.9/ 

RUN conda install --quiet --yes -n base --override-channels -c conda-forge mamba 'python_abi=*=*cp*' && \
    conda create -n racoon_clip python=3.9.2 pip  && \
    echo "conda activate racoon_clip" >> ~/.bashrc
SHELL ["/bin/bash", "--login", "-c"]
ENV PATH /opt/conda/envs/racoon_clip/bin:$PATH

RUN pip install -e .
RUN racoon_clip -h


# WORKDIR /racoon_clip-1.0.8/racoon_clip/workflow/envs
# RUN sed -i '$i\  - pandoc' racoon_R_v0.1.yml
# RUN sed -i '$i\  - r-cairo' racoon_R_v0.1.yml     
