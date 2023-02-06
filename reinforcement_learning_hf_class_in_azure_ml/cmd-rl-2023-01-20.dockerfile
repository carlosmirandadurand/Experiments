#####################################################################################################
# Custom Azure ML Environment cmd-rl-2023-01-20
#####################################################################################################

# This file is a copy of the docker context stored in the Azure ML workspace
# Checked in the repo just for reference
# This commit matches environment cmd-rl-2023-01-20 version 19 (which failed / saving just for reference)


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
# - git and git-lfs
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


# Install Git Large File Storage (git-lfs)
# References:
#  - https://docs.github.com/en/repositories/working-with-files/managing-large-files/installing-git-large-file-storage
#  - https://git-lfs.com/
#  - https://packagecloud.io/github/git-lfs/install 
#  - https://gist.github.com/wpsmith/ae659638f65a810a4fba
# Quick install command for debian:
#   curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | sudo bash
#
# This approach not working: Breaks on the "apt-get git-lfs" command
# RUN curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | bash  && \
#     apt-get git-lfs  && \  
#     git config --global credential.helper store  && \  
#     git lfs install  && \
#     echo "CMD: Installation of base machine Complete"
RUN wget https://github.com/git-lfs/git-lfs/releases/download/v3.3.0/git-lfs-linux-amd64-v3.3.0.tar.gz  && \
    pwd  && \
    ls -al  && \
    echo "CMD: git-lfs download complete, start unzipping"  && \
    tar -xf git-lfs-linux-amd64-v3.3.0.tar.gz  && \
    ls -al  && \
    cd git-lfs-3.3.0  && \
    pwd  && \
    ls -al  && \
    echo "CMD: git-lfs unzip complete, start installation"  && \
    ./install.sh  && \
    cd ..  && \
    pwd  && \
    echo "CMD: git-lfs install complete, start verification" && \  
    git config --global credential.helper store  && \  
    git lfs install  && \ 
    echo "CMD: git-lfs verification and step complete" 


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
RUN pip install --upgrade pip  && \
    pip install azureml-mlflow \
                azure-keyvault-secrets \ 
                azure-identity \ 
                huggingface_hub \ 
                gym[all]


# Needed for 4b:  import gym_pygame  
# Read: 
#   - https://www.pygame.org/wiki/GettingStarted#Pygame%20Installation
#   - https://pypi.org/project/pygame/
#   - https://pypi.org/project/gym-games/   or  https://github.com/qlan3/gym-games/blob/master/README.md
# For:
#    RUN apt-get -y install python-pygame
#    RUN pip install pygame   
# Error:
#    ==> Unable to locate package python-pygame 
#    ==> command '/bin/sh -c apt-get -y install python-pygame' returned a non-zero code: 100
# For:
# RUN echo "CMD: installing gym-games "  && \
#     pip install gym-games  && \
#     echo "CMD: installing pygame "  && \
#     pip install pygame  && \
#     echo "CMD: step complete! "
# Error:
#   ==> Could not find a version that satisfies the requirement ple>=0.0.1 (from gym-games)
RUN echo "CMD: installing gym-games in another way "  && \
    pip install git+https://github.com/qlan3/gym-games.git  && \
    echo "CMD: installing pygame "  && \
    pip install pygame  && \
    echo "CMD: step complete! "


# Add the latest stable build of pythorch 
# (1.13.1 at the time, requiring cuda 11.7)
# https://pytorch.org/get-started/locally/ 
RUN pip3 install torch torchvision torchaudio   && \
    echo "CMD: Installation of Base Machine Complete!"



#################### End of the "base machine" image ####################


# Now start to add the RL project dependencies 
# Old: RUN sudo apt-get install -y xvfb xserver-xephyr tigervnc-standalone-server x11-utils gnumeric
# Old: RUN python3 -m pip install pyvirtualdisplay pillow EasyProcess
RUN apt-get update -y  && \
    apt-get upgrade -y  && \ 
    apt-get install -y \
            python-opengl \
            ffmpeg \
            xvfb   && \
    pip3 install pyvirtualdisplay  &&\
    apt-get install -y \
            swig \
            cmake \
            freeglut3-dev   && \
    pip install pyglet==1.5.1   && \
    pip install imageio \ 
                imageio-ffmpeg


# Final step: Install RL Baselines 3 zoo:
RUN git clone https://github.com/DLR-RM/rl-baselines3-zoo  && \
    cd rl-baselines3-zoo  && \
    pip install -r requirements.txt && \
    cd .. && \
    pwd   && \
    echo "CMD: Installation of RL Packages Complete"


#################### End ####################

