import requests
import lzma
from frida_android_helper.utils import *


FRIDA_INSTALL_DIR = "/data/local/tmp/"
FRIDA_BIN_NAME = "frida-server"
# FRIDA_LATEST_RELEASE_URL = "https://api.github.com/repos/frida/frida/releases/latest"
FRIDA_VERSION = "14.2.17"


def download_latest_frida(device: Device):
    # latest_release = requests.get(FRIDA_LATEST_RELEASE_URL).json()
    arch = get_architecture(device)
    release_name = "frida-server-{}-android-{}.xz".format(FRIDA_VERSION, arch)
    download_url = "https://github.com/frida/frida/releases/download/{}/{}".format(FRIDA_VERSION, release_name)
    eprint("⚡ Downloading {}...".format(download_url))
    xz_file = requests.get(download_url)
    eprint("⚡ Extracting {}...".format(release_name))
    server_binary = lzma.decompress(xz_file.content)
    eprint("⚡ Writing {}...".format(release_name))
    with open(release_name[:-3], "wb") as f:  # remove extension
        f.write(server_binary)
    return release_name[:-3]


def launch_frida_server(device: Device):
    # hack: launch server, "forever sleep" and put in background. Short timeout to break off connection
    perform_cmd(device, "{}{} && sleep 2147483647 &".format(FRIDA_INSTALL_DIR, FRIDA_BIN_NAME), root=True, timeout=1)


def start_server():
    eprint("⚡️ Starting frida-server")
    devices = get_devices()
    for device in devices:
        eprint("📲 Device: {} ({})".format(get_device_model(device), device.get_serial_no()))
        launch_frida_server(device)


def stop_server():
    eprint("⚡️ Stopping frida-server")
    devices = get_devices()
    for device in devices:
        eprint("📲 Device: {} ({})".format(get_device_model(device), device.get_serial_no()))
        perform_cmd(device, "pkill frida-server", True)


def reboot_server():
    eprint("⚡️ Rebooting frida-server")
    stop_server()
    start_server()


def update_server():
    eprint("⚡️ Updating frida-server")
    devices = get_devices()
    for device in devices:
        eprint("📲 Device: {} ({})".format(get_device_model(device), device.get_serial_no()))
        server_binary = download_latest_frida(device)
        device.push(server_binary, "{}{}".format(FRIDA_INSTALL_DIR, FRIDA_BIN_NAME), 755)
        launch_frida_server(device)
