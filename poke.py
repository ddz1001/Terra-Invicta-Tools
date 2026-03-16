#!/usr/bin/env python3


#Copyright 2026 Dante Zitello
#
#Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
#1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
#2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
#3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS “AS IS” AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


import os
import sqlite3
import argparse
import json
import modules.prereqchain as prqc

def to_csv( entries: dict ) -> str:
    keys = entries.keys()

    csv = ""
    total = 0
    for key in keys:
        if total == 0:
            total = len(entries[key])

        csv += f"{key},"
    csv = csv[:-1] + "\n"

    #The rest
    for i in range( total ):
        for key in keys:
            csv += f"\"{entries[key][i]}\","
        csv = csv[:-1] + "\n"

    return csv

def to_friendly_stdout(entries: dict) -> str:
    keys = entries.keys()

    fstr = ""
    total = 0
    for key in keys:
        if total == 0:
            total = len(entries[key])
            break


    #The rest
    for i in range( total ):
        for key in keys:
            fstr += f"{entries[key][i]}\t"
        fstr = fstr[:-1] + "\n"

    return fstr

def to_json(entries: dict) -> str:
    keys = entries.keys()
    jstr = ""

    total = 0
    for key in keys:
        if total == 0:
            total = len(entries[key])
            break #Just grab the length of the first one

    currentObject = {}
    for i in range( total ):
        for key in keys:
            currentObject.update({
                key: entries[key][i],
            })
        jstr = jstr + json.dumps(currentObject, indent=4) + "\n"
        currentObject.clear()


    return jstr


def transpose_resultset(resultset):

    transposed = {}
    keys = resultset[0].keys()

    for key in keys:
        transposed[key] = list()

    for row in resultset:
        for key in keys:
            transposed[key].append( row[key] )

    return transposed

def handle_module(database, module:str, table):
    cursor = database.cursor()
    cursor.execute(f"SELECT * FROM {table} where module_name = ?", (module,))
    #rs = dict(cursor.fetchone())
    rs = transpose_resultset(cursor.fetchall())
    cursor.close()
    return rs

def handle_hull_module(database, module:str):
    return handle_module(database, module, "TIShipHulls")

def handle_drive_module(database, module:str):
    return handle_module( database, module, "TIDrives" )

def handle_weapon_module(database, module:str):
    cursor = database.cursor()
    record = cursor.execute("SELECT * FROM TIWeapons where module_name = ?", (module,))
    type = record.fetchone()['weapon_type']

    join_table = ""

    #Join table
    if type == "conventional_gun":
        join_table = "TIConventionalGuns"
    elif type == "magnetic_gun":
        join_table = "TIMagneticGuns"
    elif type == "missile":
        join_table = "TIMissiles"
    elif type == "particle":
        join_table = "TIParticleWeapons"
    elif type == "laser":
        join_table = "TILasers"
    elif type == "plasma":
        join_table = "TIPlasmaWeapons"

    cursor.execute(f"""
        SELECT {join_table}.*, TIWeapons.can_attack, TIWeapons.can_defend, TIWeapons.crew_needed, TIWeapons.module_mass, TIWeapons.mount_type 
        FROM TIWeapons 
        JOIN {join_table} on TIWeapons.module_name = {join_table}.module_name
        where TIWeapons.module_name = ?""", (module,))
    rs = cursor.fetchall()
    rval = transpose_resultset(rs)

    cursor.close()

    return rval

def handle_heat_sink_module(database, module:str):
    return handle_module(database, module, "TIHeatSinks")

def handle_power_plant_module(database, module:str):
    return handle_module(database, module, "TIPowerPlants")

def handle_radiator_module(database, module:str):
    return handle_module(database, module, "TIRadiators")

def handle_battery_module(database, module:str):
    return handle_module(database, module, "TIBatteries")

def handle_armor_module(database, module:str):
    return handle_module(database, module, "TIArmor")

def handle_utility_module(database, module:str):
    return handle_module(database, module, "TIUtilities")

