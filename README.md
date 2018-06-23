# PiRanha
PiRanha is the perfect companion of PiPrecious and PiRogue. It is meant to get experiments defined in PiPrecious and run them using a PiRogue. 

## Installation
Install system dependencies:
```
apt-get install adb tcpdump virtualenv -y
```

Clone the project:
```
git clone https://github.com/PiRanhaLysis/PiRanha.git /usr/share/PiRanha
```

Create the Python virtual environment:
```
cd /usr/share/PiRanha
virtualenv venv -p python3
source venv/bin/activate
```

Install Python dependencies:
```
pip install -r requirements.txt
```

## Usage
### Configuration
First of all, you have to create a configuration file `/usr/share/PiRanha/.config` specifying your PiPrecious server and your access token. 
```
# file /usr/share/PiRanha/.config
[DEFAULT]
host = http://localhost:8081
token = my_PiPrecious_access_token
```

### Register a smartphone
```
cd /usr/share/PiRanha
source venv/bin/activate
python piranha/piranha.py -r
```

### Run an experimentation
```
cd /usr/share/PiRanha
source venv/bin/activate
python piranha/piranha.py -l PiPrecious_experiment_ID
```
