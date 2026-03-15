#Copyright 2026 Dante Zitello
#
#Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
#1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
#2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
#3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS “AS IS” AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


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
