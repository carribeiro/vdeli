#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""An "authorizer" is a class handling authentications and permissions
of the FTP server. It is used by pyftpdlib.ftpserver.FTPHandler
class for:

- verifying user password
- getting user home directory
- checking user permissions when a filesystem read/write event occurs
- changing user when accessing the filesystem

This module contains two classes which implements such functionalities
in a system-specific way for both SQLite3 and Django.
"""

__all__ = []


import os
import errno

from pyftpdlib.ftpserver import DummyAuthorizer, AuthorizerError


def replace_anonymous(callable):
    """A decorator to replace anonymous user string passed to authorizer
    methods as first argument with the actual user used to handle
    anonymous sessions.
    """
    def wrapper(self, username, *args, **kwargs):
        if username == 'anonymous':
            username = self.anonymous_user or username
        return callable(self, username, *args, **kwargs)
    return wrapper


class _Base(object):
    """Methods common to both SQLite3 and Django authorizers.
    Not supposed to be used directly.
    """

    def __init__(self):
        """Check for errors in the constructor."""
        if self.rejected_users and self.allowed_users:
            raise ValueError("rejected_users and allowed_users options are "
                             "mutually exclusive")

        # users = self._get_system_users()
        # for user in (self.allowed_users or self.rejected_users):
        #     if user == 'anonymous':
        #         raise ValueError('invalid username "anonymous"')
        #     if user not in users:
        #         raise ValueError('unknown user %s' % user)

        if self.anonymous_user is not None:
            if not self.has_user(self.anonymous_user):
                raise ValueError('no such user %s' % self.anonymous_user)
            home = self.get_home_dir(self.anonymous_user)
            if not os.path.isdir(home):
                raise ValueError('no valid home set for user %s'
                                 % self.anonymous_user)

    def override_user(self, username, password=None, homedir=None, perm=None,
                      msg_login=None, msg_quit=None):
        """Overrides the options specified in the class constructor
        for a specific user.
        """
        if not password and not homedir and not perm and not msg_login \
        and not msg_quit:
            raise ValueError("at least one keyword argument must be specified")
        if self.allowed_users and username not in self.allowed_users:
            raise ValueError('%s is not an allowed user' % username)
        if self.rejected_users and username in self.rejected_users:
            raise ValueError('%s is not an allowed user' % username)
        if username == "anonymous" and password:
            raise ValueError("can't assign password to anonymous user")
        if not self.has_user(username):
            raise ValueError('no such user %s' % username)

        if username in self._dummy_authorizer.user_table:
            # re-set parameters
            del self._dummy_authorizer.user_table[username]
        self._dummy_authorizer.add_user(username, password or "",
                                                  homedir or "",
                                                  perm or "",
                                                  msg_login or "",
                                                  msg_quit or "")
        if homedir is None:
            self._dummy_authorizer.user_table[username]['home'] = ""

    def get_msg_login(self, username):
        return self._get_key(username, 'msg_login') or self.msg_login

    def get_msg_quit(self, username):
        return self._get_key(username, 'msg_quit') or self.msg_quit

    def get_perms(self, username):
        overridden_perms = self._get_key(username, 'perm')
        if overridden_perms:
            return overridden_perms
        if username == 'anonymous':
            return 'elr'
        return self.global_perm

    def has_perm(self, username, perm, path=None):
        return perm in self.get_perms(username)

    def _get_key(self, username, key):
        if self._dummy_authorizer.has_user(username):
            return self._dummy_authorizer.user_table[username][key]

    def _is_rejected_user(self, username):
        """Return True if the user has been black listed via
        allowed_users or rejected_users options.
        """
        if self.allowed_users and username not in self.allowed_users:
            return True
        if self.rejected_users and username in self.rejected_users:
            return True
        return False


try:
    import pwd, spwd, sqlite3, httplib, urllib
except ImportError:
    pass
else:
    __all__.extend(['BaseSQLite3Authorizer', 
                    'SQLite3Authorizer', 
                    'BaseDjangoAuthorizer', 
                    'DjangoAuthorizer'])

    # the uid/gid the server runs under
    PROCESS_UID = os.getuid()
    PROCESS_GID = os.getgid()

    class BaseSQLite3Authorizer(object):
        """An authorizer compatible with Unix user account and password
        database.
        This class should not be used directly unless for subclassing.
        Use higher-level SQLite3Authorizer class instead.
        """

        def __init__(self, anonymous_user=None):
#            if os.geteuid() != 0 or not spwd.getspall():
#                raise AuthorizerError("super user privileges are required")
            self.anonymous_user = anonymous_user

            # if self.anonymous_user is not None:
            #     if not self.anonymous_user in self._get_system_users():
            #         raise ValueError('no such user %s' % self.anonymous_user)
#                try:
#                    return pwd.getpwnam(self.anonymous_user).pw_dir
#                except KeyError:
#                    raise ValueError('no such user %s' % username)

          
        # --- overridden / private API

        def validate_authentication(self, username, password):
            """Authenticates against shadow password db; return
            True on success.
            """
            if username == "anonymous":
                return self.anonymous_user is not None
            try:
                db = sqlite3.connect("/srv/git/vdeli/cdnmanager/ftpserver/ftpusers.db")
                pw1 = db.cursor()
                pw1.execute('select password from users where username = "%s"' % (username))
                pw2 = password
                dbpw = list(pw1)[0]
            except KeyError:  # no such username
                print "KeyError"
                return False
            else:
                return dbpw[0] == pw2
            
#        def validate_authentication(self, username, password):
#            """Authenticates against shadow password db; return
#            True on success.
#            """
#            if username == "anonymous":
#                return self.anonymous_user is not None
#            try:
#                pw1 = spwd.getspnam(username).sp_pwd
#                pw2 = crypt.crypt(password, pw1)
#            except KeyError:  # no such username
#                return False
#            else:
#                return pw1 == pw2

        @replace_anonymous
        def impersonate_user(self, username, password):
            """Change process effective user/group ids to reflect
            logged in user.
            """
            try:
                pwdstruct = pwd.getpwnam("nobody")
            except KeyError:
                raise AuthorizerError('no such user %s' % pwdstruct)
            else:
                os.setegid(pwdstruct.pw_gid)
                os.seteuid(pwdstruct.pw_uid)
                
        def terminate_impersonation(self, username):
            """Revert process effective user/group IDs."""
            os.setegid(PROCESS_GID)
            os.seteuid(PROCESS_UID)

        @replace_anonymous
        def has_user(self, username, password):
            """Return True if user exists on the Unix system.
            If the user has been black listed via allowed_users or
            rejected_users options always return False.
            """
            if self.BaseSQLite3Authorizer.validate_authentication(self, username, password):
                return username

        @replace_anonymous
        def get_home_dir(self, username):
            """Return user home directory."""
            try:
                db = sqlite3.connect("/srv/git/vdeli/cdnmanager/ftpserver/ftpusers.db")
                cursor = db.cursor()
                cursor.execute('select homedir from users where username = "%s"' % (username))
                homedir = list(cursor)[0]
                return str(homedir[0])
            except KeyError:
                raise AuthorizerError('no such user %s' % username)

        def get_msg_login(self, username):
            return "Login successful."

        def get_msg_quit(self, username):
            return "Goodbye."

        def get_perms(self, username):
            return "elradfmw"

        def has_perm(self, username, perm, path=None):
            return perm in self.get_perms(username)


    class SQLite3Authorizer(_Base, BaseSQLite3Authorizer):
        """A wrapper on top of BaseSQLite3Authorizer providing options
        to specify what users should be allowed to login, per-user
        options, etc.

        Example usages:

         >>> from pyftpdlib.contrib.authorizers import SQLite3Authorizer
         >>> # accept all except root
         >>> auth = SQLite3Authorizer(rejected_users=["root"])
         >>>
         >>> # accept some users only
         >>> auth = SQLite3Authorizer(allowed_users=["matt", "jay"])
         >>>
         >>> # accept everybody and don't care if they have not a valid shell
         >>> auth = SQLite3Authorizer(require_valid_shell=False)
         >>>
         >>> # set specific options for a user
         >>> auth.override_user("matt", password="foo", perm="elr")
        """

        # --- public API

        def __init__(self, global_perm="elradfmw",
                           allowed_users=[],
                           rejected_users=[],
                           require_valid_shell=True,
                           anonymous_user=None,
                           msg_login="Login successful.",
                           msg_quit="Goodbye."):
            """Parameters:

             - (string) global_perm:
                a series of letters referencing the users permissions;
                defaults to "elradfmw" which means full read and write
                access for everybody (except anonymous).

             - (list) allowed_users:
                a list of users which are accepted for authenticating
                against the FTP server; defaults to [] (no restrictions).

             - (list) rejected_users:
                a list of users which are not accepted for authenticating
                against the FTP server; defaults to [] (no restrictions).

             - (bool) require_valid_shell:
                Deny access for those users which do not have a valid shell
                binary listed in /etc/shells.
                If /etc/shells cannot be found this is a no-op.
                Anonymous user is not subject to this option, and is free
                to not have a valid shell defined.
                Defaults to True (a valid shell is required for login).

             - (string) anonymous_user:
                specify it if you intend to provide anonymous access.
                The value expected is a string representing the system user
                to use for managing anonymous sessions;  defaults to None
                (anonymous access disabled).

             - (string) msg_login:
                the string sent when client logs in.

             - (string) msg_quit:
                the string sent when client quits.
            """
            BaseSQLite3Authorizer.__init__(self, anonymous_user)
            self.global_perm = global_perm
            self.allowed_users = allowed_users
            self.rejected_users = rejected_users
            self.anonymous_user = anonymous_user
            self.require_valid_shell = require_valid_shell
            self.msg_login = msg_login
            self.msg_quit = msg_quit

            self._dummy_authorizer = DummyAuthorizer()
            self._dummy_authorizer._check_permissions('', global_perm)
            _Base.__init__(self)
            if require_valid_shell:
                for username in self.allowed_users:
                    if not self._has_valid_shell(username):
                        raise ValueError("user %s has not a valid shell"
                                         % username)

        def override_user(self, username, password=None, homedir=None, perm=None,
                          msg_login=None, msg_quit=None):
            """Overrides the options specified in the class constructor
            for a specific user.
            """
            if self.require_valid_shell and username != 'anonymous':
                if not self._has_valid_shell(username):
                    raise ValueError("user %s has not a valid shell"
                                     % username)
            _Base.override_user(self, username, password, homedir, perm,
                                msg_login, msg_quit)

        # --- overridden / private API

        def validate_authentication(self, username, password):
            if username == "anonymous":
                return self.anonymous_user is not None
            if self._is_rejected_user(username):
                return False
            if self.require_valid_shell and username != 'anonymous':
                if not self._has_valid_shell(username):
                    return False
            overridden_password = self._get_key(username, 'pwd')
            if overridden_password:
                return overridden_password == password

            return BaseSQLite3Authorizer.validate_authentication(self, username, password)

        @replace_anonymous
        def has_user(self, username, password):
            if BaseSQLite3Authorizer.validate_authentication(self, username, password):
                return username

        @replace_anonymous
        def get_home_dir(self, username):
            overridden_home = self._get_key(username, 'home')
            if overridden_home:
                return overridden_home
            return BaseSQLite3Authorizer.get_home_dir(self, username)

        @staticmethod
        def _has_valid_shell(username):
            """Return True if the user has a valid shell binary listed
            in /etc/shells. If /etc/shells can't be found return True.
            """
            try:
                file = open('/etc/shells', 'r')
            except IOError, err:
                if err.errno == errno.ENOENT:
                    return True
                raise
            else:
                try:
                    shell = "/bin/bash"
                    for line in file:
                        if line.startswith('#'):
                            continue
                        line = line.strip()
                        if line == shell:
                            return True
                    return False
                finally:
                    file.close()

    class BaseDjangoAuthorizer(object):
        """ An authorizer compatible with Unix user account and password
        database.
        This class should not be used directly unless for subclassing.
        Use higher-level DjangoAuthorizer class instead.
        """

        def __init__(self, anonymous_user=None):
