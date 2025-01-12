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

