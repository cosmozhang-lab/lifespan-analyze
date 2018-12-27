import sys, os

sys.path.append(os.path.realpath(os.path.dirname(__file__)))

if len(sys.argv) < 2:
    print("no command received. exit.")
    exit(0)

command = sys.argv[1].lower()

if command == "analyze":
    from lifespan.analyzing.main import run as run_analyze
    run_analyze()
elif command == "train":
    from lifespan.learning.main import train
    train()
elif command == "rundatasets":
    from lifespan.learning.main import run_datasets
    run_datasets()
else:
    print("command not recognized")
