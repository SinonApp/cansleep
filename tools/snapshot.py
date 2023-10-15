from connectors.rtsp import RTSPClient, rtsp_connect
from tools.utils import escape_chars
from connectors.dahua import DahuaController
from connectors.hikvision import HikClient
import time
import os
import av

def _is_video_stream(stream):
    return (
        stream.profile is not None
        and stream.start_time is not None
        and stream.codec_context.format is not None
    )

def rtsp_url_parse(rtsp_url):
    ip, port, login, password = None, None, None, None
    if '@' in rtsp_url:
        login, password = rtsp_url.split('rtsp://')[1].split('@')[0].split(':')
        ip, port = rtsp_url.split('@')[1].split(':')
        ip, port = ip.replace('/', ''), port.replace('/', '')
        return (ip, port, login, password)
    else:
        ip, port = rtsp_url.split('rtsp://')[1].split(':')
        ip, port = ip.replace('/', ''), port.replace('/', '')
        return (ip, port, login, password)    

def rtsp_snapshoter(rtsp_url: str, snapshots_folder, logging, tries=1):
    MAX_SCREENSHOT_TRIES = 2
    try:
        with av.open(
            rtsp_url,
            options={
                "rtsp_transport": "tcp",
                "rtsp_flags": "prefer_tcp",
                "stimeout": "3000000",
            },
            timeout=60.0,
        ) as container:
            stream = container.streams.video[0]
            if _is_video_stream(stream):
                file_name = escape_chars(f"{rtsp_url.lstrip('rtsp://')}.jpg")
                file_path = f'./{snapshots_folder}/{file_name}'

                stream.thread_type = "AUTO"
                for frame in container.decode(video=0):
                    frame.to_image().save(file_path)
                    break
                logging.info(f'[RTSP] Make snapshot from {rtsp_url}')
                return rtsp_url_parse(rtsp_url)
            else:
                # There's a high possibility that this video stream is broken
                # or something else, so we try again just to make sure.
                if tries < MAX_SCREENSHOT_TRIES:
                    logging.debug(f'[RTSP] Failed make snapshoot x{tries} {rtsp_url}')
                    container.close()
                    tries += 1
                    return rtsp_snapshoter(rtsp_url, snapshots_folder, logging, tries=tries)
                else:
                    return
    except (MemoryError, PermissionError, av.InvalidDataError) as e:
        # These errors occur when there's too much SCREENSHOT_THREADS.
        # Try one more time in hope for luck.
        if tries < MAX_SCREENSHOT_TRIES:
            logging.debug(f'[RTSP] Failed make snapshoot x{tries} {rtsp_url}')
            tries += 1
            return rtsp_snapshoter(rtsp_url, snapshots_folder, logging, tries=tries)
        else:
            return
    except Exception as e:
        logging.debug(f'[RTSP] Failed make snapshoot {rtsp_url}')
        logging.debug(f'[RTSP] Error: {e}')
        return


def dahua_snapshoter(target, snapshots_folder, logging):
    if not target: return False
    server_ip, port, login, password, dahua = target

    snapshots_counts = 0
    try:
        dahua = DahuaController(server_ip, int(port), login, password)
        logging.debug("[DAHUA] %s enter to make_snapshots()" % server_ip)
        if dahua.status != 0:
            return False
        channels_count = dahua.channels_count
        model = dahua.model
    except Exception as e:
        logging.info('[DAHUA] Unable to login in cam %s:  %s' % (server_ip, str(e)))
        return False
    
    logging.info(f'[DAHUA] Make snapshot from {server_ip} (DM: {dahua.model}, channels: {channels_count})')
    dead_counter = 0
    for channel in range(channels_count):
    #Ускорение / Perfomance
        if dead_counter > 4:
            logging.info(f'[DAHUA] {dead_counter} dead channels in a row. Skipping this cam')
            break
        try:
            jpeg = dahua.get_snapshot(channel)
        except Exception as e:
            logging.info(f'[DAHUA] Channel {channel + 1} of {server_ip} is dead: {str(e)}')
            dead_counter += 1
            continue
        try:
            outfile = open(os.path.join(snapshots_folder, "%s_%s_%s_%s_%d_%s.jpg" % (server_ip, port, login, password,
                                                                                channel + 1, model.replace('|', ''))), 'wb')
            outfile.write(jpeg)
            outfile.close()
            time.sleep(0.1)
            snapshots_counts += 1
            logging.info(f'[DAHUA] Saved snapshot of {server_ip}, channel {channel + 1}')
            dead_counter = 0
            return (server_ip, port, login, password)
        except Exception as e:
            logging.error('[DAHUA] Cannot save screenshot from %s, channel %s: %s' % (server_ip, channel +1, str(e)))
    logging.debug("[DAHUA] %s exit from make_snapshots()" % server_ip)

def hikka_snapshoter(target, snapshots_folder, logging):
    if not target: return False
    server_ip, port, login, password, hikka = target

    snapshots_counts = 0
    try:
        hikka = HikClient(server_ip, int(port), login, password)
        logging.debug("[HIKKA] %s enter to make_snapshots()" % server_ip)
        if not hikka.connect():
            return False
        channels = hikka.get_count_channels()
    except Exception as e:
        logging.info('[HIKKA] Unable to login in cam %s:  %s' % (server_ip, str(e)))
        return False
    
    logging.info(f'[HIKKA] Make snapshot from {server_ip} (channels: {len(channels)})')
    dead_counter = 0
    for channel in channels:
    #Ускорение / Perfomance
        if dead_counter > 4:
            logging.info(f'[HIKKA] {dead_counter} dead channels in a row. Skipping this cam')
            break
        try:
            jpeg = hikka.get_snapshot(channel)
        except Exception as e:
            logging.info(f'[HIKKA] Channel {channel + 1} of {server_ip} is dead: {str(e)}')
            dead_counter += 1
            continue
        try:
            outfile = open(os.path.join(snapshots_folder, "%s_%s_%s_%s_%d.jpg" % (server_ip, port, login, password,
                                                                                channel)), 'wb')
            for chunk in jpeg.iter_content(chunk_size=1024):
                if chunk:
                    outfile.write(chunk)
            outfile.close()
            time.sleep(0.1)
            snapshots_counts += 1
            logging.info(f'[HIKKA] Saved snapshot of {server_ip}, channel {channel}')
            dead_counter = 0
            return (server_ip, port, login, password)
        except Exception as e:
            logging.error('[HIKKA] Cannot save screenshot from %s, channel %s: %s' % (server_ip, channel +1, str(e)))
    logging.debug("[HIKKA] %s exit from make_snapshots()" % server_ip)
    return (server_ip, port, login, password)