def do_show_module(database, module:str):

    cursor = database.cursor()
    cursor.execute('SELECT * FROM TIShipModules where module_name = ?', (module,))
    result = cursor.fetchone()
    if result is None:
        raise ValueError('No module named ' + module)

    module_type = result['module_type']
    cursor.close()

    if module_type == "hull":
        return handle_hull_module(database, module)
    elif module_type == "drive":
        return handle_drive_module(database, module)
    elif module_type == "nose_weapon" or module_type == "hull_weapon":
        return handle_weapon_module(database, module)
    elif module_type == "heat_sink":
        return handle_heat_sink_module(database, module)
    elif module_type == "power_plant":
        return handle_power_plant_module(database, module)
    elif module_type == "radiator":
        return handle_radiator_module(database, module)
    elif module_type == "battery":
        return handle_battery_module(database, module)
    elif module_type == "armor":
        return handle_armor_module(database, module)
    elif module_type == "utility":
        return handle_utility_module(database, module)


def do_show_modules(database):
    cursor = database.cursor()
    cursor.execute('SELECT module_name FROM TIShipModules')
    rs = cursor.fetchall()
    rval = transpose_resultset(rs)
    cursor.close()
    return rval

def do_show_global_techs(database):
    cursor = database.cursor()
    cursor.execute('SELECT TITechEntries.*, TIGlobalTechnologies.end_game_tech FROM TITechEntries JOIN TIGlobalTechnologies on TITechEntries.internal_name = TIGlobalTechnologies.internal_name')
    rs = cursor.fetchall()
    rval = transpose_resultset(rs)
    cursor.close()
    return rval

def do_show_project_techs(database):
    cursor = database.cursor()
    cursor.execute('SELECT TITechEntries.*, TIProjects.repeatable, TIProjects.globally_shared FROM TITechEntries JOIN TIProjects on TITechEntries.internal_name = TIProjects.internal_name')
    rs = cursor.fetchall()
    rval = transpose_resultset(rs)
    cursor.close()
    return rval

def do_list_dependencies(database, technology):
    cursor = database.cursor()
    resultset = prqc.get_dependencies_for( technology, cursor )
    transposed = transpose_resultset(resultset)
    cursor.close()

    return transposed

def do_show_ordered_dependencies(database, technology):
    cursor = database.cursor()
    resultset = prqc.get_cost_ordered_dependencies_for( technology, cursor )
    transposed = transpose_resultset(resultset)
    cursor.close()

    return transposed

def do_show_total_tech_cost(database, technology):
    cursor = database.cursor()
    cursor.execute("SELECT * from PrecalculatedPrerequisiteCosts where internal_name = ?", (technology,))
    resultset = cursor.fetchall()
    rs = transpose_resultset(resultset)
    cursor.close()
    return rs

def do_show_tech_information(database, technology):
    cursor = database.cursor()
    cursor.execute("SELECT tech_type from TITechEntries where internal_name = ?", (technology,))
    resultset = cursor.fetchone()
    type = resultset[0]
    cursor.close()

    resultset = None
    cursor = database.cursor()

    if type == "Global":
        cursor.execute("""
            SELECT TITechEntries.*, TIGlobalTechnologies.end_game_tech 
            FROM TITechEntries JOIN TIGlobalTechnologies 
            on TITechEntries.internal_name = TIGlobalTechnologies.internal_name
            where TITechEntries.internal_name = ?""", (technology,))
        resultset = cursor.fetchall()
    elif type == "Project":
        cursor.execute("""
            SELECT TITechEntries.*, TIProjects.repeatable, TIProjects.globally_shared
            FROM TITechEntries JOIN TIProjects 
            on TITechEntries.internal_name = TIProjects.internal_name
            where TITechEntries.internal_name = ?
        """, (technology,))
        resultset = cursor.fetchall()

    rs = transpose_resultset(resultset)
    cursor.close()
    return rs


#Program body

def list_modules(argns: argparse.Namespace):
    database = sqlite3.connect(argns.database)
    database.row_factory = sqlite3.Row

    result = do_show_modules(database)
    database.close()

    outstr = None
    if argns.csv:
        outstr = to_csv(result)
    elif argns.json:
        outstr = to_json(result)
    else:
        outstr = to_friendly_stdout(result)

    print(outstr)

