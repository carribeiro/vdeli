# sample test code

from celery.decorators import task

@task()
def add(x, y):
    return x + y

# code to run a task with a lock from inside django. copied from:
# http://docs.celeryproject.org/en/v2.2.5/cookbook/tasks.html#ensuring-a-task-is-only-executed-one-at-a-time

from celery.task import Task
from django.core.cache import cache
from django.utils.hashcompat import md5_constructor as md5
from models import VideoFile
from django.contrib.auth.models import User

LOCK_EXPIRE = 60 * 5 # Lock expires in 5 minutes

class VideoFileImporter(Task):
    name = "videofile.import"

    def run(self, video_file_name, **kwargs):
        logger = self.get_logger(**kwargs)

        # The cache key consists of the task name and the MD5 digest
        # of the video file name.
        video_file_name_digest = md5(feed_url).hexdigest()
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

            finally:
                release_lock()
            return video_file.id, video_file.file_name

        logger.debug(
            "Video file %s is already being imported by another worker" % (
                video_file_name))
        return