#            if os.geteuid() != 0 or not spwd.getspall():
#                raise AuthorizerError("super user privileges are required")
            self.anonymous_user = anonymous_user

            if self.anonymous_user is not None:
                if not self.anonymous_user in self._get_system_users():
                    raise ValueError('no such user %s' % self.anonymous_user)
#                try:
#                    return pwd.getpwnam(self.anonymous_user).pw_dir
#                except KeyError:
#                    raise ValueError('no such user %s' % username)

          
        # --- overridden / private API

        def validate_authentication(self, username, password):
            """ Authenticate agains Django ftpauth api.
            """
            if username == "anonymous":
                return self.anonymous_user is not None
            try:
                import simplejson as json
                import urllib2
                ftp_auth_request = urllib2.urlopen('http://localhost:8000/ftpauth/%s/%s/' % (username, password))
                ftp_auth = json.load(ftp_auth_request)
                print ftp_auth
            except:  # url access failed
                return False
            else:
                return ftp_auth['status'] == 'ok'

        def impersonate_user(self, username, password):
            """Change process effective user/group ids to reflect
            logged in user.
            """
            try:
                pwdstruct = pwd.getpwnam("nobody")
            except KeyError:
                raise AuthorizerError('no such user %s' % pwdstruct)
            else:
                os.setegid(pwdstruct.pw_gid)
                os.seteuid(pwdstruct.pw_uid)
                
        def terminate_impersonation(self, username):
            """Revert process effective user/group IDs."""
            os.setegid(PROCESS_GID)
            os.seteuid(PROCESS_UID)

        @replace_anonymous
        def has_user(self, username):
            """Return True if user exists on the Unix system.
            If the user has been black listed via allowed_users or
            rejected_users options always return False.
            """
            if self.BaseDjangoAuthorizer.validate_authentication(self, username, password):
                return username

        @replace_anonymous
        def get_home_dir(self, username):
            """Return user home directory."""
            try:
                homedir = ('/home/%s/' % (username))
                return homedir
            except KeyError:
                raise AuthorizerError('no such user %s or directory' % username)

        def get_msg_login(self, username):
            return "Login successful."

        def get_msg_quit(self, username):
            return "Goodbye."

        def get_perms(self, username):
            return "elradfmw"

        def has_perm(self, username, perm, path=None):
            return perm in self.get_perms(username)


    class DjangoAuthorizer(_Base, BaseDjangoAuthorizer):
        """A wrapper on top of BaseDjangoAuthorizer providing options
        
        Example usages:

         >>> from pyftpdlib.contrib.authorizers import DjangoAuthorizer
         >>> # accept all user
         >>> auth = DjangoAuthorizer()
         """

        # --- public API

        def __init__(self, global_perm="elradfmw",
                           allowed_users=[],
                           rejected_users=[],
                           require_valid_shell=True,
                           anonymous_user=None,
                           msg_login="Login successful.",
                           msg_quit="Goodbye."):
            """Parameters:

             - (string) global_perm:
                a series of letters referencing the users permissions;
                defaults to "elradfmw" which means full read and write
                access for everybody (except anonymous).

             - (list) allowed_users:
                a list of users which are accepted for authenticating
                against the FTP server; defaults to [] (no restrictions).

             - (list) rejected_users:
                a list of users which are not accepted for authenticating
                against the FTP server; defaults to [] (no restrictions).

             - (bool) require_valid_shell:
                Deny access for those users which do not have a valid shell
                binary listed in /etc/shells.
                If /etc/shells cannot be found this is a no-op.
                Anonymous user is not subject to this option, and is free
                to not have a valid shell defined.
                Defaults to True (a valid shell is required for login).

             - (string) anonymous_user:
                specify it if you intend to provide anonymous access.
                The value expected is a string representing the system user
                to use for managing anonymous sessions;  defaults to None
                (anonymous access disabled).

             - (string) msg_login:
                the string sent when client logs in.

             - (string) msg_quit:
                the string sent when client quits.
            """
            BaseDjangoAuthorizer.__init__(self, anonymous_user)
            self.global_perm = global_perm
            self.allowed_users = allowed_users
            self.rejected_users = rejected_users
            self.anonymous_user = anonymous_user
            self.require_valid_shell = require_valid_shell
            self.msg_login = msg_login
            self.msg_quit = msg_quit

            self._dummy_authorizer = DummyAuthorizer()
            self._dummy_authorizer._check_permissions('', global_perm)
            _Base.__init__(self)
            if require_valid_shell:
                for username in self.allowed_users:
                    if not self._has_valid_shell(username):
                        raise ValueError("user %s has not a valid shell"
                                         % username)

        def override_user(self, username, password=None, homedir=None, perm=None,
                          msg_login=None, msg_quit=None):
            """Overrides the options specified in the class constructor
            for a specific user.
            """
            if self.require_valid_shell and username != 'anonymous':
                if not self._has_valid_shell(username):
                    raise ValueError("user %s has not a valid shell"
                                     % username)
            _Base.override_user(self, username, password, homedir, perm,
                                msg_login, msg_quit)

        # --- overridden / private API

        def validate_authentication(self, username, password):
            if username == "anonymous":
                return self.anonymous_user is not None
            if self._is_rejected_user(username):
                return False
            if self.require_valid_shell and username != 'anonymous':
                if not self._has_valid_shell(username):
                    return False
            overridden_password = self._get_key(username, 'pwd')
            if overridden_password:
                return overridden_password == password

            return BaseDjangoAuthorizer.validate_authentication(self, username, password)

        @replace_anonymous
        def has_user(self, username):
            if BaseDjangoAuthorizer.validate_authentication(self, username, password):
                return username

        @replace_anonymous
        def get_home_dir(self, username):
            overridden_home = self._get_key(username, 'home')
            if overridden_home:
                return overridden_home
            return BaseDjangoAuthorizer.get_home_dir(self, username)
        
        #need refactor
        @staticmethod
        def _has_valid_shell(username):
            """Return True if the user has a valid shell binary listed
            in /etc/shells. If /etc/shells can't be found return True.
            """
            try:
                file = open('/etc/shells', 'r')
            except IOError, err:
                if err.errno == errno.ENOENT:
                    return True
                raise
            else:
                try:
                    shell = "/bin/bash"
                    for line in file:
                        if line.startswith('#'):
                            continue
                        line = line.strip()
                        if line == shell:
                            return True
                    return False
                finally:
                    file.close()