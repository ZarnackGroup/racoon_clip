FROM condaforge/miniforge3:25.3.1-0
#FROM condaforge/mambaforge:22.9.0-2
#FROM condaforge/mambaforge:4.14.0-2
#

# Set timezone to avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

RUN apt clean \
&& apt-get update \
&& apt-get install -yq --no-install-recommends \
	wget \
	unzip \
    git \
    gcc \ 
    g++ \
    libtiff-dev \
    libarchive-tools \
    libarchive-dev && \
    ldconfig && \
    apt-get purge && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Get python 3.9 with miniforge (mamba already included)
##################################

# Install exact Python 3.9.0 using mamba (already available in miniforge)
RUN mamba install -c conda-forge python=3.9.0 pip -y && mamba clean -afy

# Check installed Python version
RUN echo "Python version:" && python --version && python -c "import sys; print(f'Exact version: {sys.version}')"

# check mamba is available
RUN mamba --version

# Get racoon_clip
##################################

RUN wget https://github.com/ZarnackGroup/racoon_clip/archive/refs/tags/v.1.3.0.zip
RUN unzip v.1.3.0.zip

WORKDIR /racoon_clip-v.1.3.0/ 

# Install racoon_clip directly in the base environment
RUN pip install --verbose -e . && \
    pip show racoon_clip

# Test racoon_clip installation
##############################

# Test racoon_clip installation (installed in base environment)
RUN racoon_clip -h
RUN racoon_clip test --light

# Set default entrypoint
CMD ["/bin/bash"]




# WORKDIR /racoon_clip-1.3.0/racoon_clip/minimal_examples
# RUN unzip minimal_example_eCLIP.zip


# WORKDIR /racoon_clip-1.0.8/racoon_clip/workflow/envs
# RUN sed -i '$i\  - pandoc' racoon_R_v0.1.yml
# RUN sed -i '$i\  - r-cairo' racoon_R_v0.1.yml     
