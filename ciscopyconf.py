# -*- coding: utf-8 -*-
"""
This module uses the pexpect package to retrieve a cisco ios type
running, or startup, configuration and stores it as a CiscoPyConfAsList
object via inheritance.
"""

import re
import pexpect


class CiscoPyPxRxs(object):
    """
    Instantiating this class provides access to the regular expressions that
    are used by a pexpect instance expect method. pexpect needs to be
    instantiated first so that this class may compile the regular expressions.
    Compiling the regular expression speeds the regular expression matching
    process.
    """
    def __init__(self, pxobj):
        self.passwd_prompt = '(?i)password'
        self.exec_prompt = r'[\x21-\x7E]{2,}>$'
        self.priv_exec_prompt = r'[\x21-\x7E]{2,}#$'
        self.period = r'\.{2,}'
        self.copy_command = (r'Building configuration\.\.\.|Accessing'
                             r'.*\.\.\.|Loading|[!.CEO]+[!.CEO]+')
        self.px_passwd_list = [self.passwd_prompt,
                               pexpect.TIMEOUT,
                               pexpect.EOF]
        self.px_default_list = [self.exec_prompt,
                                self.priv_exec_prompt,
                                pexpect.TIMEOUT,
                                pexpect.EOF]
        self.px_verify_md5_list = [self.period,
                                   self.priv_exec_prompt,
                                   pexpect.TIMEOUT,
                                   pexpect.EOF]
        self.px_copy_command_list = [self.copy_command,
                                     self.priv_exec_prompt,
                                     pexpect.TIMEOUT,
                                     pexpect.EOF]
        self.px_cdefaultlist = pxobj.compile_pattern_list(self.px_default_list)
        self.px_cpasswdlist = pxobj.compile_pattern_list(self.px_passwd_list)
        self.px_cvrfymd5list = pxobj.compile_pattern_list(self.px_verify_md5_list)
        self.px_ccpcmdlist = pxobj.compile_pattern_list(self.px_copy_command_list)


