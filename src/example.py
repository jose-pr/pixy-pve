import pycdlib, pycpio
from io import BytesIO
from pathlib import Path

import pixy_pve

CPIO_ALIGMENT = 512
PIXY_PVE_PATH = Path(pixy_pve.__file__).parent

WORKDIR = Path(__file__).parent.parent

ISO_PATH = WORKDIR / "isos" / "proxmox.iso"
NEXTSERVER = WORKDIR / "nextserver"

NEXTSERVER = NEXTSERVER.resolve()
PROXMOX_PXE_ROOT = NEXTSERVER / "proxmox"

PROXMOX_PXE_ROOT.mkdir(0o0755, parents=True, exist_ok=True)


INITRD = PROXMOX_PXE_ROOT / "initrd"


initrd = pycpio.PyCPIO()
initrd.append_recursive(PIXY_PVE_PATH / "initrd", relative=PIXY_PVE_PATH / "initrd")

iso = pycdlib.PyCdlib()

iso.open(ISO_PATH)


iso.get_file_from_iso(PROXMOX_PXE_ROOT / ".cd-info", rr_path="/.cd-info")
iso.get_file_from_iso(PROXMOX_PXE_ROOT / "base.squashfs", rr_path="/pve-base.squashfs")
iso.get_file_from_iso(
    PROXMOX_PXE_ROOT / "installer.squashfs", rr_path="/pve-installer.squashfs"
)
iso.get_file_from_iso(PROXMOX_PXE_ROOT / "vmlinuz", rr_path="/boot/linux26")

#
# Extract initrd and append to it
#
initrd_fh = BytesIO()
iso.get_file_from_iso_fp(initrd_fh, rr_path="/boot/initrd.img")
padding = CPIO_ALIGMENT - initrd_fh.getbuffer().nbytes % CPIO_ALIGMENT
if padding:
    initrd_fh.write(bytes(padding))
added = initrd_fh.getbuffer().nbytes
initrd.write_fp(initrd_fh)
added = initrd_fh.getbuffer().nbytes - added
print(added)
initrd_fh.seek(0)
INITRD.write_bytes(initrd_fh.read())
