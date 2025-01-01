
import sqlite3
import sys
import os





if __name__ == '__main__':

    database = sqlite3.connect('testfile')
    database.row_factory = sqlite3.Row


    if not len(sys.argv) == 2:
        exit(1)

    print(f"Computing total research cost for module, { sys.argv[1] }" )

    #Grab base cost
    cursor = database.cursor()

    cursor.execute( "select "
                    "TIShipModules.module_name, TITechEntries.internal_name, TITechEntries.cost from TIShipModules"
                    " inner join TITechEntries on TITechEntries.internal_name = TIShipModules.required_project"
                    " where TIShipModules.module_name = ?",
                    (sys.argv[1],)
                    )

    result = cursor.fetchone()
    name = result["internal_name"]
    cost = result["cost"]

    print(f"Module: {name}, Cost: {cost}")

    cursor.close()
    #Calculate for all prerequisites
    prereqlist = []

    cursor = database.cursor()
    cursor.execute( "select TIPrerequisites.*, TITechEntries.cost from TIPrerequisites "
                    "left join TITechEntries on TIPrerequisites.requires = TITechEntries.internal_name "
                    "where TIPrerequisites.internal_name = ?",
                    (name,))
    first_result = cursor.fetchall()
    for row in first_result:
        prereqlist.append((row["requires"], row["cost"]))

    cursor.close()

    for requirement in prereqlist:
        cursor = database.cursor()

        cursor.execute("select TIPrerequisites.*, TITechEntries.cost from TIPrerequisites "
                       "left join TITechEntries on TIPrerequisites.requires = TITechEntries.internal_name "
                       "where TIPrerequisites.internal_name = ?",
                       (requirement[0],))

        first_result = cursor.fetchall()
        for row in first_result:
            prereqlist.append((row["requires"], row["cost"]))

        cursor.close()

    unique_list = list(dict.fromkeys(prereqlist))
    unique_list.sort( key = lambda x : x[1], reverse = True )


    print("Requirements:\n")
    total = cost
    for requirement in unique_list:
        print(f"Name: {requirement[0]} Cost: {requirement[1]}")
        total += requirement[1]


    print(f"\nTotal: { total }")