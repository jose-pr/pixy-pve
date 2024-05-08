from io import BytesIO
from pathlib import Path, PurePosixPath

import pycdlib
import pycdlib.dr
import pycdlib.inode
import pycdlib.rockridge

import pixy_pve
import pycpio
import pycpio.writer
from pycpio.cpio.data import CPIOData
from pycpio.cpio.file import CPIO_File
from pycpio.header.cpioheader import CPIOHeader
from pycpio.masks.modes import CPIOModes

CPIO_ALIGMENT = 512
PIXY_PVE_PATH = Path(pixy_pve.__file__).parent

WORKDIR = Path(__file__).parent.parent

ISO_PATH = WORKDIR / "isos" / "proxmox.iso"
NEXTSERVER = WORKDIR / "nextserver"

NEXTSERVER = NEXTSERVER.resolve()
PROXMOX_PXE_ROOT = NEXTSERVER / "proxmox"

PROXMOX_PXE_ROOT.mkdir(0o0755, parents=True, exist_ok=True)


INITRD = PROXMOX_PXE_ROOT / "initrd"


iso = pycdlib.PyCdlib()
iso.open(ISO_PATH)
iso.get_file_from_iso(PROXMOX_PXE_ROOT / "vmlinuz", rr_path="/boot/linux26")
with INITRD.open("wb") as initrd_fh:
    record: pycdlib.dr.DirectoryRecord = iso.get_record(rr_path="/boot/initrd.img")
    iso.get_file_from_iso_fp(initrd_fh, rr_path="/boot/initrd.img")
    padding = CPIO_ALIGMENT - record.get_data_length() % CPIO_ALIGMENT
    if padding:
        initrd_fh.write(bytes(padding))

    with pycpio.writer.CPIOWriter(initrd_fh) as initrd:
        initrd.write(
            CPIOData.from_dir(
                PIXY_PVE_PATH / "initrd", relative=PIXY_PVE_PATH / "initrd"
            )
        )

        for path in [".cd-info", "pve-base.squashfs", "pve-installer.squashfs"]:
            rr_path = PurePosixPath("/") / path
            buffer = BytesIO()
            iso.get_file_from_iso_fp(buffer, rr_path=rr_path.as_posix())
            entry = CPIO_File(
                buffer.getbuffer(),
                header=CPIOHeader(
                    name=rr_path.name,
                    mode=CPIOModes.File.value | 0o644,
                ),
            )
            initrd.write(entry)
