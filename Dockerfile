# Set base image (host OS)
FROM python:3.12-alpine

# By default, listen on port 5000
EXPOSE 5000/tcp

# Set the working directory in the container
WORKDIR /app

COPY startup_docker.sh .
COPY requirements.txt .
# Install any dependencies

RUN apk add --no-cache curl
RUN sh startup_docker.sh
RUN pip install -r requirements.txt

# Copy the content of the local src directory to the working directory
COPY app.py .
COPY llm_retrieval.py .
COPY config.py . 
COPY templates/index.html ./templates/index.html
COPY static/main.css ./static/main.css

# Specify the command to run on container start
CMD [ "python", "./app.py" ]
