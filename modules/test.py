#Copyright 2026 Dante Zitello
#
#Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
#1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
#2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
#3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS “AS IS” AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


import traceback

import eel
import dbrepository
import formatutil as fmt
import sqlite3

repo = dbrepository.TerraInvictaDatabaseRepository("../test_database.db")
db = sqlite3.connect("../test_database.db")
db.row_factory = sqlite3.Row

@eel.expose
def findForTable( table_name ):
    return fmt.to_html_table( repo.get_module_tech_traits( table_name ) )

@eel.expose
def getTables():
    return list(repo.module_tables())

@eel.expose
def execute( sql ):
    try:
        cursor = db.cursor()
        rs = cursor.execute(sql).fetchall()
        tr = dbrepository.transform_result_set(rs)
        cursor.close()
        html = fmt.to_html_table( tr )
        return html
    except sqlite3.Error as e:
        traceback.print_exc()
        return " <p> " + str( e ) + " </p> "
    except ValueError as e:
        traceback.print_exc()
        return "<p>Internal Error</p>"

if __name__ == "__main__":
    # Initialize Eel with the folder containing your HTML/JS/CSS
    eel.init('test')

    # Start the application
    eel.start('index.html')
    pass



