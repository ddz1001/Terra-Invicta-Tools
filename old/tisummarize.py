
import sqlite3
import sys
import os

#DO NOT DELETE THIS QUERY
PROJECT_DEPENDENCY_CHAIN_STMT = """
    WITH RECURSIVE DependencyChain AS (
        SELECT
            internal_name,
            requires
        FROM TIPrerequisites
        WHERE internal_name = :start_name
    
        UNION ALL
    
        SELECT
            tp.internal_name,
            tp.requires
        FROM TIPrerequisites tp
        INNER JOIN DependencyChain dc
            ON tp.internal_name = dc.requires
    )
    SELECT * from (SELECT TITechEntries.internal_name, TITechEntries.category, TITechEntries.cost from TITechEntries
    WHERE internal_name = :start_name)
    UNION ALL
    SELECT * from (SELECT DISTINCT DependencyChain.requires as internal_name, TITechEntries.category, TITechEntries.cost from DependencyChain
    LEFT JOIN TITechEntries on DependencyChain.requires = TITechEntries.internal_name ORDER BY cost DESC);
"""


def list_dependencies(tech, database):
    cursor = database.cursor()
    cursor.execute(PROJECT_DEPENDENCY_CHAIN_STMT, {"start_name": tech})

    results = cursor.fetchall()
    total = 0
    columns = []
    for row in results:
        total += row["cost"]
        columns.append( dict(row) )

    return columns, total


if __name__ == '__main__':

    database = sqlite3.connect('../test_database.db')
    database.row_factory = sqlite3.Row

    project = "Accelerando"

    print(f"Computing total research cost for project, { project }" )

    (r, t) = list_dependencies(project, database)

    print(f"Total Cost: {t}")
    print(f"Dependencies: {r}")

    database.close()

    #Grab base cost
   #cursor = database.cursor()

   #cursor.execute( "select "
   #                "TIShipModules.module_name, TITechEntries.internal_name, TITechEntries.cost from TIShipModules"
   #                " inner join TITechEntries on TITechEntries.internal_name = TIShipModules.required_project"
   #                " where TIShipModules.module_name = ?",
   #                (module,)
   #                )

   #result = cursor.fetchone()
   #name = result["internal_name"]
   #cost = result["cost"]

   #print(f"Project: {name}, Cost: {cost}")

    #cursor.close()
    ##Calculate for all prerequisites
    #prereqlist = []
#
    #cursor = database.cursor()
    #cursor.execute( "select TIPrerequisites.*, TITechEntries.cost from TIPrerequisites "
    #                "left join TITechEntries on TIPrerequisites.requires = TITechEntries.internal_name "
    #                "where TIPrerequisites.internal_name = ?",
    #                (name,))
    #first_result = cursor.fetchall()
    #for row in first_result:
    #    prereqlist.append((row["requires"], row["cost"]))
#
    #cursor.close()
#
    #for requirement in prereqlist:
    #    cursor = database.cursor()
#
    #    cursor.execute("select TIPrerequisites.*, TITechEntries.cost from TIPrerequisites "
    #                   "left join TITechEntries on TIPrerequisites.requires = TITechEntries.internal_name "
    #                   "where TIPrerequisites.internal_name = ?",
    #                   (requirement[0],))
#
   #     first_result = cursor.fetchall()
   #     for row in first_result:
   #         prereqlist.append((row["requires"], row["cost"]))
#
   #     cursor.close()
#
   # unique_list = list(dict.fromkeys(prereqlist))
   # unique_list.sort( key = lambda x : x[1], reverse = True )
#
#
   # print("Requirements:\n")
  #  total = cost
  #  for requirement in unique_list:
  #      print(f"Name: {requirement[0]} Cost: {requirement[1]}")
  #      total += requirement[1]
#
#
  #  print(f"\nTotal: { total }")