# basic ftpserver config
import os.path

FTP_VERSION = "0.1 alpha"
FTP_BANNER = "VDN FTP Server %s ready" % FTP_VERSION
FTP_AUTH_ADDRESS = "_AUTH_SERVER_"
FTP_HOME_DIR = os.path.join("_VDELIHOME_", "cdnmanager/cdnmanager/cdn/uploads")
