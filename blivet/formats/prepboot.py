# prepboot.py
# Format class for PPC PReP Boot.
#
# Copyright (C) 2009  Red Hat, Inc.
#
# This copyrighted material is made available to anyone wishing to use,
# modify, copy, or redistribute it subject to the terms and conditions of
# the GNU General Public License v.2, or (at your option) any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY expressed or implied, including the implied warranties of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License for more details.  You should have received a copy of the
# GNU General Public License along with this program; if not, write to the
# Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.  Any Red Hat trademarks that are incorporated in the
# source code or documentation are not subject to the GNU General Public
# License and may only be used or replicated with the express permission of
# Red Hat, Inc.
#
# Red Hat Author(s): Dave Lehman <dlehman@redhat.com>
#

from ..size import Size
from .. import platform
from ..i18n import N_
from . import DeviceFormat, register_device_format
from ..threads import KEY_ABSENT
from parted import PARTITION_PREP
import os
import logging
log = logging.getLogger("blivet")

class PPCPRePBoot(DeviceFormat):
    """ Generic device format. """
    _type = "prepboot"
    _name = N_("PPC PReP Boot")
    partedFlag = PARTITION_PREP
    _formattable = True                 # can be formatted
    _linuxNative = True                 # for clearpart
    _maxSize = Size("10 MiB")
    _minSize = Size("4 MiB")

    def __init__(self, **kwargs):
        """
            :keyword device: path to block device node
            :keyword exists: whether this is an existing format
            :type exists: bool

            .. note::

                The 'device' kwarg is required for existing formats. For non-
                existent formats, it is only necessary that the :attr:`device`
                attribute be set before the :meth:`create` method runs. Note
                that you can specify the device at the last moment by specifying
                it via the 'device' kwarg to the :meth:`create` method.
        """
        DeviceFormat.__init__(self, **kwargs)

    def _setCreateEventInfo(self):
        self.eventSync.info_update(ID_FS_TYPE=KEY_ABSENT)

    def _create(self, **kwargs):
        super(PPCPRePBoot, self)._create(**kwargs)
        try:
            fd = os.open(self.device, os.O_RDWR)
            length = os.lseek(fd, 0, os.SEEK_END)
            os.lseek(fd, 0, os.SEEK_SET)
            buf = '\0' * 1024 * 1024
            while length > 0:
                if length >= len(buf):
                    os.write(fd, buf)
                    length -= len(buf)
                else:
                    buf = '\0' * length
                    os.write(fd, buf)
                    length = 0
        except OSError as e:
            log.error("error zeroing out %s: %s", self.device, e)
        finally:
            if fd:
                os.close(fd)

    @property
    def status(self):
        return False

    @property
    def supported(self):
        return isinstance(platform.platform, platform.IPSeriesPPC)

register_device_format(PPCPRePBoot)