def show_module_information(argns: argparse.Namespace):
    database = sqlite3.connect(argns.database)
    database.row_factory = sqlite3.Row

    result = do_show_module(database, argns.module_name)
    database.close()

    outstr = None
    if argns.csv:
        outstr = to_csv(result)
    elif argns.json:
        outstr = to_json(result)
    else:
        outstr = to_friendly_stdout(result)

    print(outstr)

def list_projects(argns: argparse.Namespace):
    database = sqlite3.connect(argns.database)
    database.row_factory = sqlite3.Row

    result = do_show_project_techs(database)
    database.close()
    outstr = None


    if argns.truncate:
        dlist = []
        for key in result.keys():
            if key != "internal_name":
                dlist.append(key)

        for key in dlist:
            del result[key]
    elif argns.research:
        dlist = []
        for key in result.keys():
            if key != "internal_name" and key != "cost":
                dlist.append(key)

        for key in dlist:
            del result[key]


    if argns.csv:
        outstr = to_csv(result)
    elif argns.json:
        outstr = to_json(result)
    else:
        outstr = to_friendly_stdout(result)

    print(outstr)

def list_globals(argns: argparse.Namespace):
    database = sqlite3.connect(argns.database)
    database.row_factory = sqlite3.Row

    result = do_show_global_techs(database)
    database.close()
    outstr = None


    if argns.truncate:
        dlist = []
        for key in result.keys():
            if key != "internal_name":
                dlist.append(key)

        for key in dlist:
            del result[key]
    elif argns.research:
        dlist = []
        for key in result.keys():
            if key != "internal_name" and key != "cost":
                dlist.append(key)

        for key in dlist:
            del result[key]


    if argns.csv:
        outstr = to_csv(result)
    elif argns.json:
        outstr = to_json(result)
    else:
        outstr = to_friendly_stdout(result)

    print(outstr)

def show_dependencies(argns: argparse.Namespace):
    database = sqlite3.connect(argns.database)
    database.row_factory = sqlite3.Row

    result = None
    if argns.ordered:
        result = do_show_ordered_dependencies(database, argns.technology_name)
    else:
        result = do_list_dependencies(database, argns.technology_name)

    if argns.truncate:
        del result["cost"] #our only other column


    database.close()
    outstr = None

    if argns.csv:
        outstr = to_csv(result)
    elif argns.json:
        outstr = to_json(result)
    else:
        outstr = to_friendly_stdout(result)

    print(outstr)

def show_tech_cost(argns: argparse.Namespace):
    database = sqlite3.connect(argns.database)
    database.row_factory = sqlite3.Row

    result = do_show_total_tech_cost(database, argns.technology_name)
    database.close()

    outstr = None

    if argns.csv:
        outstr = to_csv(result)
    elif argns.json:
        outstr = to_json(result)
    else:
        outstr = to_friendly_stdout(result)

    print(outstr)

def show_tech_details(argns: argparse.Namespace):
    database = sqlite3.connect(argns.database)
    database.row_factory = sqlite3.Row

    #result = do_show_total_tech_cost(database, argns.technology_name)
    result = do_show_tech_information(database, argns.technology_name)

    database.close()

    if argns.research:
        dlist = []
        for key in result.keys():
            if key != "internal_name" and key != "cost":
                dlist.append(key)

        for key in dlist:
            del result[key]

    outstr = None

    if argns.csv:
        outstr = to_csv(result)
    elif argns.json:
        outstr = to_json(result)
    else:
        outstr = to_friendly_stdout(result)

    print(outstr)


