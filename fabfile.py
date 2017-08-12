from __future__ import with_statement
from fabric.api import env, cd, lcd, local, run

env.user = 'muden'
env.hosts = ['s17.wservices.ch']

local_user = 'mloeks'
svn_user = local_user
app_name = 'rtg'

## constant fields
DEMO_APP = {
    'name': '%s_demo' % app_name,
    'dir': '/home/%s/%s_demo' % (env.user, app_name,),
    'requirements': 'production',
    'manage_script': 'manage_test',
    'backup_script': '/home/%s/scripts/%s_demo/backup.sh' % (env.user, app_name),
}
PROD_APP = {
    'name': app_name,
    'dir': '/home/%s/%s' % (env.user, app_name,),
    'requirements': 'production',
    'manage_script': 'manage_prod',
    'backup_script': '/home/%s/scripts/%s/backup.sh' % (env.user, app_name),
}
LOCAL_APP = {
    'name': app_name,
    'dir': '/home/%s/projects/%s/lcube/%s' % (local_user, local_user, app_name,),
    'requirements': 'local',
    'manage_script': 'manage',
    'backup_script': '',
}

REMOTE_BACKUP_DIR = "/home/%s/backups" % env.user
SVN_BASE_URL = 'https://srv55.svn-repos.de/dev897/%s/%s' % (svn_user, app_name)


def run_tests_local():
    with lcd(LOCAL_APP['dir']):
        print("Running tests...")
        local('/home/%s/pyve/%s/bin/python rtg/manage.py test rtg' % (local_user, app_name))


def svn_commit():
    run_tests_local()
    with lcd(LOCAL_APP['dir']):
        print("Committing changes to SVN...")
        local('svn ci -m "%s AUTOCOMMIT during deployment"' % app_name)


def deploy_demo():
    print("Starting DEMO Deployment...")
    deploy(DEMO_APP)


def deploy_prod():
    print("Starting PROD Deployment...")
    deploy(PROD_APP)


def deploy(app_env):
    try:
        print("Remote project backup...")
        run('bash ' + app_env['backup_script'])

        print("Remote checkout of latest revision...")
        run('rm -rf /tmp/rtg')
        run('svn checkout --username %s %s /tmp/%s' % (svn_user, SVN_BASE_URL, app_name,))

        print("Keeping media files of existing app...")
        with cd(app_env['dir']):
            run('cp -rf %s/media /tmp/%s/rtg' % (app_name, app_name,))

        print("Stopping " + app_env['name'] + " app server...")
        run('${HOME}/init/%s stop' % app_env['name'])

        print("Replacing " + app_env['name'] + " app with freshly checked out project")
        with cd(app_env['dir']):
            run('rm -rf %s' % app_name)
            run('rsync -aC /tmp/%s/rtg .' % app_name)
            run('rsync -aC /tmp/%s/requirements .' % app_name)

        print("Updating pip requirements...")
        with cd(app_env['dir']):
            run('${HOME}/v/%s/bin/pip install -r requirements/%s.txt' % (app_name, app_env['requirements'],))

        print("Collecting static files...")
        with cd('%s/%s' % (app_env['dir'], app_name,)):
            run('${HOME}/v/%s/bin/python %s.py collectstatic -v0 --noinput' % (app_name, app_env['manage_script'],))

        print("Applying database migrations...")
        with cd('%s/%s' % (app_env['dir'], app_name,)):
            run('${HOME}/v/%s/bin/python %s.py migrate' % (app_name, app_env['manage_script'],))

        # TODO geht nicht weil ich keine Rechte zum erstellen/droppen von DBs habe...
        # print("Running tests remotely...")
        # with cd(app_version['dir']):
        #     run('${HOME}/v/%s/bin/python manage_prod.py test' % app_name)

        print("Starting " + app_env['name'] + " app server...")
        run('${HOME}/init/%s start' % app_env['name'])

        print("Restarting " + app_env['name'] + " web server...")
        run('${HOME}/init/nginx stop')
        run('${HOME}/init/nginx start')

        print(app_env['name'] + " Deployment finished succesfully!")
    finally:
        deployment_cleanup()


def deployment_cleanup():
    print("Cleaning up...")
    local('rm -rf /tmp/rtg')
    local('rm -rf /tmp/rtg*.dump')
    run('rm -rf /tmp/rtg')
    run('rm -rf /tmp/rtg*.dump')
