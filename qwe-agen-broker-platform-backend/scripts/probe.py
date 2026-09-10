import os
print("cwd:", os.getcwd())
print("visible:", os.listdir("refs")[:3])
print("work/bp:", os.listdir("work/bp")[:3])
