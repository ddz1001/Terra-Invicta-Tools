#!/usr/bin/env python3

#Copyright 2026 Dante Zitello
#
#Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
#1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
#2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
#3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS “AS IS” AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import os
import argparse
import sys

from modules.dbmanagement import TerraInvictaDatabaseManager
from modules.dbrepository import TerraInvictaDatabaseRepository

program_state = argparse.Namespace()
program_state.ready = False

def verbose_info(msg) :
    if program_state.verbose:
        print(msg, file=sys.stderr)

def initialize_program_state():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("filename", default=None, type=str, action="store", help="Database filename")
    argparser.add_argument("directory", default=None, type=str, action="store", help="Directory of relevant files")
    argparser.add_argument("-V", "--verbose", action="store_true", help="Verbose output to stderr")

    argparser.parse_args(namespace=program_state)
    program_state.ready = True

def program():
    if not program_state.ready:
        print("Program not in ready state", file=sys.stderr)
        exit(1)

    if program_state.filename is None or program_state.filename.strip() == "":
        print("Database filename cannot be empty", file=sys.stderr)
        exit(1)

    if program_state.directory is None or program_state.directory.strip() == "":
        print("Directory name cannot be empty", file=sys.stderr)
        exit(1)

    if not os.path.exists(program_state.filename):
        print("File does not exist", file=sys.stderr)
        exit(1)

    if not os.path.exists(program_state.directory):
        print("Directory does not exist", file=sys.stderr)
        exit(1)

    if not os.path.isdir(program_state.directory):
        print("Directory is not a directory", file=sys.stderr)
        exit(1)


    #Program

    #grab json files
    json_path_list = []
    for root, dirs, files in os.walk(str(program_state.directory)):
        for name in files:
            json_path_list.append(os.path.abspath( os.path.join( root, name ) ))
        break

    verbose_info(f"From directory: {program_state.directory}")
    verbose_info(f"{json_path_list}")

    verbose_info(f"Check if already populated")
    try:
        dbrepository = TerraInvictaDatabaseRepository(program_state.filename)
        is_populated = dbrepository.get_db_populated()
        dbrepository.close() #close the connection
    except Exception as e:
        print(f"Failed to open database {program_state.filename}", file=sys.stderr)
        print(e, file=sys.stderr)
        exit(1)

    #For now, we will only allow for fresh files
    if is_populated:
        print("Database is already loaded, to reload, use another file, or reinitialize the provided file", file=sys.stderr)
        exit(1)

    verbose_info(f"Loading data into database")
    dbhandler = TerraInvictaDatabaseManager()
    try:
        dbhandler.populate_db( str( program_state.filename ), json_path_list )
        verbose_info(f"Precalculate dependencies")
        dbhandler.precalculate_dependency_costs( str( program_state.filename ) )
    except Exception as e:
        print("Failed to populate database, transaction rolled back", file=sys.stderr)
        print(e, file=sys.stderr)
        exit(1)

    verbose_info(f"Data loading complete")

if __name__ == '__main__':
    initialize_program_state()
    program()
    exit(0)