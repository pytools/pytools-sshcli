# -*- coding: utf-8 -*-

import os
import paramiko
from pytools_cli import CLI


def _strip(input):
    if hasattr(input, 'read'):
        try:
            stripped = input.read().decode('utf-8').rstrip()
        except Exception:
            return ''

        return stripped

    return ''


def _normalize(path):
    return os.path.normpath(path)


class SSHReturnValue:

    def __init__(self, **kwargs):
        self._return_value = kwargs.get('return_value', None)
        self._stdin = kwargs.get('stdin', None)
        self._stdout = kwargs.get('stdout', None)
        self._stderr = kwargs.get('stderr', None)

        if self._stdin == '':
            self._stdin = None

        if self._stdout == '':
            self._stdout = None

        if self._stderr == '':
            self._stderr = None

    def success(self):
        return self._return_value == 0

    def failure(self):
        return self._return_value != 0 or self._stderr is not None

    def return_value(self):
        return self._return_value

    def stdout(self):
        return self._stdout

    def stderr(self):
        return self._stderr

    def output(self):
        stdout = self.stdout()

        if stdout is None:
            stdout = ''

        return stdout


class SSHCLI(CLI):

    def __init__(self, **kwargs):
        self._hostname = kwargs.get('hostname', None)
        self._port = kwargs.get('port', 22)
        self._username = kwargs.get('username', None)
        self._password = kwargs.get('password', None)

        self._client = None
        self._sftp = None

    def __del__(self):
        self._close()

    def cwd(self, path=None):
        self._check_connection()

        result = self._exec('cd {}; pwd'.format(self._get_cwd()))
        output = result.output()

        if path:
            return _normalize(output + '/' + path)

        return output

    def cud(self, path=None):
        self._check_connection()

        result = self._exec('''eval echo ~$USER''')
        cud = result.output()

        if path:
            return _normalize(cud + '/' + path)

        return cud

    def cd(self, path):
        self._check_connection()

        if path == '~/':
            self._set_cwd(self.cud())
            return

        if path == '/':
            self._set_cwd(_normalize(path))
            return

        normalized = _normalize(self._get_cwd() + '/' + path)

        if self.dir_exists(normalized):
            self._set_cwd(normalized)

    def file_exists(self, path, include_symlink_to_file=True):
        self._check_connection()

        normalized = _normalize(path)
        result = self._exec('''cd {}; [ -f {} ] && exit 0'''.format(self._get_cwd(), normalized))

        # if path exists and it is a file, the return_value is 0, otherwise 1
        exists = result.return_value() == 0

        if not include_symlink_to_file:
            return exists and not self.symlink_exists(normalized)
            pass

        return exists

    def dir_exists(self, path, include_symlink_to_dir=True):
        self._check_connection()

        normalized = _normalize(path)
        result = self._exec('''cd {}; [ -d {} ] && exit 0'''.format(self._get_cwd(), normalized))

        # if path exists and it is a directory, the return_value is 0, otherwise 1
        exists = result.return_value() == 0

        if not include_symlink_to_dir:
            return exists and not self.symlink_exists(normalized)

        return exists

    def symlink_exists(self, path, must_point_to_file=False, must_point_to_dir=False):
        self._check_connection()

        normalized = _normalize(path)
        result = self._exec('''cd {}; [ -L {} ] && exit 0'''.format(self._get_cwd(), normalized))

        # if path exists and it is a symlink, the return_value is 0, otherwise 1
        is_symlink = result.return_value() == 0

        if must_point_to_file:
            return is_symlink and self.file_exists(normalized)

        if must_point_to_dir:
            return is_symlink and self.dir_exists(normalized)

        return is_symlink

    def cat(self, path):
        self._check_connection()

        normalized = _normalize(path)
        result = self._exec('cd {}; cat {}'.format(self._get_cwd(), normalized))

        print(result.output())

    def touch(self, file_name):
        self._check_connection()

        self._exec('cd {}; touch {}'.format(self._get_cwd(), file_name))

    def mkdir(self, path):
        self._check_connection()

        self._exec('cd {}; mkdir -p {}'.format(self._get_cwd(), path))

    def symlink(self, what_path, to_where):
        self._check_connection()

        self._exec('cd {}; ln -sfn {} {}'.format(self._get_cwd(), what_path, to_where))

    def rm(self, path):
        self._check_connection()

        self._exec('cd {}; rm -rf {}'.format(self._get_cwd(), path))

    def cp(self, source, dest):
        self._check_connection()

        self._exec('cd {}; yes | cp -rf {} {}'.format(self._get_cwd(), source, dest))

    def mv(self, source, dest):
        self._check_connection()

        self._exec('cd {}; mv {} {}'.format(self._get_cwd(), source, dest))

    def glob(self, pattern):
        self._check_connection()

        result = self._exec('''cd {}; shopt -s globstar; ls {}'''.format(self._get_cwd(), pattern))

        output = result.output()  # type: str
        paths = output.splitlines()  # type: list
        filtered_paths = []

        for path in paths:  # type: str
            if path == '':
                continue

            if path.endswith(':'):
                path = path[0:-1]

            filtered_paths.append(path)

        return filtered_paths

    def compress(self, path, archive_name):
        self._check_connection()

        normalized = _normalize(path)

        if not self.exists(normalized):
            raise NotADirectoryError('The path "{}" does not exist.'.format(normalized))

        arc_name = archive_name  # type: str

        if arc_name.endswith('.tar.xz'):
            arc_name = arc_name.replace('.tar.xz', '')

        self._exec('cd {}; XZ_OPT=-9 tar -cvpJf {}.tar.xz {}'.format(self._get_cwd(), arc_name, normalized))

        archive = '{}.tar.xz'.format(arc_name)

        if not self.file_exists(self.cwd(archive)):
            raise FileNotFoundError('The archive "{}" was not created.'.format(archive))

    def extract(self, archive_name, dir_to_extract=None):
        self._check_connection()

        arc_name = archive_name  # type: str

        if arc_name.endswith('.tar.xz'):
            arc_name = arc_name.replace('.tar.xz', '')

        archive = '{}.tar.xz'.format(arc_name)

        if not self.file_exists(self.cwd(archive)):
            raise FileNotFoundError('Archive "{}" does not exist.'.format(archive))

        dir = arc_name

        if dir_to_extract:
            dir = _normalize(dir_to_extract)

        if not self.dir_exists(dir):
            self.create_dir(dir)

        self._exec('cd {}; tar xf {}.tar.xz -C {}'.format(self._get_cwd(), arc_name, dir))

    def download(self, remote_file_name_to_download, save_as):
        self._check_connection()

        sftp = self._sftp

        sftp.get(remote_file_name_to_download, save_as)

    def upload(self, local_file_name_to_upload, save_as_on_remote):
        self._check_connection()

        sftp = self._sftp

        sftp.put(local_file_name_to_upload, save_as_on_remote)

    def _check_connection(self):
        if self._client is None:
            self._client = paramiko.SSHClient()

            self._connect()

            # determine CWD upon initialization
            self._determine_cwd()

    def _connect(self):
        client = self._client

        # client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        client.connect(hostname=self._hostname,
                       port=self._port,
                       username=self._username,
                       password=self._password)

        self._sftp = client.open_sftp()

    def _exec(self, command):
        self._check_connection()

        stdin, stdout, stderr = self._client.exec_command(command)

        result = SSHReturnValue(return_value=stdout.channel.recv_exit_status(),
                                stdin=_strip(stdin),
                                stdout=_strip(stdout),
                                stderr=_strip(stderr))
        return result

    def _close(self):
        if self._client:
            self._client.close()

    def _determine_cwd(self):
        result = self._exec('pwd')

        self._set_cwd(result.output())
