# -*- coding: utf-8 -*-
"""
break up a string running-config/startup-config into a list and manipulate the
content as per a cisco ios cli.
"""
import re
from .ciscopynetwork import CiscoPyNetwork


class CiscoPyConfAsList(list):
    def __init__(self, lst):
        super(CiscoPyConfAsList, self).__init__()

        if isinstance(lst, list):
            self.extend(lst)
        else:
            raise TypeError('Parameter, lst, is not list type.')

        self.start_block_rx = None
        self.end_block_rx = None

    def __str__(self):
        return self.as_string()

    @staticmethod
    def _get_indent_len(s):
        return len(re.search(r'^(\s*)(.*?)$', s).groups('')[0])

    def _sub_section(self, i):
        indent_len = self._get_indent_len(self[i])
        try:
            section_end = ([li for li, lv in list(enumerate(self[i+1:]))
                            if self._get_indent_len(lv) <= indent_len][0] + i + 1)
        except IndexError:
            section_end = len(self) + 1

        lst = self[i:section_end]

        return lst

    def _get_indicies(self, rx):
        return [i for i, v in enumerate(self) if re.search(rx, v)]

    def as_generator(self):
        if self.start_block_rx and self.end_block_rx:
            start_block_idxs = self._get_indicies(self.start_block_rx)
            end_block_idxs = self._get_indicies(self.end_block_rx)
            for sbi in start_block_idxs:
                rl = CiscoPyConfAsList([])
                ebi = [v for v in end_block_idxs if v > sbi][0] + 1
                rl.extend(self[sbi:ebi])
                yield rl
        else:
            for le in self:
                yield le

    def as_string(self):
        return '\n'.join(self)

    def begin(self, rx):
        """
        The begin method is equivalent to the Cisco IOS pipe (|) through
        begin regular expression.

        One 'begin' alias is included for convenience:
            b:  shorthand for begin
        """
        for i, v in enumerate(self):
            if re.search(rx, v):
                return CiscoPyConfAsList([le for le in self[i:]])

    b = begin

    def include(self, rx):
        """
        The include method is equivalent to the Cisco IOS pipe through (|)
        include regular expression.

        One 'include' alias is included for convenience:
            i:  shorthand for include
        """
        return CiscoPyConfAsList([v for v in self if re.search(rx, v)])

    i = include

    def exclude(self, rx):
        """
        The exclude method is equivalent to the Cisco IOS pipe through (|)
        exclude regular expression.

        One 'exclude' alias is included for convenience:
            e:  shorthand for exclude
        """
        return CiscoPyConfAsList([v for v in self if not re.search(rx, v)])

    e = exclude

    def conf_blocks(self, start_block_rx, end_block_rx):
        self.start_block_rx = start_block_rx
        self.end_block_rx = end_block_rx

        rl = CiscoPyConfAsList([])
        rl.start_block_rx = self.start_block_rx
        rl.end_block_rx = self.end_block_rx

        for le in self.as_generator():
            rl.extend(le)

        return rl

    def sections(self, rx):
        list_indicies = [i for i, v in enumerate(self) if re.search(rx, v)]

        while len(list_indicies):
            current_index = list_indicies[0]
            rl = self._sub_section(current_index)

            yield rl

            list_indicies = [i for i in list_indicies if i >= current_index + len(rl)]

    def section(self, rx):
        """
        The section method is equivalent to the Cisco IOS pipe through (|)
        section regular expression.

        One 'section' alias is included for convenience:
            s:  shorthand for section
        """
        rl = CiscoPyConfAsList([])

        for v in list(self.sections(rx)):
            rl.extend(v)

        return rl

    s = section

    def has_regexp(self, rx):
        r = False

        for v in self:
            if re.search(rx, v):
                r = True

        return r

    def has_noregexp(self, rx):
        r = True

        for v in self:
            if re.search(rx, v):
                r = False

        return r

    def has_string(self, s):
        r = False

        for v in self:
            if s in v:
                r = True

        return r

    def section_interface(self):
        rl = []
        interfaces = self.section(r'^interface')
        interface_indicies = []

        for i, v in enumerate(interfaces):
            if 'interface' in v:
                interface_indicies.append(i)

        for i, v in enumerate(interface_indicies):
            try:
                rl.append(CiscoPyConfAsList
                          (interfaces[v:interface_indicies[i+1]]))
            except IndexError:
                rl.append(CiscoPyConfAsList(interfaces[v:]))

        return rl

    def obtac_snmpcommunity(self):
        rx = r'^snmp-server community.*[rRwW] snmp-access$'

        if self.include(rx):
            return self.include(rx)[0].split()[-3]
        else:
            return None

    def nonobtac_snmpcommunities(self):
        rx = r'^snmp-server community'
        obtacsc = self.obtac_snmpcommunity()
        scs = self.include(rx)
        nonobtacscs = [v for v in scs if obtacsc not in v]

        return CiscoPyConfAsList(nonobtacscs)

    def find_interfaceswith(self, rx):
        interfaces = self.section_interface()
        interfaces_with = []

        for i, v in enumerate(interfaces):
            interface_with = CiscoPyConfAsList([])

            for k, e in enumerate(v):
                if re.search(rx, e):
                    interface_with.append(e)

            if len(interface_with) > 0:
                interface_with.insert(0, v[0])
                interface_with.append(' exit')
                interfaces_with.append(interface_with)

        return interfaces_with

    def get_hostname(self):
        return self.include(r'^hostname')[-1]


