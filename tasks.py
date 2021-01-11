import os
from fabric import Connection
from invoke import task

CONN = Connection(user='muden', host='s17.wservices.ch')

local_user = 'mloeks'
git_user = 'mloeks'
app_name = 'rtg'

## constant fields
DEMO_APP = {
    'name': '%s_demo' % app_name,
    'dir': '${HOME}/%s_demo' % app_name,
    'requirements': 'production',
    'manage_script': 'manage_test',
    'backup_script': '${HOME}/scripts/%s/backup/backup.sh %s_demo' % (app_name, app_name),
}
PROD_APP = {
    'name': app_name,
    'dir': '${HOME}/%s' % app_name,
    'requirements': 'production',
    'manage_script': 'manage_prod',
    'backup_script': '${HOME}/scripts/%s/backup/backup.sh %s' % (app_name, app_name),
}
LOCAL_APP = {
    'name': app_name,
    'dir': '${HOME}/dev/%s' % app_name,
    'requirements': 'local',
    'manage_script': 'manage',
    'backup_script': '',
}

REMOTE_BACKUP_DIR = "${HOME}/backups"
GIT_URL = 'git@github.com:%s/%s.git' % (git_user, app_name)


@task
def deploy_demo(context):
    print("Starting DEMO Deployment...")
    # TODO this feels like the context variable is not used as intended ;-)
    deploy(CONN, DEMO_APP)


@task
def deploy_prod(context):
    print("Starting PROD Deployment...")
    deploy(CONN, PROD_APP)


def deploy(ctx, app_env):
    project_name = app_env['name']

    try:
        print("Remote project backup...")
        ctx.run('bash ' + app_env['backup_script'])

        print("Remote SCM checkout of latest revision...")
        ctx.run('rm -rf /tmp/%s' % project_name)
        ctx.run('git clone %s /tmp/%s' % (GIT_URL, project_name,))
        ctx.run('rm -rf /tmp/%s/deployment' % project_name)
        ctx.run('rm -rf /tmp/%s/fabfile.py' % project_name)  # deprecated, remove for backwards compatibility
        ctx.run('rm -rf /tmp/%s/tasks.py' % project_name)
        ctx.run('rm -rf /tmp/%s/README.md' % project_name)

        print("Keeping media files and meta files of existing app...")
        with ctx.cd(app_env['dir']):
            ctx.run('cp -rf media /tmp/%s' % project_name)
            ctx.run('cp -rf .htpasswd /tmp/%s' % project_name)
            ctx.run('cp -rf RUN /tmp/%s' % project_name)
            ctx.run('cp -rf %s.pid /tmp/%s 2>/dev/null' % (project_name, project_name))
            ctx.run('cp -rf %s.sock /tmp/%s 2>/dev/null' % (project_name, project_name))

        print("Stopping " + project_name + " app server...")
        ctx.run('${HOME}/init/%s stop' % project_name)

        print("Replacing " + project_name + " app with freshly checked out project")
        with ctx.cd(app_env['dir']):
            ctx.run('rm -rf %s/* 2>/dev/null' % app_name)
            ctx.run('rsync -adC /tmp/%s/* .' % project_name)

        print("Updating pip requirements...")
        with ctx.cd(app_env['dir']):
            ctx.run('${HOME}/v/%s/bin/pip install -r requirements/%s.txt' % (app_name, app_env['requirements'],))

        # Make sure the app's secret key environment variable is available for the following commands
        with ctx.prefix('source ${HOME}/.bash_profile'):
            print("Collecting static files...")
            with ctx.cd(app_env['dir']):
                ctx.run('${HOME}/v/%s/bin/python %s.py collectstatic -v0 --noinput' % (app_name, app_env['manage_script'],))

            print("Applying database migrations...")
            with ctx.cd(app_env['dir']):
                ctx.run('${HOME}/v/%s/bin/python %s.py migrate' % (app_name, app_env['manage_script'],))

            print("Starting " + project_name + " app server...")
            ctx.run('${HOME}/init/%s start' % project_name)

        print("Restarting " + project_name + " web server...")
        ctx.run('${HOME}/init/nginx stop')
        ctx.run('${HOME}/init/nginx start')

        print(project_name + " Deployment finished succesfully!")
    finally:
        # deployment_cleanup(ctx, app_env)
        pass


def deployment_cleanup(ctx, app_env):
    print("Cleaning up...")
    ctx.run('rm -rf /tmp/%s' % app_env['name'])
    ctx.run('rm -rf /tmp/%s*.dump' % app_env['name'])