class CiscoPyConfAsList(list):
    def __init__(self, lst=list()):
        super(CiscoPyConfAsList, self).__init__()
        if type(lst) is list:
            self.extend(lst)
        else:
            raise TypeError('Initialisation attribute MUST be type list')
        self.start_block_rx = None
        self.end_block_rx = None
    
    def __str__(self):
        # provide a string representation of the list
        return self.cfg_asstring

    @staticmethod
    def _get_indent_len(s):
        # Return count of leading whitespace
        return len(re.search(r'^(\s*)(.*?)$', s).groups('')[0])

    def _sub_section(self, i):
        indent_len = self._get_indent_len(self[i])
        # workout where the section ends, It is subsequent lines that are up
        # to the same indent level
        #
        # Identified by first in a list of subsequent lines offset by the
        # original index, plus 1
        try:
            section_end = ([li for li, lv in list(enumerate(self[i+1:]))
                            if self._get_indent_len(lv) <= indent_len][0] + i + 1)
        except IndexError:
            # if the section includes the last line, attempting
            # to check the line after raises an IndexError
            # the section offset is the list end
            section_end = len(self) + 1

        # return a new list based on the section start and end
        lst = CiscoPyConfAsList(self[i:section_end])
        # self.logger.debug('_subsection: Index {}: Lines {}'.format(i, len(l)))
        return lst

    def _get_indicies(self, rx):
        return [i for i, v in enumerate(self) if re.search(rx, v)]

    def cfg_asgenerator(self):
        # Returns parts of the list (self) of configuration lines, either line
        # by line, or by blocks
        if self.start_block_rx and self.end_block_rx:
            start_block_idxs = self._get_indicies(self.start_block_rx)
            end_block_idxs = self._get_indicies(self.end_block_rx)
            for sbi in start_block_idxs:
                rl = CiscoPyConfAsList()
                ebi = [v for v in end_block_idxs if v > sbi][0] + 1
                rl.extend(self[sbi:ebi])
                yield rl
        else:
            for le in self:
                yield le
    
    @property
    def cfg_asstring(self):
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
        # Simulates Cisco IOS show ... | include RegularExpression
        return CiscoPyConfAsList([v for v in self if re.search(rx, v)])
    
    i = include

    def exclude(self, rx):
        """
        The exclude method is equivalent to the Cisco IOS pipe through (|)
        exclude regular expression.
        
        One 'exclude' alias is included for convenience:
            e:  shorthand for exclude
        """
        # Simulates Cisco IOS show | exclude string
        # Also has the option of excluding based on rx e
        return CiscoPyConfAsList([v for v in self if not re.search(rx, v)])

    e = exclude

    def cfg_blocks(self, start_block_rx, end_block_rx):
        self.start_block_rx = start_block_rx
        self.end_block_rx = end_block_rx

        rl = CiscoPyConfAsList()
        rl.start_block_rx = self.start_block_rx
        rl.end_block_rx = self.end_block_rx

        for le in self.cfg_asgenerator():
            rl.extend(le)
        
        return rl

    def sections(self, rx):
            # Generate indexes for lines that match the regex
            list_indicies = [i for i, v in enumerate(self) if re.search(rx, v)]

            # Iterate through the idxs list that may be modified after each
            # index.  This tries to ensure that nested regex matches do not
            # create double entries in the overall section call
            while len(list_indicies):
                current_index = list_indicies[0]
                l = self._sub_section(current_index)
                # yield the current section
                yield l

                # Skip indexes that are after the current index and fall within
                # lines already contained in the last _sub_section call
                list_indicies = [i for i in list_indicies
                                 if i >= current_index + len(l)]

    def section(self, rx):
        """
        The section method is equivalent to the Cisco IOS pipe through (|)
        section regular expression.
        
        One 'section' alias is included for convenience:
            s:  shorthand for section
        """
        # return single config list based on sections()
        rl = CiscoPyConfAsList()
        
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
    
    @property
    def get_sectioninterface(self):
        rl = []
        interfaces = CiscoPyConfAsList(self.section(r'^interface'))
        interface_indicies = []
        
        for i, v in enumerate(interfaces):
            if 'interface' in v:
                interface_indicies.append(i)
        
        for i, v in enumerate(interface_indicies):
            try:
                rl.append(CiscoPyConfAsList(interfaces[v:interface_indicies[i+1]]))
            except IndexError:
                rl.append(CiscoPyConfAsList(interfaces[v:]))
        
        return rl

    @property
    def get_obtacsnmpcommunity(self):
        rx = r'^snmp-server community.*[rRwW] snmp-access$'
        
        if self.include(rx):
            return self.include(rx)[0].split()[-3]
        else:
            return None
    
    @property
    def get_nonobtacsnmpcommunities(self):
        rx = r'^snmp-server community'
        obtacsc = self.get_obtacsnmpcommunity
        scs = self.include(rx)
        nonobtacscs = [v for v in scs if obtacsc not in v]
        
        return CiscoPyConfAsList(nonobtacscs)
        
    def get_interfaceswith(self, rx):
        interfaces = self.get_sectioninterface
        interfaces_with = []
        
        for i, v in enumerate(interfaces):
            interface_with = CiscoPyConfAsList()
                
            for k, e in enumerate(v):
                if re.search(rx, e):
                    interface_with.append(e)
            
            if len(interface_with) > 0:
                interface_with.insert(0, v[0])
                interface_with.append(' exit')
                interfaces_with.append(interface_with)
        
        return interfaces_with
        
    @property
    def get_devicehostname(self):
        return self.include(r'^hostname').cfg_asstring.split()[-1]
    

