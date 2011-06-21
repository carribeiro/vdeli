# code to run a task with a lock from inside django. copied from:
# http://docs.celeryproject.org/en/v2.2.5/cookbook/tasks.html#ensuring-a-task-is-only-executed-one-at-a-time

import paramiko
import datetime
import os.path

from celery.decorators import periodic_task
from celery.task import Task, task
from django.contrib.auth.models import User
from django.core.cache import cache
from django.utils.hashcompat import md5_constructor as md5
from paramiko.ssh_exception import SSHException
from videorepo.models import CDNServer, Logfile
from videorepo.models import VideoFile, TransferQueue


LOCK_EXPIRE = 60 * 5 # Lock expires in 5 minutes

class VideoFileImporter(Task):
    name = "videofile.import"

    def run(self, video_file_name, **kwargs):
        logger = self.get_logger(**kwargs)

        # The cache key consists of the task name and the MD5 digest
        # of the video file name.
        video_file_name_digest = md5(video_file_name).hexdigest()
        lock_id = "%s-lock-%s" % (self.name, video_file_name_digest)

        # cache.add fails if if the key already exists
        acquire_lock = lambda: cache.add(lock_id, "true", LOCK_EXPIRE)
        # memcache delete is very slow, but we have to use it to take
        # advantage of using add() for atomic locking
        release_lock = lambda: cache.delete(lock_id)

        logger.debug("Importing video file: %s" % video_file_name)
        if acquire_lock():
            try:
                import time
                import os
                import settings

                # check if the file is in the publisher/project/(...)/video_file format
                # it has to have at least two dirs before the file
                relative_video_file_name = os.path.relpath(video_file_name, settings.MEDIA_ROOT)
                path, file_name = os.path.split(relative_video_file_name)
                path_elements = path.split('/')

                # trivial tests regarding the path
                if len(path_elements) == 0:
                    # video file at the root
                    logger.debug("Video file %s is at the root of the file repository and cannot be distributed" % video_file_name)
                    return
                elif path_elements[0] == "..":
                    # path is not inside MEDIA_ROOT
                    logger.debug("Video file %s is not inside the file repository and cannot be distributed" % video_file_name)
                    return

                # test the publisher
                try:
                    publisher = User.objects.get(username=path_elements[0])
                except:
                    # first element is not a valid publisher
                    logger.debug("Video file %s is not stored inside a publisher dir and cannot be distributed" % video_file_name)
                    return
                if len(path_elements) == 1:
                    # only the publisher was provided, but without a project - can't distribute the file
                    logger.debug("Video file %s from publisher %s is not associated "\
                        "with a project and cannot be distributed" % (video_file_name, path_elements[0]))

                # test the project                
                video_projects = dict((video_project.name, video_project) for video_project in publisher.videoproject_set.all())
                if path_elements[1] not in video_projects:
                    # second element is not a valid project from that publisher (obs: case sensitive)
                    logger.debug("Video file %s from publisher %s does not have a project named %s "\
                        "and cannot be distributed" % (video_file_name, path_elements[0], path_elements[1]))

                # creates the video file object    
                video_file = VideoFile.from_file_name(video_file_name, video_projects[path_elements[1]])
                video_file.save()

                # create the transfer entries to all servers in the region
                # ideally it should be a celery subtask

                # for all policies, list the servers in the region. but never add a server twice.
                servers = {}
                print video_file.project
                print video_file.project.projectpolicy_set.all()
                for policy in video_file.project.projectpolicy_set.all():
                    for server in policy.cdnregion.cdnserver_set.all():
                        if server.node_name not in servers:
                            servers[server.node_name] = (server, policy)
                print "SERVERS:", servers.keys()
                # for each servers, put a new transfer in the queue using the correct parameters
                for server, policy in servers.values():
                    print "vf %d: server:%s, region:%s, transfer:%s" % (
                        video_file.id, server.node_name, policy.cdnregion.region_name, policy.transfer_method)
                    tq = TransferQueue(
                        video_file=video_file,
                        server=server,
                        transfer_method=policy.transfer_method,
                        transfer_status="not scheduled",
                        protocol=policy.protocol,
                        max_simultaneous_segments=policy.max_simultaneous_segments,
                        segment_size_kb=policy.segment_size_kb,
                        max_bandwidth_kbps=policy.max_bandwidth_per_segment_kbps,
                        percentage_transferred=0,
                        )
                    tq.save()
            finally:
                release_lock()
            return video_file.id, video_file.file_name

        logger.debug(
            "Video file %s is already being imported by another worker" % (
                video_file_name))
        return

