from os import path
from datetime import datetime

from fabric.context_managers import settings
from fabric.contrib import files
from fabric.operations import require
from fabric.state import env
from fabric import utils

from dye import fablib


# do all this just to override link_webserver_conf
def deploy(revision=None, keep=None, full_rebuild=True):
    """ update remote host environment (virtualenv, deploy, update)

    It takes three arguments:

    * revision is the VCS revision ID to checkout (if not specified then
      the latest will be checked out)
    * keep is the number of old versions to keep around for rollback (default
      5)
    * full_rebuild is whether to do a full rebuild of the virtualenv
    """
    require('server_project_home', provided_by=env.valid_envs)
    env.python_bin = path.join('/', 'usr', 'bin', 'python')

    # this really needs to be first - other things assume the directory exists
    fablib._create_dir_if_not_exists(env.server_project_home)

    # if the <server_project_home>/previous/ directory doesn't exist, this does
    # nothing
    fablib._migrate_directory_structure()
    fablib._set_vcs_root_dir_timestamp()

    fablib.check_for_local_changes(revision)
    # TODO: check for deploy-in-progress.json file
    # also check if there are any directories newer than current ???
    # might just mean we did a rollback, so maybe don't bother as the
    # deploy-in-progress should be enough
    # _check_for_deploy_in_progress()

    # TODO: create deploy-in-progress.json file
    # _set_deploy_in_progress()
    fablib.create_copy_for_next()
    fablib.checkout_or_update(in_next=True, revision=revision)
    # remove any old pyc files - essential if the .py file is removed by VCS
    if env.project_type == "django":
        fablib.rm_pyc_files(path.join(env.next_dir, env.relative_django_dir))
    # create the deploy virtualenv if we use it
    fablib.create_deploy_virtualenv(in_next=True, full_rebuild=full_rebuild)

    # we only have to disable this site after creating the rollback copy
    # (do this so that apache carries on serving other sites on this server
    # and the maintenance page for this vhost)
    downtime_start = datetime.now()
    link_webserver_conf(maintenance=True)
    with settings(warn_only=True):
        fablib.webserver_cmd('reload')
    # TODO: do a database dump in the old directory
    fablib.point_current_to_next()

    # Use tasks.py deploy:env to actually do the deployment, including
    # creating the virtualenv if it thinks it necessary, ignoring
    # env.use_virtualenv as tasks.py knows nothing about it.
    fablib._tasks('deploy:' + env.environment)

    # bring this vhost back in, reload the webserver and touch the WSGI
    # handler (which reloads the wsgi app)
    link_webserver_conf()
    fablib.webserver_cmd('reload')
    downtime_end = datetime.now()
    fablib.touch_wsgi()

    fablib.delete_old_rollback_versions(keep)
    if env.environment == 'production':
        fablib.setup_db_dumps()

    # TODO: _remove_deploy_in_progress()
    # move the deploy-in-progress.json file into the old directory as
    # deploy-details.json
    fablib._report_downtime(downtime_start, downtime_end)


def link_webserver_conf(maintenance=False):
    """link the webserver conf file"""
    require('vcs_root_dir', provided_by=env.valid_envs)
    if env.webserver is None:
        return
    # TODO: if you want to deploy this separate to opencontracting then
    # you need to uncomment various lines below
    # create paths in the vcs checkout
    vcs_config_stub = path.join(env.vcs_root_dir, env.webserver, env.environment)
    vcs_config_live = vcs_config_stub + '.conf'
    vcs_config_include = vcs_config_stub + '_include.conf'

    # create paths in the webserver config
    webserver_conf = _webserver_conf_path()
    webserver_include = _webserver_include_path()

    # ensure the includes dir exists
    webserver_include_dir = '/etc/apache2/sites-available/includes'
    fablib._create_dir_if_not_exists(webserver_include_dir)

    # ensure the main file is linked properly
    if not files.exists(vcs_config_live):
        utils.abort('No %s conf file found - expected %s' %
                (env.webserver, vcs_config_live))
    fablib._delete_file(webserver_conf)
    fablib._link_files(vcs_config_live, webserver_conf)

    # now manage the include file
    if maintenance:
        fablib._delete_file(webserver_include)
    else:
        if not files.exists(vcs_config_include):
            utils.abort('No %s conf file found - expected %s' %
                    (env.webserver, vcs_config_include))
        fablib._delete_file(webserver_include)
        fablib._link_files(vcs_config_include, webserver_include)

    # debian has sites-available/sites-enabled split with links
    if fablib._linux_type() == 'debian':
        webserver_conf_enabled = webserver_conf.replace('available', 'enabled')
        fablib._link_files(webserver_conf, webserver_conf_enabled)
    fablib.webserver_configtest()


def _webserver_include_path():
    webserver_conf_dir = {
        'apache_redhat': '/etc/httpd/conf.d/includes',
        'apache_debian': '/etc/apache2/sites-available/includes',
    }
    key = env.webserver + '_' + fablib._linux_type()
    if key in webserver_conf_dir:
        return path.join(webserver_conf_dir[key],
            '%s_%s.conf' % (env.project_name, env.environment))
    else:
        utils.abort('webserver %s is not supported (linux type %s)' %
                (env.webserver, fablib._linux_type()))


def _webserver_conf_path():
    require('webserver', 'project_name', provided_by=env.valid_envs)
    webserver_conf_dir = {
        'apache_redhat': '/etc/httpd/conf.d',
        'apache_debian': '/etc/apache2/sites-available',
    }
    key = env.webserver + '_' + fablib._linux_type()

    if key in webserver_conf_dir:
        return path.join(webserver_conf_dir[key],
            '%s.conf' % (env.environment))
    else:
        utils.abort('webserver %s is not supported (linux type %s)' %
                (env.webserver, fablib._linux_type()))
