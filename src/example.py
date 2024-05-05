import pycdlib
from io import BytesIO
from pathlib import Path

WORKDIR = Path(__file__).parent.parent

ISO_PATH = WORKDIR / 'isos' / 'proxmox.iso'
NEXTSERVER = WORKDIR / 'nextserver'

NEXTSERVER = NEXTSERVER.resolve()
PROXMOX_PXE_ROOT = NEXTSERVER / 'proxmox'

PROXMOX_PXE_ROOT.mkdir(0o0755, parents=True, exist_ok=True)



iso = pycdlib.PyCdlib()

iso.open(ISO_PATH)

iso.get_file_from_iso(PROXMOX_PXE_ROOT / 'vmlimux', rr_path='/boot/linux26')
iso.get_file_from_iso(PROXMOX_PXE_ROOT/'initrd', rr_path='/boot/initrd.img')
iso.get_file_from_iso(PROXMOX_PXE_ROOT/'.cd-info', rr_path='/.cd-info')
iso.get_file_from_iso(PROXMOX_PXE_ROOT/'pve-base.squashfs', rr_path='/base.squashfs')
iso.get_file_from_iso(PROXMOX_PXE_ROOT/'pve-installer.squashfs', rr_path='/installer.squashfs')