def program():
    argparser = argparse.ArgumentParser()
    sub = argparser.add_subparsers(required=True, dest='command', help="Commands")

    parser_list_modules = sub.add_parser('list-modules', help="List module names")
    parser_list_modules.add_argument("database", default=None, type=str,action="store", help="Database to inspect")
    parser_list_modules.add_argument("-c", "--csv", default=False, action="store_true", help="Format output as CSV")
    parser_list_modules.add_argument("-j", "--json", default=False, action="store_true", help="Format output as JSON")
    parser_list_modules.set_defaults(func=list_modules)

    parser_list_projects = sub.add_parser('list-projects', help="List all projects")
    parser_list_projects.add_argument("database", default=None, type=str,action="store", help="Database to inspect")
    parser_list_projects.add_argument("-c", "--csv", default=False, action="store_true", help="Format output as CSV")
    parser_list_projects.add_argument("-j", "--json", default=False, action="store_true", help="Format output as JSON")
    parser_list_projects.add_argument("-t", "--truncate", default=False, action="store_true", help="Truncate to just the project name")
    parser_list_projects.add_argument("-r", "--research", default=False, action="store_true", help="Truncate to just the project name and research cost")
    parser_list_projects.set_defaults(func=list_projects)

    parser_list_globals = sub.add_parser('list-global-techs', help="List all global technologies")
    parser_list_globals.add_argument("database", default=None, type=str,action="store", help="Database to inspect")
    parser_list_globals.add_argument("-c", "--csv", default=False, action="store_true", help="Format output as CSV")
    parser_list_globals.add_argument("-j", "--json", default=False, action="store_true", help="Format output as JSON")
    parser_list_globals.add_argument("-t", "--truncate", default=False, action="store_true", help="Truncate to just the tech name")
    parser_list_globals.add_argument("-r", "--research", default=False, action="store_true", help="Truncate to just the project name and research cost")
    parser_list_globals.set_defaults(func=list_globals)

    parser_show_module = sub.add_parser('show-module', help="Show detailed module information")
    parser_show_module.add_argument("database", default=None, type=str,action="store", help="Database to inspect")
    parser_show_module.add_argument("module_name", default=None, type=str,action="store", help="Module name")
    parser_show_module.add_argument("-c", "--csv", default=False, action="store_true", help="Format output as CSV")
    parser_show_module.add_argument("-j", "--json", default=False, action="store_true", help="Format output as JSON")
    parser_show_module.set_defaults(func=show_module_information)

    parser_list_tech_dependencies = sub.add_parser('show-dependencies', help="Show dependencies for any tech or project")
    parser_list_tech_dependencies.add_argument("database", default=None, type=str,action="store", help="Database to inspect")
    parser_list_tech_dependencies.add_argument("technology_name", default=None, type=str,action="store", help="Technology name")
    parser_list_tech_dependencies.add_argument("-c", "--csv", default=False, action="store_true", help="Format output as CSV")
    parser_list_tech_dependencies.add_argument("-j", "--json", default=False, action="store_true", help="Format output as JSON")
    parser_list_tech_dependencies.add_argument("-o", "--ordered", default=False, action="store_true", help="Return result ordered by cost")
    parser_list_tech_dependencies.add_argument("-t", "--truncate", default=False, action="store_true", help="Truncate to just the tech names")
    parser_list_tech_dependencies.set_defaults(func=show_dependencies)

    parser_show_tech_total_cost = sub.add_parser('show-tech-cost', help="Show total cost breakdown for given technology")
    parser_show_tech_total_cost.add_argument("database", default=None, type=str,action="store", help="Database to inspect")
    parser_show_tech_total_cost.add_argument("technology_name", default=None, type=str,action="store", help="Module name")
    parser_show_tech_total_cost.add_argument("-c", "--csv", default=False, action="store_true", help="Format output as CSV")
    parser_show_tech_total_cost.add_argument("-j", "--json", default=False, action="store_true", help="Format output as JSON")
    parser_show_tech_total_cost.set_defaults(func=show_tech_cost)

    parser_show_tech = sub.add_parser('show-tech', help="Show all details for a given technology")
    parser_show_tech.add_argument("database", default=None, type=str,action="store", help="Database to inspect")
    parser_show_tech.add_argument("technology_name", default=None, type=str,action="store", help="Module name")
    parser_show_tech.add_argument("-c", "--csv", default=False, action="store_true", help="Format output as CSV")
    parser_show_tech.add_argument("-j", "--json", default=False, action="store_true", help="Format output as JSON")
    parser_show_tech.add_argument("-r", "--research", default=False, action="store_true", help="Truncate to just tech name and research cost")
    parser_show_tech.set_defaults(func=show_tech_details)




    args = argparser.parse_args()
    args.func(args) #Call the function

if __name__ == '__main__':
    program()
    exit(0)






