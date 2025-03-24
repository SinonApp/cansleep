# Cansleep

# !!!The project is not abandoned, as soon as possible we will update and improve it!!!

## Description
Cansleep is a software application developed exclusively for educational purposes. It is designed to analyze and evaluate the functionality and security of urban surveillance cameras, digital video recorders (DVRs), and Real-Time Streaming Protocol (RTSP) video streams. This tool serves as an educational resource for students, researchers, and security professionals interested in understanding the complexities of video surveillance infrastructure.

## Dependencies
For the program to work, you need to install [Nmap](https://nmap.org), [Massan](https://github.com/robertdavidgraham/masscan), [Smap](https://github.com/s0md3v/Smap), [Python3.8](https://www.python.org) or higher

## Warning masscan on windows: [Transmit rate (IMPORTANT!!)](https://github.com/robertdavidgraham/masscan#transmit-rate-important)

## Installation Linux
```bash
# Nmap install
sudo apt install nmap -y

# Masscan install
sudo apt install git make gcc -y \
  && git clone https://github.com/robertdavidgraham/masscan \
  && cd masscan \
  && make \
  && make install
# Or if you use kali linux
sudo apt install masscan -y

# Smap install
sudo apt install golang -y \
  && go install -v github.com/s0md3v/smap/cmd/smap@latest

# Cansleep
git clone https://github.com/SinonApp/cansleep.git \
  && cd cansleep \
  && pip3 install -r requirements.txt
```

## Installation Windows
You need install [Nmap](https://nmap.org)
```
# Cansleep
git clone https://github.com/SinonApp/cansleep.git
cd cansleep
pip3 install -r requirements.txt
```

## Usage
To use the cansleep program, run the following command:
```
sudo python3 cansleep.py [-h] [--target TARGET] [-l LOAD] [-s SCANNER] [-p PORTS] -m MODE [--combo COMBO] [-t THREADS] [-d]
```
# Options
The cansleep program accepts the following options:
```
-h, --help:                    Displays the help message and exits.
--target TARGET:               Specifies the IP address, CIDR range, or file to scan.
-l LOAD, --load LOAD:          Loads a file with a report.txt for skip scanning.
-s SCANNER, --scanner SCANNER: Chooses the scanning tool to use (smap, nmap, or masscan).
-p PORTS, --ports PORTS:       Specifies the ports to scan.
-m MODE, --mode MODE:          Specifies the attack mode to use (all, rtsp, dahua, or hikka).
--combo COMBO:                 Specifies the combo of usernames and passwords to use for brute force attacks.
-t THREADS, --threads THREADS: Specifies the number of threads to use for brute force attacks.
-d, --debug:                   Enables debug logging.
```

# Examples
To scan a single IP address using nmap and the all attack mode:

```
sudo python3 cansleep.py --target 192.168.1.1 -s nmap -m all
```
To scan a CIDR range using masscan and the rtsp attack mode:
```
sudo python3 cansleep.py --target 192.168.1.0/24 -s masscan -m rtsp
```
To scan a file containing a list of IP addresses using smap and the dahua attack
mode:
```
sudo python3 cansleep.py --target ips.txt -s smap -m dahua
```
To perform a brute force attack using a combo of usernames and passwords:

```
sudo python3 cansleep.py --target 192.168.1.1 --combo usernames.txt:passwords.txt -m all -t 10
```