class CiscoPyConf(CiscoPyConfAsList):
    def __init__(self, px_timeout=60, px_maxread=10000,
                 px_searchwindowsize=200000, px_encoding='utf-8',
                 splitlines_rx=r'[\r\n]+'):
        super(CiscoPyConf, self).__init__()

        self.splitlines_rx = splitlines_rx
        self.px_timeout = px_timeout
        self.px_maxread = px_maxread
        self.px_searchwindowsize = px_searchwindowsize
        self.px_encoding = px_encoding
        self.status = False
        self.statuscause = None
        self.hostname = None
        self.username = None
        self.passwd = None
        self.ssh_options = ' '.join(['-o CheckHostIP=no',
                                     '-o StrictHostKeyChecking=no',
                                     '-o UserKnownHostsFile=/dev/null',
                                     '-o ConnectTimeout=2'])
        self.ssh_destination = None
        self.ssh_command = None
        self.px_spawn = None
        self.px_rxs = None

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

    def get_cfgfromstring(self, s):
        """
        Extend a list object instance from a string variable by
        converting a configuration as a string into a list using the
        str2lst() method, then sanitising the list elements using the
        _sanitise() method.
        """
        try:
            self.extend(self._sanitise(self._str2list(s)))
        except Exception as exception:
            self.statuscause = str(exception)
        
        if len(self) > 0:
            self.status = True

    def get_cfgfromfile(self, f, encoding='raw_unicode_escape'):
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
    
    def get_cfgfromdevice(self, h, u='source', p='g04itMua', es='cisco'):
        """
        This method uses pexpect and ssh to get a running-config.
        """
        def pxspawn_cleanup():
            self.px_spawn.close()
            del self.px_spawn
        
        self.hostname = h
        self.username = u
        self.passwd = p
        self.ssh_destination = ''.join([self.username, '@', self.hostname])
        self.ssh_command = ' '.join(['/usr/bin/env ssh -q',
                                     self.ssh_options,
                                     ssh_destination])
        self.px_spawn = pexpect.spawn(self.ssh_command, timeout=self.px_timeout,
                                      maxread=self.px_maxread,
                                      searchwindowsize=self.px_searchwindowsize,
                                      encoding=self.px_encoding)
        self.px_rxs = CiscoPyPxRxs(self.px_spawn)
        pxresult = self.px_spawn.expect(self.px_rxs.px_cpasswdlist)
        
        if pxresult == 0:
            pass
        elif pxresult == 1:
            pxspawn_cleanup()
            self.statuscause = 'ssh timeout password prompt'
            self.append('no running-config')
            return
        elif pxresult == 2:
            pxspawn_cleanup()
            self.statuscause = 'ssh spawn eof'
            self.append('no running-config')
            return
        
        self.px_spawn.sendline(self.passwd)

        pxresult = self.px_spawn.expect(self.px_rxs.px_cdefaultlist)

        if pxresult == 0:
            self.px_spawn.sendline('enable')
            pxresult = self.px_spawn.expect(self.px_rxs.px_cpasswdlist)
            if pxresult == 0:
                self.px_spawn.sendline(es)
                pxresult = self.px_spawn.expect(self.px_rxs.px_cdefaultlist)
                if pxresult == 0:
                    pxspawn_cleanup()
                    self.statuscause = 'wrong enable secret'
                    return
                elif pxresult == 1:
                    pass
                elif pxresult == 2:
                    pxspawn_cleanup()
                    self.statuscause = 'timeout: post enable priv exec prompt'
                    return
                elif pxresult == 3:
                    pxspawn_cleanup()
                    self.statuscause = 'eof: post enable priv exec prompt'
                    return
            elif pxresult == 1:
                pxspawn_cleanup()
                self.statuscause = 'timeout: post enable password prompt'
                return
            elif pxresult == 2:
                pxspawn_cleanup()
                self.statuscause = 'eof: post enable password prompt'
                return
        elif pxresult == 1:
            pass
        elif pxresult == 2:
            pxspawn_cleanup()
            self.statuscause = 'timeout: post ssh password'
            return
        elif pxresult == 3:
            pxspawn_cleanup()
            self.statuscause = 'eof: post ssh password'
        
        self.px_spawn.sendline('terminal length 0')

        pxresult = self.px_spawn.expect(self.px_rxs.px_cdefaultlist)

        if pxresult == 1:
            pass
        elif pxresult == 2:
            pxspawn_cleanup()
            self.statuscause = 'timeout: post term len 0 priv exec prompt'
            return
        elif pxresult == 3:
            pxspawn_cleanup()
            self.statuscause = 'eof: post term len 0 priv exec prompt'
            return
        
        self.px_spawn.sendline('show running-config')
        
        pxresult = self.px_spawn.expect(self.px_rxs.px_cdefaultlist)
        
        if pxresult == 1:
            pass
        elif pxresult == 2:
            pxspawn_cleanup()
            self.statuscause = 'timeout: post show runn priv exec prompt'
            return
        elif pxresult == 3:
            pxspawn_cleanup()
            self.statuscause = 'eof: post show runn priv exec prompt'
            return
        
        self.status = True
        
        self.extend(self._sanitise(self._str2list(self.px_spawn.before)))
        
        pxspawn_cleanup()
