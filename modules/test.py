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



