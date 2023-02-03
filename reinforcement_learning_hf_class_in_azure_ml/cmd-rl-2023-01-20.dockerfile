#####################################################################################################
# Requirements (Collab Project)
#####################################################################################################

# Trying to reproduce a base machine with:
# - Hardware: NVIDIA Tesla T4 GPU + two Intel x86-64 CPUs
# - Hardware Drivers: NVIDIA Driver Version 460.32.03
# - Operating System: Ubuntu 18.04.6 LTS (Bionic Beaver) or 20.04.5 LTS (Focal Fossa)
# - CUDA Version: 11.2
# - python 3.8.16 or Python 3.8.10
# - pytorch 1.13.0 + cu116
# - tensorflow 2.9.2
# - root access
# - some python packages / apt packages (see list)
#
# Then on top of the base machine, I will need to install:
# - !apt install python-opengl
# - !apt install ffmpeg
# - !apt install xvfb
# - !pip3 install pyvirtualdisplay
# - !pip install pyglet==1.5.1
# - !git clone https://github.com/DLR-RM/rl-baselines3-zoo
# - %cd /content/rl-baselines3-zoo/
# - !pip install -r requirements.txt


#####################################################################################################
# New Machine (Azure ML Compute Instance)
#####################################################################################################

# The Standard NV6 compute instance automatically has: 
# - Hardware: NVIDIA Tesla M60 GPU + Six Intel Xeon CPU 
# - Hardware Drivers: NVIDIA Driver Version: 470.141.10   
# - Operating System: Ubuntu 20.04.5 LTS (Focal Fossa)

# And this will change with the base image but for the record, the standard instance also had:
# - CUDA Version: 11.4  
# - Python 3.8.5
# - Tensor Flow 2.2.1
# - pytorch not installed


#####################################################################################################
# New Custom Environment
#####################################################################################################

# Base image from NVIDIA with TF preinstalled: TensorFlow Release 22.12
# https://docs.nvidia.com/deeplearning/frameworks/tensorflow-release-notes/rel-22-12.html#rel-22-12
# Image specs are ahead of the requirements of the project (CUDA 11.8.0 > 11.2,  2.10.1 > 2.9.2), but let's try...
# Image requires NVIDIA Driver release 520 or later; 450.51 (or later R450), 470.57 (or later R470), 510.47 (or later R510), or 515.65 (or later R515).
FROM nvcr.io/nvidia/tensorflow:22.05-tf2-py3


# Commented since the NVIDIA image has the right version of python
# # Install python 3.8.16 
# # RUN apt-get update && \
# #     apt-get install -y software-properties-common && \
# #     add-apt-repository -y ppa:deadsnakes/ppa && \
# #     apt-get update && \
# #     apt install -y python3.8
# # compile python from source - avoid unsupported library problems
# RUN apt update -y && \
#     apt upgrade -y && \ 
#     apt-get install -y wget build-essential checkinstall  libreadline-gplv2-dev  libncursesw5-dev  libssl-dev  libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev libffi-dev zlib1g-dev && \
#     cd /usr/src && \
#     wget https://www.python.org/ftp/python/3.8.16/Python-3.8.16.tgz && \
#     tar xzf Python-3.8.16.tgz && \
#     cd Python-3.8.16 && \
#     ./configure --enable-optimizations && \
#     make altinstall

# Essential python packages
RUN pip install --upgrade pip
RUN pip install azureml-mlflow azure-keyvault-secrets azure-identity huggingface_hub 


# Add the latest stable build of pythorch 
# (1.13.1 at the time, requiring cuda 11.7)
# https://pytorch.org/get-started/locally/ 
RUN pip3 install torch torchvision torchaudio

# End of the "base machine" image... 


# Now start to add the RL project dependencies 
RUN apt-get update -y && \
    apt-get upgrade -y && \ 
    apt-get install -y \
    python-opengl \
    ffmpeg \
    xvfb

RUN pip3 install pyvirtualdisplay
# #RUN sudo apt-get install -y xvfb xserver-xephyr tigervnc-standalone-server x11-utils gnumeric
# #RUN python3 -m pip install pyvirtualdisplay pillow EasyProcess

RUN apt-get install -y \
    swig \
    cmake \
    freeglut3-dev 

RUN pip install pyglet==1.5.1


# Final step: Install RL Baselines 3 zoo:
RUN git clone https://github.com/DLR-RM/rl-baselines3-zoo  && \
    cd rl-baselines3-zoo  && \
    pip install -r requirements.txt

