from invoke import task

@task
def data(ctx):
    ctx.run("python3 src/Luncher/lounaat.py", pty=True)

# @task
# def clustering(ctx):
#     ctx.run("python3 src/Luncher/klusterointi.py", pty=True)