class CiscoPyConf(CiscoPyConfAsList):
    def __init__(self):
        super(CiscoPyConf, self).__init__([])
        self.cpnetwork = CiscoPyNetwork()
        self.status = False
        self.statuscause = None
        self.hostname = None
        self.username = None
        self.passwd = None
        self.enable_secret = None
        self.remote_host = None
        self.show_config_command = None

    @staticmethod
    def _rm_lst_element_at_strt(lst, reverse=False):
        """
        This method was created to remove unnecessary list elements.
        Captured 'show running-config' or 'show startup-config' command
        output where 'paging' was used will still contain control
        characters at the beginning and the end of the command output.

        A regular expression is used to determine when the body of the
        configuration text starts. This provides a list index. Then the
        crap at the beginning to the index is deleted from the list.
        """
        if reverse:
            rx = r'^end$'
            lst.reverse()
        else:
            rx = r'^[a-zA-Z]'

        for i, v in enumerate(lst):
            if re.match(rx, v):
                del(lst[0:i])
                break

        if reverse:
            lst.reverse()

        return lst

    def _sanitise(self, lst):
        """
        This method was created to remove unnecessary list element
        characters where 'paging' was used to capture command output.
        """
        rl = []
        rx = r'\x08( *[\x21-\x7E]+(?: +[\x21-\x7E]+)*)$'

        for i, v in enumerate(lst):
            if 'More' in v:
                if re.search(rx, v):
                    s = re.search(rx, v).group(1)
                    if '!' == s:
                        continue
                    elif 'banner login' in s:
                        rl.append('banner login #')
                    elif s.startswith('^C'):
                        rl.append('#')
                    else:
                        rl.append(s)
            elif '!' in v:
                continue
            elif 'banner login' in v:
                rl.append('banner login #')
            elif v.startswith('^C'):
                rl.append('#')
            else:
                rl.append(v)

        rl = self._rm_lst_element_at_strt(rl)
        rl = self._rm_lst_element_at_strt(rl, reverse=True)

        return rl

    @staticmethod
    def _str2list(s):
        return s.splitlines()

    def from_string(self, s):
        """
        Extend a list object instance from a string variable by
        converting a configuration as a string into a list using the
        str2lst() method, then sanitising the list elements using the
        _sanitise() method.
        """
        self.extend(self._sanitise(self._str2list(s)))

    def from_file(self, f, encoding='raw_unicode_escape'):
        """
        Extend a ConfAsList object instance from a file containing a
        running/startup configuration. The configuration from the file
        is read as a string object and is converted to a list object.
        The str to list conversion is completed by the str2lst()
        method.

        List element sanitisation is performed by the _sanitise()
        method.

        Encoding may be changed by specifying a different str encoding
        using the 'enc' keyword method variable. 'raw_unicode_escape'
        is the default due to the strange characters included if paging
        was used during the output capture to a file of a
        'show running-config' or 'show startup-config' command.

        For the most part, it is expected that configurations captured
        to file will have been performed using the 'terminal length 0'
        command. That is, no paging will have been used to capture the
        output of a 'show running-config', or 'show startup-config',
        command.

        Another alternative a 'running-config' or 'startup-config' will
        have been transferred using a network method:
        scp/tftp/ftp etc.

        The rx method keyword variable may be used to change the default
        line boundary. The rx method keyword variable is a regular
        expression.
        """
        try:
            fd = open(f, encoding=encoding)
        except Exception as exception:
            self.statuscause = str(exception)
        else:
            with fd:
                try:
                    self.extend(self._sanitise(self._str2list(fd.read())))
                except UnicodeDecodeError as exception:
                    self.statuscause = str(exception)

        if len(self) > 0:
            self.status = True

    def from_device(self,
                    host,
                    user='source',
                    passwd='g04itMua',
                    enable_secret='cisco',
                    which_config='running',
                    running_all=False):
        """
        Retrieve a config from a remote device.

        The "default" config to retrieve is "running". The alternate value is "startup".
        """

        self.hostname = host
        self.username = user
        self.passwd = passwd
        self.enable_secret = enable_secret
        self.remote_host = ''.join([self.username, '@', self.hostname])

        if which_config == 'running':
            if not running_all:
                self.show_config_command = 'show {}-config'.format(which_config)

            if running_all:
                self.show_config_command = 'show {}-config all'.format(which_config)

        elif which_config == 'startup':
            self.show_config_command = 'show {}-config'.format(which_config)
        else:
            errortext = 'Attribute "which_config" error: value MUST be either "running" or "startup" not "{}"'
            raise AttributeError(errortext.format(which_config))

        if self.cpnetwork.reachable(self.hostname):
            try:
                self.cpnetwork.set_sshclient(host=self.hostname, username=self.username, password=self.passwd,
                                             secret=self.enable_secret)

                cmd_output = self.cpnetwork.sshclient.send_command(self.show_config_command,
                                                                   expect_string=self.cpnetwork.sshclient.prompt)
                if len(cmd_output) > 0:
                    self.from_string(cmd_output)
                    self.status = True
                else:
                    errortext = 'Attribute "cmd_output" error from device {}: no show config output'
                    self.statuscause = AttributeError(errortext.format(self.hostname))

                self.cpnetwork.sshclient.disconnect()
            except Exception as exception:
                self.statuscause = exception
