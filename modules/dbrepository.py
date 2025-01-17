
import sqlite3
import formatutil


def transform_result_set(result_set) -> list[dict]:
    list_of_results = []


    #Now we extract the results
    for row in result_set:
        r = dict( row )
        list_of_results.append(r)

    return list_of_results

def remove_all(keys, dictionary: dict):
    for key in keys:
        if key in dictionary:
            del dictionary[key]

def retain_all(keys, dictionary: dict):
    removal = set(dictionary.keys())
    removal.difference_update( set(keys) )

    for key in removal:
        if key in dictionary:
            del dictionary[key]



class TerraInvictaDatabaseRepository:

    #This query gives you general information about any given module, with adjustable conditions and table names
    __GENERAL_MODULE_TECH_STMT = """
        SELECT
            tm.friendly_name,
            pc.*,
            tm.required_project,
            tech.tech_type,
            tech.category,
            tech.cost,
            calc.dependency_count,
            calc.cost_sum_total
        FROM $$principle$$ pc
        JOIN TIModules tm ON pc.module_name = tm.module_name
        JOIN TITechEntries tech ON tm.required_project = tech.internal_name
        JOIN PrecalculatedPrerequisiteCosts calc ON calc.internal_name = tech.internal_name
        
    """

    __MODULE_TABLES = {
        "TIHabModules","TIShipModules", "TIShipHulls", "TIBatteries", "TIHeatSinks", "TIPowerPlants", "TIDrives",
        "TIUtilities", "TIWeapons", "TIConventionalGuns", "TIMagneticGuns", "TIMissiles", "TILasers",
        "TIParticleWeapons", "TIPlasmaWeapons", "TIArmor", "DrivePropellants", "HabModuleMonthlyBalances",
        "FactionUniqueModules"
    }

    def __init__(self, database_url):
        try:
            self.__database = sqlite3.connect(database_url)
            self.__database.row_factory = sqlite3.Row
        except sqlite3.Error as e:
            raise IOError(f"Error while connecting to database: {e}", e)

    def module_tables(self):
        return self.__MODULE_TABLES.copy()


    def get_module_tech_traits(self, table, condition=None, order_by=None, group_by=None, retention="include", columns=None) -> list[dict]:
        if condition is None:
            condition = ""
        else:
            condition = "WHERE " + condition
        if order_by is None:
            order_by = ""
        else:
            order_by = "ORDER BY " + order_by
        if group_by is None:
            group_by = ""
        else:
            group_by = " GROUP BY " + group_by

        if table not in self.__MODULE_TABLES:
            raise ValueError(f"Table {table} not recognized, the following tables are supported {self.__MODULE_TABLES}")

        cursor = self.__database.cursor()

        query = self.__GENERAL_MODULE_TECH_STMT.replace("$$principle$$", table)
        query += condition + " " + group_by + " " + order_by + "; "

        result = cursor.execute(query).fetchall()

        if len(result) > 0:
            trf = transform_result_set(result)
            #We prune out the unwanted columns at the end
            if columns is not None:
                for entry in trf:
                    if retention == "exclude":
                        remove_all( columns, entry )
                    elif retention == "include":
                        retain_all( columns, entry )
            return trf
        else:
            return []




if __name__ == "__main__":
    repository = TerraInvictaDatabaseRepository('../test_database.db')

    stuff = repository.get_module_tech_traits("FactionUniqueModules", condition="pc.faction not like 'AlienCouncil'")
    print( formatutil.to_csv(stuff) )
