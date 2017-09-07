from __future__ import with_statement
from fabric.api import env, cd, lcd, local, run

env.user = 'muden'
env.hosts = ['s17.wservices.ch']

local_user = 'mloeks'
git_user = 'matze09'
app_name = 'rtg'

## constant fields
DEMO_APP = {
    'name': '%s_demo' % app_name,
    'dir': '${HOME}/%s_demo' % app_name,
    'requirements': 'production',
    'manage_script': 'manage_test',
    'backup_script': '${HOME}/scripts/%s_demo/backup.sh %s_demo' % (app_name, app_name),
}
PROD_APP = {
    'name': app_name,
    'dir': '${HOME}/%s' % app_name,
    'requirements': 'production',
    'manage_script': 'manage_prod',
    'backup_script': '${HOME}/scripts/%s/backup.sh %s' % (app_name, app_name),
}
LOCAL_APP = {
    'name': app_name,
    'dir': '${HOME}/dev/bitbucket/%s' % app_name,
    'requirements': 'local',
    'manage_script': 'manage',
    'backup_script': '',
}

REMOTE_BACKUP_DIR = "${HOME}/backups"
GIT_URL = 'git@bitbucket.org:%s/%s.git' % (git_user, app_name)


def deploy_demo():
    print("Starting DEMO Deployment...")
    deploy(DEMO_APP)


def deploy_prod():
    print("Starting PROD Deployment...")
    deploy(PROD_APP)


def deploy(app_env):
    project_name = app_env['name']

    try:
        print("Remote project backup...")
        run('bash ' + app_env['backup_script'])

        print("Remote SCM checkout of latest revision...")
        run('rm -rf /tmp/%s' % project_name)
        run('git clone %s /tmp/%s' % (GIT_URL, project_name,))
        run('rm -rf /tmp/%s/deployment' % project_name)
        run('rm -rf /tmp/%s/fabfile.py' % project_name)
        run('rm -rf /tmp/%s/README.md' % project_name)

        print("Keeping media files and meta files of existing app...")
        with cd(app_env['dir']):
            run('cp -rf media /tmp/%s' % project_name)
            run('cp -rf .htpasswd /tmp/%s' % project_name)
            run('cp -rf RUN /tmp/%s' % project_name)
            run('cp -rf %s.pid /tmp/%s' % (project_name, project_name))
            run('cp -rf %s.sock /tmp/%s' % (project_name, project_name))

        print("Stopping " + project_name + " app server...")
        run('${HOME}/init/%s stop' % project_name)

        print("Replacing " + project_name + " app with freshly checked out project")
        with cd(app_env['dir']):
            run('rm -rf %s/* 2>/dev/null' % app_name)
            run('rsync -aC /tmp/%s/* .' % project_name)

        print("Updating pip requirements...")
        with cd(app_env['dir']):
            run('${HOME}/v/%s/bin/pip install -r requirements/%s.txt' % (app_name, app_env['requirements'],))

        print("Collecting static files...")
        with cd(app_env['dir']):
            run('${HOME}/v/%s/bin/python %s.py collectstatic -v0 --noinput' % (app_name, app_env['manage_script'],))

        print("Applying database migrations...")
        with cd(app_env['dir']):
            run('${HOME}/v/%s/bin/python %s.py migrate' % (app_name, app_env['manage_script'],))

        print("Starting " + project_name + " app server...")
        run('${HOME}/init/%s start' % project_name)

        print("Restarting " + project_name + " web server...")
        run('${HOME}/init/nginx stop')
        run('${HOME}/init/nginx start')

        print(project_name + " Deployment finished succesfully!")
    finally:
        # deployment_cleanup(app_env)
        pass


def deployment_cleanup(app_env):
    print("Cleaning up...")
    run('rm -rf /tmp/%s' % app_env['name'])
    run('rm -rf /tmp/%s*.dump' % app_env['name'])
