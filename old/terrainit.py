
#Copyright 2026 Dante Zitello
#
#Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
#1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
#2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
#3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS “AS IS” AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


import os
import argparse
import sqlite3
import sys

version = "0.1"
default_search_path= "../tidb.sql"

class ProgramState:
    pass

program_state = ProgramState()
program_state.ready = False

def verbose_info(msg) :
    if program_state.verbose:
        print(msg, file=sys.stderr)

def initialize_program_state():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-o", "--overwrite", action="store_true", help="Overwrite existing database file")
    argparser.add_argument("filename", default=None, type=str, action="store", help="Output filename")
    argparser.add_argument("-v", "--version", action="version", version=version)
    argparser.add_argument("-s", "--sql", type=str, default= default_search_path, help="SQL script location")
    argparser.add_argument("-V", "--verbose", action="store_true", help="Verbose output to stderr")

    argparser.parse_args(namespace=program_state)

    program_state.ready = True


def program():
    if not program_state.ready:
        print("Program not in ready state", file=sys.stderr)
        exit(1)

    if program_state.filename is None or program_state.filename.strip() == "":
        print("Filename cannot be empty", file=sys.stderr)
        exit(1)

    if program_state.sql is None or program_state.sql.strip() == "":
        print("No SQL script specified", file=sys.stderr)
        exit(1)


    if os.path.exists( program_state.filename ) and not program_state.overwrite:
        print("Database file already exists. Run with -o/--overwrite option to overwrite existing database file", file=sys.stderr)
        exit(1)

    if program_state.overwrite and not os.path.exists( program_state.filename ):
        print("Cannot overwrite database file, file not found,", file=sys.stderr)
        exit(1)

    if not os.path.exists(program_state.sql) :
        print("No SQL script specified", file=sys.stderr)
        exit(1)


    #Program

    if os.path.exists( program_state.filename ) and program_state.overwrite:
        verbose_info(f"Overwriting existing database file {program_state.filename}")
        os.remove( program_state.filename )

    verbose_info( f"Initializing new database {program_state.filename}" )
    database = sqlite3.connect( program_state.filename )
    database.row_factory = sqlite3.Row

    verbose_info(f"Load script {program_state.sql}")
    sql_script = open(program_state.sql, "r")
    sql = sql_script.read()

    try:
        cursor = database.cursor()

        verbose_info("Executing script")
        cursor.executescript(sql)
        database.commit()
        cursor.close()
    except sqlite3.Error as e:
        database.rollback()
        print(f"SQL Error: \n {e}", file=sys.stderr)
        database.close()
        exit(2)

    verbose_info("Initialization complete")

    if program_state.verbose:
        cv = database.cursor()
        cv.execute(" SELECT `entry_name`, `entry_value` from `TIDatabaseInfo` where `entry_name` = 'dbversion' ")
        dbversion = cv.fetchone()['entry_value']
        verbose_info(f"Database version is {dbversion}")

    database.close()

if __name__ == '__main__':
    initialize_program_state()
    program()
    exit(0)