class TransferQueueCallBack(object):
    def __init__(self, tq):
        self.tq = tq

    def transfer_callback(self, bytes_transferred, bytes_total):
        try:
            self.tq.percentage_transferred = int((100.0 * bytes_transferred) / bytes_total)
        except:
            self.tq.percentage_transferred = 0
        self.tq.save()

@periodic_task(run_every=datetime.timedelta(minutes=1), name="videofile.transfer_one_file")
def process_transfer_queue():

#    # get the first entry on the transfer queue and handle it
#    try:
#        tq = TransferQueue.objects.filter(transfer_status='not scheduled')[0]
#    except:
#        return "no transfer to be done"

#     do one single transfer

    for tq in TransferQueue.objects.filter(transfer_status='not scheduled')[0]:
        source = str(tq.video_file.file_name)
        tq.transfer_status='processing'
        tq.save()
        path, file_name = os.path.split(source)
        path, project = os.path.split(path)
        user_dir = os.path.join("/srv/vdeli/cdnserver/data", tq.video_file.project.user.username)
        project_dir = os.path.join(user_dir, project)
        destination = os.path.join(project_dir, file_name)
    
        print "Trying to connect to the host %s:%d" % (tq.server.ip_address, tq.server.server_port)
        error = None
        try:
            transport = paramiko.Transport((tq.server.ip_address, tq.server.server_port))
            transport.connect(username=tq.server.username, password=tq.server.password)
            sftp = paramiko.SFTPClient.from_transport(transport)

            # Check base dirs
            try:
                if not 'vdeli' in sftp.listdir('/srv'):
                    print 'Not vdeli'
                    prj_path = '/srv'
                    for dir in ['vdeli', 'cdnserver', 'data']:
                        prj_path = '%s/%s' % (prj_path, dir)
                        try:
                            sftp.mkdir(prj_path)
                        except IOError:
                            error = 'Can\'t create project dirs: %s. Permission denied.' % \
                            prj_path
                            break
                if not 'cdnserver' in sftp.listdir('/srv/vdeli'):
                    prj_path = '/srv/vdeli'
                    for dir in ['cdnserver', 'data']:
                        prj_path = '%s/%s' % (prj_path, dir)
                        try:
                            sftp.mkdir(prj_path)
                        except IOError:
                            error = 'Can\'t create project dirs: %s. Permission denied.' % \
                            prj_path
                            break
                if not 'data' in sftp.listdir('/srv/vdeli/cdnserver'):
                    try:
                        sftp.mkdir('/srv/vdeli/cdnserver/data')
                    except IOError:
                        error = 'Can\'t create project dirs: %s. Permission denied.' % \
                            '/srv/vdeli/cdnserver/data'
    
                if not tq.video_file.project.user.username in sftp.listdir('/srv/vdeli/cdnserver/data'):
                    try:
                        sftp.mkdir(user_dir)
                    except IOError:
                        error = 'Can\'t create project dirs: %s. Permission denied.' % \
                            user_dir
    
                if not project in sftp.listdir(user_dir):
                    try:
                        sftp.mkdir(project_dir)
                    except IOError:
                        error = 'Can\'t create project dirs: %s. Permission denied.' % \
                            project_dir
            except IOError:
                if error is None:
                    error = 'IOError'

        except SSHException:
            error = 'No route to host %s' % tq.server.ip_address
        if error is None:
            print "Copying file %s to the %s" % (source, destination)
            tq_call_back = TransferQueueCallBack(tq)
            sftp.put(source, destination, callback=tq_call_back.transfer_callback)
            sftp.close()
            tq.transfer_status = 'transferred'
        else:
            tq.transfer_status = 'failed'
            tq.last_error_msg = error
        transport.close()
        tq.save()

