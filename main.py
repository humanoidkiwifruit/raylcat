#!/usr/bin/env python3
import sys

from transpiler import transpiler

COMMANDS = ["build", "run"]

if len(sys.argv) > 1:
    command = sys.argv[1]
    if len(sys.argv) > 2:
        sb3_path = sys.argv[2]
        if command == "build":
            project = transpiler.ScratchProject(sb3_path)
            project.build()
        elif command == "run":
            project = transpiler.ScratchProject(sb3_path)
            project.build()
            project.run()

    elif command in COMMANDS:
        print("Please specify an sb3 path.")
    else:
        print("Invalid command.")
else:
    print(f"Please specify a command. Options are {COMMANDS}.")
