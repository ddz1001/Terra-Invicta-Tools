#Copyright 2026 Dante Zitello
#
#Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
#1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
#2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
#3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS “AS IS” AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


import sqlite3

class TerraInvictaModuleRepository:

    __database = None

    def __init__(self, database_url):
        self.__database = sqlite3.connect(database_url)
        self.__database.row_factory = sqlite3.Row

    def get_drives(self):
        cursor = self.__database.cursor()

        result_set = cursor.execute("""
            select TIDrives.*, TIModules.required_project
                FROM TIDrives 
                    LEFT JOIN TIModules on TIDrives.module_name = TIModules.module_name 
                    GROUP BY common_drive_name;
        """).fetchall()

        result = transpose_resultset(result_set)
        cursor.close()

        return result


def transpose_resultset(resultset):

    transposed = {}
    keys = resultset[0].keys()

    for key in keys:
        transposed[key] = list()

    for row in resultset:
        for key in keys:
            transposed[key].append( row[key] )

    return transposed


def to_csv( modules: dict ) -> str:
    keys = modules.keys()

    csv = ""
    total = 0
    for key in keys:
        if total == 0:
            total = len(modules[key])

        csv += f"{key},"
    csv = csv[:-1] + ";"

    #The rest
    for i in range( total ):
        for key in keys:
            csv += f"\"{modules[key][i]}\","
        csv = csv[:-1] + ";"

    return csv

if __name__ == "__main__":
    repository = TerraInvictaModuleRepository("../test_database.db")

    print( to_csv(repository.get_drives()).replace(";", "\n") )

