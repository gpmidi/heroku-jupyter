try:
    import os
    import json
    import traceback
    import IPython.lib
    from hybridcontents import HybridContentsManager
    # from s3contents import S3ContentsManager, GCSContentsManager
    from pgcontents.pgmanager import PostgresContentsManager
    # LargeFileManager is the default Jupyter content manager
    # NOTE: LargFileManager only exists in notebook > 5
    # If using notebook < 5, use FileContentManager instead
    from notebook.services.contents.largefilemanager import LargeFileManager

    c = get_config()

    ### Password protection ###
    # http://jupyter-notebook.readthedocs.io/en/latest/security.html
    if os.environ.get('JUPYTER_NOTEBOOK_PASSWORD_DISABLED') != 'DangerZone!':
        passwd = os.environ['JUPYTER_NOTEBOOK_PASSWORD']
        c.NotebookApp.password = IPython.lib.passwd(passwd)
    else:
        c.NotebookApp.token = ''
        c.NotebookApp.password = ''

    ### PostresContentsManager ###
    database_url = os.getenv('DATABASE_URL', None)
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    if database_url:
        # Tell IPython to use PostgresContentsManager for all storage.
        c.NotebookApp.contents_manager_class = HybridContentsManager

        c.HybridContentsManager.manager_classes = {
            # # Associate the root directory with a LargeFileManager,
            # # This manager will receive all requests that don't fall under any of the
            # # other managers.
            # # If you want to make this path un-editable you can configure it to use a read-only filesystem
            # '': LargeFileManager,
            # # Associate /directory with a LargeFileManager.
            # 'directory': LargeFileManager,
            # Associate the postgres directory with a PostgresContentManager
            'postgres': PostgresContentsManager,
            # # Associate the s3 directory with AWS S3
            # 's3': S3ContentsManager,
            # # Associate the gcs directory with GCS
            # 'gcs': GCSContentsManager
        }

        c.HybridContentsManager.manager_kwargs = {
            # # Args for the LargeFileManager mapped to /directory
            # '': {
            #     'root_dir': '/tmp/read-only',
            # },
            # # Args for the LargeFileManager mapped to /directory
            # 'directory': {
            #     'root_dir': '/home/viaduct/local_directory',
            # },
            # Args for  PostgresContentsManager.
            'postgres': {
                'db_url': database_url,
                'max_file_size_bytes': 1024*1024*1024*2,  # Optional
            },
            # # Args for  S3ContentManager.
            # 's3': {
            #     "access_key_id": os.environ.get("AWS_ACCESS_KEY_ID"),
            #     "secret_access_key": os.environ.get("AWS_SECRET_ACCESS_KEY"),
            #     "endpoint_url": os.environ.get("AWS_ENDPOINT_URL"),
            #     "bucket": "my-remote-data-bucket",
            #     "prefix": "s3/prefix"
            # },
            # # Args for  GCSContentManager.
            # 'gcs': {
            #     'project': "<your-project>",
            #     'token': "~/.config/gcloud/application_default_credentials.json",
            #     'bucket': "<bucket-name>"
            # },
        }

    def no_spaces(path):
        return ' ' not in path

    c.HybridContentsManager.path_validators = {
        'postgres': no_spaces,
        # 's3': no_spaces
    }

except Exception:
    traceback.print_exc()
    # if an exception occues, notebook normally would get started
    # without password set. For security reasons, execution is stopped.
    exit(1)
