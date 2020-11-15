# The first instruction is what image we want to base our container on
# We Use an un-official Python runtime as a parent image
FROM m.docker-registry.ir/python:3.6.9

# The enviroment variable ensures that the python output is set straight
# to the terminal with out buffering it first
ENV PYTHONUNBUFFERED 1

# create root directory for our project in the container
RUN mkdir /opt/goldiba/back

# Set the working directory to /opt/goldiba/back/
WORKDIR /opt/goldiba/back

# Copy the current directory contents into the container at /opt/goldiba/back/
ADD . /opt/goldiba/back/

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt