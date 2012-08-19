# -*- coding:utf-8 -*-
#
# Copyright (C) 2012, Maximilian Köhl <linuxmaxi@googlemail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import ctypes
import ctypes.util
import errno
import functools
import logging
import platform
import stat
import traceback

__author__ = 'Maximilian Köhl'
__copyright__ = 'Copyright (C) 2012, Maximilian Köhl'
__license__ = 'GPLv3'
__version__ = '0.0.1'
__status__ = 'Development'
__all__ = ['Operations', 'FUSE']

_library = ctypes.util.find_library('fuse')
if not _library:
    raise ImportError('No library named fuse')

_fuse = ctypes.CDLL(_library)

_formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
_stream = logging.StreamHandler()
_stream.setFormatter(_formatter)
_logger = logging.getLogger('fuse')
_logger.addHandler(_stream)

def _function(name, result, args):
    func = getattr(_fuse, name)
    func.restype = result
    func.argtypes = args
    return func

def _struct(*fields):
    class _Struct(ctypes.Structure):
        _fields_ = list(fields)
    return _Struct

_c_timespec = _struct(('tv_sec', ctypes.c_long), ('tv_nsec', ctypes.c_long))
_c_utimbuf = _struct(('actime', _c_timespec), ('modtime', _c_timespec))

_setxattr_t = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_byte), ctypes.c_size_t, ctypes.c_int)
_getxattr_t = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_byte), ctypes.c_size_t)

if platform.machine() == 'x86_64':
    _c_stat = _struct(('st_dev', ctypes.c_ulonglong),
                      ('st_ino', ctypes.c_ulong),
                      ('st_nlink', ctypes.c_ulong),
                      ('st_mode', ctypes.c_uint),
                      ('st_uid', ctypes.c_uint),
                      ('st_gid', ctypes.c_uint),
                      ('__pad0', ctypes.c_int),
                      ('st_rdev', ctypes.c_ulonglong),
                      ('st_size', ctypes.c_longlong),
                      ('st_blksize', ctypes.c_long),
                      ('st_blocks', ctypes.c_long),
                      ('st_atimespec', _c_timespec),
                      ('st_mtimespec', _c_timespec),
                      ('st_ctimespec', _c_timespec))
else:
    _c_stat = _struct(('st_dev', ctypes.c_ulonglong),
                      ('st_ino', ctypes.c_ulonglong),
                      ('st_mode', ctypes.c_uint),
                      ('st_nlink', ctypes.c_uint),
                      ('st_uid', ctypes.c_uint),
                      ('st_gid', ctypes.c_uint),
                      ('st_rdev', ctypes.c_ulonglong),
                      ('__pad2', ctypes.c_ushort),
                      ('st_size', ctypes.c_longlong),
                      ('st_blksize', ctypes.c_long),
                      ('st_blocks', ctypes.c_longlong),
                      ('st_atimespec', _c_timespec),
                      ('st_mtimespec', _c_timespec),
                      ('st_ctimespec', _c_timespec))

_c_statvfs = _struct(('f_bsize', ctypes.c_ulong),
                     ('f_frsize', ctypes.c_ulong),
                     ('f_blocks', ctypes.c_ulonglong),
                     ('f_bfree', ctypes.c_ulonglong),
                     ('f_bavail', ctypes.c_ulonglong),
                     ('f_files', ctypes.c_ulonglong),
                     ('f_ffree', ctypes.c_ulonglong),
                     ('f_favail', ctypes.c_ulonglong))

_fuse_file_info = _struct(('flags', ctypes.c_int),
                          ('fh_old', ctypes.c_ulong),
                          ('writepage', ctypes.c_int),
                          ('direct_io', ctypes.c_uint, 1),
                          ('keep_cache', ctypes.c_uint, 1),
                          ('flush', ctypes.c_uint, 1),
                          ('padding', ctypes.c_uint, 28),
                          ('fh', ctypes.c_uint64),
                          ('lock_owner',ctypes. c_uint64))

_fuse_operations = _struct(('getattr', ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_char_p, ctypes.POINTER(_c_stat))),
                           ('readlink', ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_char_p, ctypes.POINTER(ctypes.c_byte), ctypes.c_size_t)),
                           ('getdir',  ctypes.c_voidp),
                           ('mknod', ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_char_p, ctypes.c_uint, ctypes.c_ulonglong)),
                           ('mkdir', ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_char_p, ctypes.c_uint)),
                           ('unlink', ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_char_p)),
                           ('rmdir', ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_char_p)),
                           ('symlink', ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p)),
                           ('rename', ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p)),
                           ('link', ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p)),
                           ('chmod', ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_char_p, ctypes.c_uint)),
                           ('chown', ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_char_p, ctypes.c_uint, ctypes.c_uint)),
                           ('truncate', ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_char_p, ctypes.c_longlong)),
                           ('utime', ctypes.c_voidp),
                           ('open', ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_char_p, ctypes.POINTER(_fuse_file_info))),
                           ('read', ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_char_p, ctypes.POINTER(ctypes.c_byte), ctypes.c_size_t, ctypes.c_longlong, ctypes.POINTER(_fuse_file_info))),
                           ('write', ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_char_p, ctypes.POINTER(ctypes.c_byte), ctypes.c_size_t, ctypes.c_longlong, ctypes.POINTER(_fuse_file_info))),
                           ('statfs', ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_char_p, ctypes.POINTER(_c_statvfs))),
                           ('flush', ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_char_p, ctypes.POINTER(_fuse_file_info))),
                           ('release', ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_char_p, ctypes.POINTER(_fuse_file_info))),
                           ('fsync', ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.POINTER(_fuse_file_info))),
                           ('setxattr', _setxattr_t),
                           ('getxattr', _getxattr_t),
                           ('listxattr', ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_char_p, ctypes.POINTER(ctypes.c_byte), ctypes.c_size_t)),
                           ('removexattr', ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p)),
                           ('opendir', ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_char_p, ctypes.POINTER(_fuse_file_info))),
                           ('readdir', ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_char_p, ctypes.c_voidp, ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_voidp, ctypes.c_char_p, ctypes.POINTER(_c_stat), ctypes.c_longlong), ctypes.c_longlong, ctypes.POINTER(_fuse_file_info))),
                           ('releasedir', ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_char_p, ctypes.POINTER(_fuse_file_info))),
                           ('fsyncdir', ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.POINTER(_fuse_file_info))),
                           ('init', ctypes.CFUNCTYPE(ctypes.c_voidp, ctypes.c_voidp)),
                           ('destroy', ctypes.CFUNCTYPE(ctypes.c_voidp, ctypes.c_voidp)),
                           ('access', ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_char_p, ctypes.c_int)),
                           ('create', ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_char_p, ctypes.c_uint, ctypes.POINTER(_fuse_file_info))),
                           ('ftruncate', ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_char_p, ctypes.c_longlong, ctypes.POINTER(_fuse_file_info))),
                           ('fgetattr', ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_char_p, ctypes.POINTER(_c_stat), ctypes.POINTER(_fuse_file_info))),
                           ('lock', ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_char_p, ctypes.POINTER(_fuse_file_info), ctypes.c_int, ctypes.c_voidp)),
                           ('utimens', ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_char_p, ctypes.POINTER(_c_utimbuf))),
                           ('bmap', ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_char_p, ctypes.c_size_t, ctypes.POINTER(ctypes.c_ulonglong))))                        

_fuse_main_real = _function('fuse_main_real', ctypes.c_int, [ctypes.c_int, ctypes.Array, ctypes.POINTER(_fuse_operations), ctypes.c_int, ctypes.c_void_p])

def _timespec_to_time(timespec):
    return timespec.tv_sec + timespec.tv_nsec / 10 ** 9

def _stat_set_attributes(stat, **kwargs):
    for key, value in kwargs.items():
        if key in ('st_atime', 'st_mtime', 'st_ctime'):
            timespec = getattr(stat, key + 'spec')
            timespec.tv_sec = int(value)
            timespec.tv_nsec = int((value - timespec.tv_sec) * 10 ** 9)
        elif hasattr(stat, key):
            setattr(stat, key, value)

class Operations():
    def getattr(self, path):
        '''
        Get file attributes.
        
        Similar to stat(). The 'st_dev' and 'st_blksize' fields are
        ignored. The 'st_ino' field is ignored except if the 'use_ino'
        mount option is given.
        
        Should return a dictionary mapping stat attributes to values.
        '''
        if path == '/':
            return {'st_mode': stat.S_IFDIR  | 0o755, 'st_link': 2}
        raise OSError(errno.ENOENT, '')
    
    def readlink(self, path):
        '''
        Read the target of a symbolic link.
        
        Should return the target of the symbolic link as a string.
        '''
        raise OSError(errno.ENOENT, '')


    def mknod(self, path, mode, dev):
        '''
        Create a file node.
        
        This is called for creation of all non-directory, non-symlink
        nodes. If the filesystem defines a create() method, then for
        regular files that will be called instead.
        '''
        raise OSError(errno.EROFS, '')
    
    def mkdir(self, path, mode):
        '''
        Create a directory.

        Note that the mode argument may not have the type specification
        bits set, i.e. S_ISDIR(mode) can be false. To obtain the
        correct directory type bits use mode|S_IFDIR.
        '''
        raise OSError(errno.EROFS, '')
    
    def unlink(self, path):
        ''' 
        Remove a file.
        '''
        raise OSError(errno.EROFS, '')
    
    def rmdir(self, path):
        '''
        Remove a directory.
        '''
        raise OSError(errno.EROFS, '')
    
    def symlink(self, target, source):
        '''
        Create a symbolic link.
        '''
        raise OSError(errno.EROFS, '')
    
    def rename(self, source, target):
        '''
        Rename a file.
        '''
        raise OSError(errno.EROFS, '')
    
    def link(self, target, source):
        '''
        Create a hard link to a file.
        '''
        raise OSError(errno.EROFS, '')
    
    def chmod(self, path, mode):
        '''
        Change the permission bits of a file.
        '''
        raise OSError(errno.EROFS, '')
    
    def chown(self, path, uid, gid):
        '''
        Change the owner and group of a file.
        '''
        raise OSError(errno.EROFS, '')
    
    def truncate(self, path, offset):
        '''
        Change the size of a file.
        '''
        raise OSError(errno.EROFS, '')
    
    def open(self, path, flags):
        '''
        File open operation.
    
        No creation (O_CREAT, O_EXCL) and by default also no
        truncation (O_TRUNC) flags will be passed to open(). If an
        application specifies O_TRUNC, fuse first calls truncate()
        and then open(). Only if 'atomic_o_trunc' has been
        specified and kernel version is 2.6.24 or later, O_TRUNC is
        passed on to open.
        
        Unless the 'default_permissions' mount option is given,
        open should check if the operation is permitted for the
        given flags. 
        
        Should return a file handle.
        '''
        return 0
    
    def read(self, path, size, offset, file_handle):
        '''
        Read data from an open file.
        
        Read should return exactly the number of bytes requested except
        on EOF or error, otherwise the rest of the data will be
        substituted with zeroes. An exception to this is when the
        'direct_io' mount option is specified, in which case the return
        value of the read system call will reflect the return value of
        this operation.
        
        Should return a byte string with the data.
        '''
        raise OSError(errno.ENOENT, '')
    
        
    def write(self, path, data, size, offset, file_handle):
        '''
        Write data to an open file

        Write should return exactly the number of bytes requested
        except on error. An exception to this is when the 'direct_io'
        mount option is specified (see read operation).
        '''
        raise OSError(errno.EROFS, '')
    
    def statfs(self, path):
        '''
        Get file system statistics
        
        The 'f_frsize', 'f_favail', 'f_fsid' and 'f_flag' fields are ignored.
        
        Should return a dictionary.
        '''
        return {}
    
    def flush(self, path, file_handle):
        '''
        Possibly flush cached data

        BIG NOTE: This is not equivalent to fsync(). It's not a
        request to sync dirty data.

        Flush is called on each close() of a file descriptor. So if a
        filesystem wants to return write errors in close() and the file
        has cached dirty data, this is a good place to write back data
        and return any errors. Since many applications ignore close()
        errors this is not always useful.

        NOTE: The flush() method may be called more than once for each
        open(). This happens if more than one file descriptor refers
        to an opened file due to dup(), dup2() or fork() calls. It is
        not possible to determine if a flush is final, so each flush
        should be treated equally. Multiple write-flush sequences are
        relatively rare, so this shouldn't be a problem.
        
        Filesystems shouldn't assume that flush will always be called
        after some writes, or that if will be called at all.
        '''
        return 0
    
    def release(self, path, file_handle):
        '''
        Release an open file.

        Release is called when there are no more references to an open
        file: all file descriptors are closed and all memory mappings
        are unmapped.

        For every open() call there will be exactly one release() call
        with the same flags and file descriptor. It is possible to
        have a file opened more than once, in which case only the last
        release will mean, that no more reads/writes will happen on the
        file. The return value of release is ignored.
        '''
        return 0
    
    def fsync(self, path, datasync, file_handle):
        '''
        Synchronize file contents.
        
        If the datasync parameter is non-zero, then only the user data
        should be flushed, not the meta data.
        '''
        return 0
    
    def setxattr(self, path, name, value, options):
        '''
        Set extended attributes.
        '''
        raise OSError(errno.ENOTSUP, '')
    
    def getxattr(self, path, name):
        '''
        Get extended attributes.
        '''
        raise OSError(errno.ENOTSUP, '')
    
    def listxattr(self, path):
        '''
        List extended attributes.
        
        Should return a dictionary mapping names to values.
        '''
        return {}
    
    def removexattr(self, path, name):
        '''
        Remove extended attributes.
        '''
        raise OSError(errno.ENOTSUP, '')
    
    def opendir(self, path):
        '''
        Open directory.

        Unless the 'default_permissions' mount option is given,
        this method should check if opendir is permitted for this
        directory.
        
        Should return a file_handle.
        '''
        return 0
    
    def readdir(self, path, file_handle):
        '''
        Read directory.
        
        This supersedes the old getdir() interface. New applications
        should use this.
        
        Should return a list with dirs and files.
        '''
        return ['.', '..']
    
    def releasedir(self, path, file_handle):
        '''
        Release directory.
        '''
        return 0
    
    def fsyncdir(self, path, datasync, file_handle):
        '''
        Synchronize directory contents.

        If the datasync parameter is non-zero, then only the user data
        should be flushed, not the meta data.
        '''
        return 0
    
    def init(self):
        '''
        Initialize filesystem.
        '''
        pass
    
    def destroy(self):
        '''
        Clean up filesystem.
        
        Called on filesystem exit.
        '''
        pass
    
    def access(self, path, mode):
        '''
        Check file access permissions
        
        This will be called for the access() system call. If the
        'default_permissions' mount option is given, this method is not
        called.
        
        This method is not called under Linux kernel versions 2.4.x.
        '''
        return 0
    
    def create(self, path, mode):
        '''
        Create and open a file

        If the file does not exist, first create it with the specified
        mode, and then open it.

        If this method is not implemented or under Linux kernel
        versions earlier than 2.6.15, the mknod() and open() methods
        will be called instead.
        
        Should return a file handle.
        '''
        raise OSError(errno.EROFS, '')
    
    def ftruncate(self, path, offset, file_handle):
        '''
        Change the size of an open file

        This method is called instead of the truncate() method if the
        truncation was invoked from an ftruncate() system call.
        
        If this method is not implemented or under Linux kernel
        versions earlier than 2.6.15, the truncate() method will be
        called instead.
        '''
        raise OSError(errno.EROFS, '')

    def fgetattr(self, path, file_handle):
        '''
        Get attributes from an open file.
        
        This method is called instead of the getattr() method if the
        file information is available.
        
        Currently this is only called after the create() method if that
        is implemented (see above). Later it may be called for
        invocations of fstat() too.
        '''
        if path == '/':
            return {'st_mode': stat.S_IFDIR  | 0o755, 'st_link': 2}
        raise OSError(errno.ENOENT, '')
    
    def lock(self, path, file_handle, cmd, flock):
        '''
        Perform POSIX file locking operation.

        The cmd argument will be either F_GETLK, F_SETLK or F_SETLKW.
        
        For the meaning of fields in 'struct flock' see the man page
        for fcntl(2). The l_whence field will always be set to
        SEEK_SET.
        
        For checking lock ownership, the 'fuse_file_info->owner'
        argument must be used.
        
        For F_GETLK operation, the library will first check currently
        held locks, and if a conflicting lock is found it will return
        information without calling this method. This ensures, that
        for local locks the l_pid field is correctly filled in. The
        results may not be accurate in case of race conditions and in
        the presence of hard links, but it's unlikly that an
        application would rely on accurate GETLK results in these
        cases. If a conflicting lock is not found, this method will be
        called, and the filesystem may fill out l_pid by a meaningful
        value, or it may leave this field zero.
    
        For F_SETLK and F_SETLKW the l_pid field will be set to the pid
        of the process performing the locking operation.
        
        Note: if this method is not implemented, the kernel will still
        allow file locking to work locally.  Hence it is only
        interesting for network filesystems and similar.
        '''
        raise OSError(errno.EFAULT, '')
    
    def utimes(self, path, times=None):
        '''
        Change the access and modification times of a file with
        nanosecond resolution.
        
        If times is None use the current time instead.
        '''
        return 0
    
    def bmap(self, path, blocksize, idx):
        '''
        Map block index within file to block index within device
         
        Note: This makes sense only for block device backed filesystems
        mounted with the 'blkdev' option.
        '''
        raise OSError(errno.EFAULT, '')

class FUSE():
    def __init__(self, operations, mountpoint, foreground=True, debug=False, nothreads=False, fsname=None, start=True, logging=False, **kwargs):       
        self.operations = operations
        self.mountpoint = mountpoint
        self.foreground = foreground
        self.debug = debug
        self.nothread = nothreads
        self.fsname = fsname
        self.logging = logging
        
        self.arguments = ['fuse']
        if foreground: self.arguments.append('-f')
        if debug: self.arguments.append('-d')
        if nothreads: self.arguments.append('-s')
        if fsname is None: fsname = self.operations.__class__.__name__
        self.arguments.append('-o')
        self.arguments.append('fsname={}'.format(fsname) + ','.join(key if value is True else '{}={}'.format(key, value) for key, value in kwargs.items()))
        self.arguments.append(mountpoint)
        
        self._operations = _fuse_operations()
        for name, function in self._operations._fields_:
            if hasattr(self, name) and hasattr(self.operations, name):
                setattr(self._operations, name, function(functools.partial(self._call, getattr(self, name))))
        
        if start:
            self.start() 
    
    def _call(self, function, *args):
        try:
            if self.logging:
                _logger.debug('{}{}'.format(function.__name__, args))
            return function(*args) or 0
        except OSError as error:
            return -(error.errno or errno.EFAULT)
        except:
            traceback.print_exc()
            return -errno.EFAULT
    
    def start(self):
        _fuse_main_real(len(self.arguments), (ctypes.c_char_p * len(self.arguments))(*[argument.encode('utf-8') for argument in self.arguments]),
                        ctypes.pointer(self._operations), ctypes.sizeof(self._operations), None)
    
    def getattr(self, path, stat):
        ctypes.memset(stat, 0, ctypes.sizeof(_c_stat))
        _stat_set_attributes(stat.contents, **self.operations.getattr(path.decode('utf-8')))
        return 0
    
    def readlink(self, path, target, size):
        data = ctypes.create_string_buffer(self.operations.readlink(path.decode('utf-8')).encode('utf-8')[:size - 1])
        ctypes.memmove(target, data, len(data))
        return 0
    
    def mknod(self, path, mode, dev):
        return self.operations.mknod(path.decode('utf-8'), mode, dev)
    
    def mkdir(self, path, mode):
        return self.operations.mkdir(path.decode('utf-8'), mode)
    
    def unlink(self, path):
        return self.operations.unlink(path.decode('utf-8'))
    
    def rmdir(self, path):
        return self.operations.rmdir(path.decode('utf-8'))
    
    def symlink(self, source, target):
        return self.operations.symlink(target.decode('utf-8'), source.decode('utf-8'))
    
    def rename(self, source, target):
        return self.operations.rename(source.decode('utf-8'), target.decode('utf-8')) 
    
    def link(self, source, target):
        return self.operations.link(target.decode('utf-8'), source.decode('utf-8'))
    
    def chmod(self, path, mode):
        return self.operations.chmod(path.decode('utf-8'), mode)
    
    def chown(self, path, uid, gid):
        return self.operations.chown(path.decode('utf-8'), uid, gid)
    
    def truncate(self, path, offset):
        return self.operations.truncate(path.decode('utf-8'), offset)
    
    def open(self, path, file_info):
        file_info.contents.fh = self.operations.open(path.decode('utf-8'), file_info.contents.flags)
        return 0
    
    def read(self, path, result, size, offset, file_info):
        data = self.operations.read(path.decode('utf-8'), size, offset, file_info.contents.fh)
        if not data:
            return 0
        data = ctypes.create_string_buffer(data[:size], size)
        ctypes.memmove(result, data, size)
        return size
    
    def write(self, path, data, size, offset, file_info):
        return self.operations('write', path.decode('utf-8'), ctypes.string_at(data, size), offset, file_info.contents.fh) 
  
    def statfs(self, path, statfs):
        attributes = self.operations.statfs(path.decode('utf-8'))
        for key, value in attributes.items():
            if hasattr(statfs.contents, key):
                setattr(statfs.contents, key, value)
        return 0
    
    def flush(self, path, file_info):
        return self.operations.flush(path.decode('utf-8'), file_info.contents.fh)
    
    def release(self, path, file_info):
        return self.operations.release(path.decode('utf-8'), file_info.contents.fh)
    
    def fsync(self, path, datasync, file_info):
        return self.operations.fsync(path.decode('utf-8'), datasync, file_info.contents.fh)
    
    def setxattr(self, path, name, value, size, options):
        return self.operations.setxattr(path.decode('utf-8'), name, ctypes.string_at(value, size), options)
    
    def getxattr(self, path, name, result, size):
        value = self.operations.getxattr(path.decode('utf-8'), name).encode('utf-8')
        length = len(value)
        if result:
            if length > size:
                return -errno.ERANGE
            ctypes.memmove(result, ctypes.create_string_buffer(value, length), length)
        return length
    
    def listxattr(self, path, result, size):
        attributes = self.operations.listxattr(path.decode('utf-8'))
        attributes = ctypes.create_string_buffer('\x00'.join(['\x00'.join([key, value]) for key, value in attributes.items()])) if attributes else ''
        length = len(attributes)
        if result:
            if length > size:
                return -errno.ERANGE
            ctypes.memmove(result, attributes, length)
        return length
    
    def removexattr(self, path, name):
        return self.operations.removexattr(path.decode('utf-8'), name.decode('utf-8'))
    
    def opendir(self, path, file_info):
        file_info.contents.fh = self.operations.opendir(path.decode('utf-8'))
        return 0
    
    def readdir(self, path, result, filler, offset, file_info):
        for path in self.operations.readdir(path.decode('utf-8'), file_info.contents.fh):
            if isinstance(path, str):
                name, stat, offset = path, None, 0
            else:
                name, attributes, offset = path
                if attributes:
                    stat = _c_stat()
                    _stat_set_attributes(stat, attributes)
                else:
                    stat = None
            if not filler(result, name.encode('utf-8'), stat, offset):
                break
        return 0
    
    def releasedir(self, path, file_info):
        return self.operations.releasedir(path.decode('utf-8'), file_info.contents.fh)
    
    def fsyncdir(self, path, datasync, file_info):
        return self.operations.fsyncdir(path.decode('utf-8'), datasync, file_info.contents.fh)
    
    def init(self, connection):
        return self.operations.init()
    
    def destroy(self, private):
        return self.operations.destroy()
    
    def access(self, path, mode):
        return self.operations.access(path.decode('utf-8'), mode)
    
    def create(self, path, mode, file_info):
        file_info.contents.fh = self.operations.create(path.decode('utf-8'), mode)
        return 0
    
    def ftruncate(self, path, length, file_info):
        return self.operations.truncate(path.decode('utf-8'), length, file_info.contents.fh)
    
    def fgetattr(self, path, stat, file_info):
        ctypes.memset(stat, 0, ctypes.sizeof(_c_stat))
        _stat_set_attributes(stat.contents, **self.operations.fgetattr(path.decode('utf-8'), file_info.contents.fh))
        return 0
    
    def lock(self, path, file_info, cmd, flock):
        return self.operations.lock(path.decode('utf-8'), file_info.contents.fh, cmd, flock)
    
    def utimens(self, path, times):
        if times:
            atime = _timespec_to_time(times.contents.actime)
            mtime = _timespec_to_time(times.contents.modtime)
            times = (atime, mtime)
        else:
            times = None
        return self.operations.utimens(path.decode('utf-8'), times)
    
    def bmap(self, path, blocksize, idx):
        return self.operations.bmap(path.decode('utf-8'), blocksize, idx)