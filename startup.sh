python3 -m venv ollama_env

## Download required packages
source ollama_env/bin/activate
pip install -r requirements.txt

## Download the raw data
mkdir data
curl -L https://raw.githubusercontent.com/beandog/lds-scriptures/master/text/lds-scriptures.txt > data/scriptures.txt