#        print "SFTP %s -> %s" % (source, destination)
#        error = 'unknown error'
#        try:
#            transport = paramiko.Transport((host, port))
#            try:
#                transport.connect(username=username, password=password)
#                sftp = paramiko.SFTPClient.from_transport(transport)
#                try:
#                    try:
#                        print "mkdir %s" % user_dir, sftp.mkdir(user_dir)
#                    except:
#                        pass
#                    try:
#                        print "mkdir %s" % project_dir, sftp.mkdir(project_dir)
#                    except:
#                        pass
#                    try:
#    

#    
#                        print "sftp" % sftp.put(source, destination, callback=transfer_callback)
#                    except:
#                        pass
#                except:
#                    error = 'SFTP put failed'
#                finally:
#                    sftp.close()
#            except:
#                error = 'connect failed'
#            finally:
#                transport.close()
#            tq.transfer_status = 'transferred'
#            tq.save()
#        except:
#            tq.transfer_status = error
#            tq.save()
    
        #ssh = paramiko.SSHClient()
        #ssh.connect(server.ip_address, username=username, password=password)
        #ssh_stdin, ssh_stdout, ssh_stderr = ssh_session.exec_command("ftpget ")

@task
def copy_nginx_logfiles(local_time='00:15', cdnmanager_logfiles_path=None):
    port = 22
    # the logfiles are copied in a three step process

    # step 1: create all the Logfile entries, with status as 'notcopied'
    dt = datetime.datetime.now()
    for server in CDNServer.objects.get_servers_by_localtime(local_time):
        logfile = Logfile(server=server, status='notcopied', timestamp=CDNServer.objects.localtime_for_timezone(dt, server.timezone))
        logfile.save()

    # step 2: loop over all 'notcopied' logfiles. this will include all
    # new Logfile entries created in the preceding step, and also any
    # entries that were created before (either a previous call to 
    # copy_nginx_logfiles or manually) and that are still 'notcopied'.
    for logfile in Logfile.objects.filter(status='notcopied'):
        # retrieve the log file using paramiko
        error = None
        try:
            transport = paramiko.Transport((logfile.server.ip_address, port))
            try:
                transport.connect(username=logfile.server.username, password=logfile.server.password)
                sftp = paramiko.SFTPClient.from_transport(transport)
    
                # Check the remote file exists
                try:
                    sftp.stat(logfile.cdnserver_filename())
                except IOError:
                    error = 'Remote file doesn\'t exists'
    
                # Copy a remote file
                if error is None:
                    try:
                        # mark the file as being copied
                        logfile.status = 'copying'
                        if cdnmanager_logfiles_path is None:
                            local_path = logfile.cdnmanager_filename()
                        else:
                            local_path = '%s/%s' % (cdnmanager_logfiles_path, logfile.cdnmanager_filename().split('/')[-1])
                        print "SFTP %s -> %s" % (logfile.cdnserver_filename(), local_path)
                        sftp.get(logfile.cdnserver_filename(), local_path)
                        print 'File %s copied!' % logfile.cdnserver_filename()
                        sftp.close()
                        transport.close()
                        logfile.logfile = local_path
                        logfile.save()
                    except IOError:
                        error = 'Local path is not a file or connection problem'
            except:
                error = 'Connection failed'

        except SSHException:
            error = 'No route to host %s' % logfile.server.ip_address
        
        if error is not None:
            # if the transfer fails, increase retry count, and go to the next file
            logfile.copy_retry_count += 1
            logfile.last_error_msg = error
            logfile.status = 'notcopied'
            logfile.save()
        else:
            # if the transfer is ok, set status of the logfile as "copied"
            logfile.status = 'copied'
            logfile.last_error_msg = None
            logfile.save()

    # step 3: loop over all 'copied' logfiles. this will include logfiles
    # that were copied in step 2 and also any files which were copied before
    # but still not processed for any reason.
    for logfile in Logfile.objects.filter(status='copied'):
        # change the status of the logfile to "filtering"
        #logfile.status = 'filtering'
        #logfile.save()
        pass

        # unpack the file, and read it line by line

        # separate lines per each customer (it's the first item on the URL)

        # when finished, set logfile.status = 'completed' or 'ok'
        #logfile.status = 'completed'
        #logfile.save()

