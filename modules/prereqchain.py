

import sqlite3

def get_dependencies_for(technology, db_cursor):

    query = """
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
        SELECT * from (SELECT TITechEntries.internal_name, TITechEntries.cost from TITechEntries
        WHERE internal_name = :start_name)
        UNION ALL
        SELECT * from (SELECT DISTINCT DependencyChain.requires as internal_name, TITechEntries.cost from DependencyChain
        LEFT JOIN TITechEntries on DependencyChain.requires = TITechEntries.internal_name ORDER BY cost DESC);
    """

    #This exceedingly complicated query returns the entire dependency chain for a given technology/project
    #The first row is always the technology provided. The results are ordered by the cost in research points
    #If our technology has no prerequisites, then only the provided technology is returned

    db_cursor.execute(query, {"start_name": technology})
    return db_cursor.fetchall()
