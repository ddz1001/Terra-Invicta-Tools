#Copyright 2026 Dante Zitello
#
#Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
#1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
#2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
#3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS “AS IS” AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


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

    __GENERAL_MODULE_MATERIAL_STMT = """
            SELECT
            tm.friendly_name,
            pc.*,
            mt.water,
            mt.volatiles,
            mt.metals,
            mt.nobleMetals,
            mt.fissiles,
            mt.exotics,
            mt.antimatter
        FROM $$principle$$ pc
        JOIN TIModules tm ON pc.module_name = tm.module_name
        JOIN TIModuleMaterials mt on tm.module_name = mt.module_name    
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

    def __base_get(self, principle_query, condition=None, order_by=None, group_by=None, retention="include", columns=None):
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


        cursor = self.__database.cursor()

        principle_query += condition + " " + group_by + " " + order_by + "; "

        result = cursor.execute(principle_query).fetchall()

        ret = []
        if len(result) > 0:
            trf = transform_result_set(result)
            #We prune out the unwanted columns at the end
            if columns is not None:
                for entry in trf:
                    if retention == "exclude":
                        remove_all( columns, entry )
                    elif retention == "include":
                        retain_all( columns, entry )
            ret = trf

        cursor.close()
        return ret


    def get_module_tech_traits(self, table, condition=None, order_by=None, group_by=None, retention="include", columns=None) -> list[dict]:
        if table not in self.__MODULE_TABLES:
            raise ValueError(f"Table {table} not recognized, the following tables are supported {self.__MODULE_TABLES}")

        query = self.__GENERAL_MODULE_TECH_STMT.replace("$$principle$$", table)
        return self.__base_get(query, condition, order_by, group_by, retention, columns)

    def get_module_material_traits(self, table, condition=None, order_by=None, group_by=None, retention="include", columns=None) -> list[dict]:
        if table not in self.__MODULE_TABLES:
            raise ValueError(f"Table {table} not recognized, the following tables are supported {self.__MODULE_TABLES}")

        query = self.__GENERAL_MODULE_MATERIAL_STMT.replace("$$principle$$", table)
        return self.__base_get(query, condition, order_by, group_by, retention, columns)


if __name__ == "__main__":
    repository = TerraInvictaDatabaseRepository('../test_database.db')

    stuff = repository.get_module_material_traits("FactionUniqueModules", condition="pc.faction not like 'AlienCouncil'")
    print( formatutil.to_csv(stuff) )
