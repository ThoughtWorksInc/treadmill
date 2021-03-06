"""Configures NFS inside the container."""

from treadmill.runtime.linux.image import fs as image_fs


class NFSFilesystemPlugin(image_fs.FilesystemPluginBase):
    """Mounts nfs based on container environment."""
    def __init__(self, tm_env):
        super(NFSFilesystemPlugin, self).__init__(tm_env)

    def init(self):
        """Pre mount NFS shares for private nfs namespace to a Treadmill known
        location.

        This is done to avoid NFS delays at container create time."""
        pass

    def configure(self, root_dir, app):
        pass
