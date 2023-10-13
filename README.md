# Cansleep

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

## Roadmap
- [x] Version 1.0.0 (Current Version):
__Feature Set Consolidation: This version focuses on consolidating the existing feature set, including network device scanning, authentication testing, and RTSP video stream quality testing. Enhance user experience and fix any known issues.__

- [ ] Version 1.1.0:
__Adding New Scanners: In this release, we will introduce support for additional scanners and detection techniques, improving the tool's ability to identify a wider range of devices and vulnerabilities.__

- [ ] Version 1.2.0:
__New Protocols and Camera Vendors: Expand the tool's capabilities by adding support for new protocols beyond RTSP, and integrate compatibility with a broader array of camera vendors, including their specific functionalities.__

- [ ] Version 1.3.0:
__In this release, we will integrate exploits. This enhancement will empower the tool to identify and exploit a wider range of security weaknesses, contributing to a more comprehensive assessment of target systems.__

- [ ] Version 1.4.0:
__Generating Reports in Many Formats: In this release, we will introduce the functionality to generate comprehensive reports in various formats, such as PDF, HTML, and JSON, making it easier for users to analyze and share the results of their scans.__

- [ ] Version 2.0.0:
__Enhanced User Interface: This major update will focus on improving the user interface to make the tool more user-friendly and intuitive. It will involve revamping the graphical interface, enhancing user interactions, and providing a more seamless experience.__

- [ ] Version 2.1.0:
__Advanced Vulnerability Assessment: Expand the tool's capabilities to perform in-depth vulnerability assessments and penetration testing on detected devices, including running specific exploits or checks.__

- [ ] Version 2.2.0:
__Integration with Security Databases: Implement integration with security vulnerability databases and threat intelligence feeds to provide real-time information on known vulnerabilities associated with detected devices.__
