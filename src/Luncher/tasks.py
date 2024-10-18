from invoke import task

@task
def data(ctx):
    ctx.run("python3 lounaat.py", pty=True)

@task
def clustering(ctx):
    ctx.run("python3 klusterointi.py", pty=True)
