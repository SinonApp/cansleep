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


## Contributing
We welcome contributions to the Cansleep project from individuals who are passionate about enhancing the tool's functionality, security, and educational value. Your contributions can help make this project even more valuable for educational and research purposes. Here's how you can get involved:

1. Reporting Issues:
If you come across any bugs, vulnerabilities, or issues in the tool, please open a new issue on the project's GitHub repository. Be sure to provide a detailed description of the problem, including steps to reproduce it, and any relevant system information.

2. Feature Requests:
If you have ideas for new features or improvements to the tool, feel free to create a feature request on the GitHub repository. Provide a clear description of the feature and its potential benefits.

3. Code Contributions:
If you are a developer and would like to contribute code to the project, we encourage you to submit pull requests. Follow these guidelines when making contributions:

- Fork the repository and create a new branch for your changes.
- Ensure your code adheres to the project's coding standards.
- Include tests for new features and fixes.
- Provide clear documentation for any new functionality.

4. Documentation:
Improving documentation is always valuable. If you can enhance the project's documentation by adding more details, guides, or examples, please submit documentation-related pull requests.

5. Testing:
Help test the tool on different platforms and provide feedback on its performance. This includes testing compatibility with various operating systems, network environments, and camera systems.

6. Security:
If you discover security vulnerabilities or issues that could impact the security of the tool, please follow responsible disclosure practices and contact the project maintainers privately before disclosing them publicly.

7. Support and Discussion:
Engage with the project's community by participating in discussions, answering questions, and helping other users. This can be done through the project's issue tracker and forums.

Getting Started:
Before making any contributions, please review the project's contribution guidelines and code of conduct. These guidelines provide important information on how to contribute, maintain a positive and inclusive environment, and adhere to ethical practices.

By contributing to the Cansleep, you are playing a vital role in improving the educational resources and security of urban surveillance systems. We appreciate your support and look forward to your valuable contributions.

Thank you for being a part of this educational and security-focused community!
