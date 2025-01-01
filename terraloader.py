
import os
import argparse
import sqlite3
import json
import sys
import traceback

TECH_ENTRY_STMT = ("INSERT INTO TITechEntries"
                   "( internal_name, friendly_name, ai_critical, tech_type, category, role, cost )"
                   "VALUES"
                   "( :dataName, :friendlyName, :AI_criticalTech, :_type, :techCategory, :AI_techRole, :researchCost)"
                   ";")

GLOBAL_TECH_STMT = ("INSERT INTO TIGlobalTechnologies"
                          "(internal_name, end_game_tech)"
                          "VALUES"
                          "(:dataName, :endGameTech)"
                    ";")

PROJECT_TECH_STMT = ("INSERT INTO TIProjects"
                     "( internal_name, globally_shared, repeatable )"
                     "VALUES "
                     "( :dataName, :oneTimeGlobally, :repeatable )"
                     ";")

TECH_PREREQ_STMT = ("INSERT INTO TIPrerequisites"
                    "(internal_name, requires)"
                    "VALUES "
                    "(:_dataName, :_pr)"
                    ";")

FACTION_STMT = ("INSERT INTO TIFactions"
                "(faction_internal, faction_common)"
                "VALUES "
                "(:dataName, :friendlyName)"
                ";")

FACTION_PREREQ_STMT = ("INSERT INTO TIFactionPrerequisites"
                       "(internal_name, faction)"
                       "VALUES "
                       "(:_dataName, :_faction)"
                       ";")

SHIP_MODULE_STMT = ("INSERT INTO TIShipModules"
                    "(module_name, friendly_name, required_project, module_type)"
                    "VALUES "
                    "(:dataName, :friendlyName, :requiredProjectName, :_type)"
                    ";")

SHIP_HULL_MODULE_STMT = ("INSERT INTO TIShipHulls"
                         "(module_name, alien_only, construction_tier,"
                         "construction_time, maximum_officers,"
                         "starting_crew, mission_control, "
                         "monthly_cost, base_mass, length,"
                         "width, volume, structural_integrity,"
                         "nose_hardpoints, hull_hardpoints,"
                         "max_modules, thruster_multiplier)"
                         "VALUES "
                         "(:dataName, :alien, :consTier, "
                         ":baseConstructionTime_days, "
                         ":maxOfficers, :crew, :missionControl,:monthlyIncome_Money,"
                         ":mass_tons, :length_m, :width_m, :volume,"
                         ":structuralIntegrity, :noseHardpoints, :hullHardpoints,"
                         ":internalModules, :thrusterMultiplier)"
                         ";")

SHIP_POWER_PLANT_MODULE_STMT = ("INSERT INTO TIPowerPlants"
                                "(module_name, plant_class,"
                                "max_power, specific_power,"
                                "general_use, efficiency,"
                                "crew_needed)"
                                "VALUES "
                                "(:dataName, :powerPlantClass, :maxOutput_GW,"
                                ":specificPower_tGW, :generalUse, :efficiency,"
                                ":crew)"
                                ";")

SHIP_DRIVE_MODULE_STMT = ("INSERT INTO TIDrives"
                          "(module_name, common_drive_name, thruster_count,"
                          "drive_class, power_plant_class, thrust,"
                          "exhaust_velocity, efficiency, power_needed,"
                          "rating, flat_mass, cooling_cycle, combat_cap,"
                          "needs_helium_3)"
                          "VALUES "
                          "(:dataName, :_commonDrive, :thrusters, "
                          ":driveClassification, :requiredPowerPlant,"
                          ":thrust_N, :EV_kps, :efficiency, :_requiredPower, "
                          ":thrustRating_GW, :flatMass_tons, :cooling,"
                          ":thrustCap, :helium3Fuel )"
                          ";")

SHIP_RADIATOR_MODULE_STMT = ("INSERT INTO TIRadiators"
                             "(module_name, specific_mass,"
                             "specific_power, operating_temperature,"
                             "emissivity, vulnerability, crew_needed,"
                             "radiator_type, collector)"
                             "VALUES "
                             "(:dataName, :specificMass_2s_kgm2,"
                             ":specificPower_2s_KWkg, "
                             ":operatingTemp_K,"
                             ":emissivity, :vulnerability,"
                             ":crew, :radiatorType, :collector)"
                             ";")

SHIP_BATTERY_MODULE_STMT = ("INSERT INTO TIBatteries"
                            "(module_name, capacity,"
                            "recharge_rate, mass,"
                            "crew_needed, hit_points)"
                            "VALUES "
                            "(:dataName, :energyCapacity_GJ,"
                            ":rechargeRate_GJs, :mass_tons,"
                            ":crew, :hp)"
                            ";")

SHIP_HEAT_SINK_MODULE_STMT = ("INSERT INTO TIHeatSinks"
                           "(module_name, capacity, mass, crew_needed)"
                           "VALUES "
                           "(:dataName, :heatCapacity_GJ, :mass_tons, :crew)"
                           ";")

SHIP_UTILITY_MODULE_STMT = ("INSERT INTO TIUtilities"
                            "(module_name, no_combat_repair, power_requirement)"
                            "VALUES "
                            "(:dataName, :noCombatRepair, :powerRequirement_MW )"
                            ";")

SHIP_UTILITY_EFFECTS_STMT = ("INSERT INTO TIUtilityEffects"
                             "(module_name, rule)"
                             "VALUES "
                             "(:_dataName, :_rule)"
                             ";")

SHIP_WEAPON_MODULE_STMT = ("INSERT INTO TIWeapons"
                           "(module_name, module_mass, mount_type,"
                           "can_attack, can_defend, crew_needed)"
                           "VALUES "
                           "(:dataName, :baseWeaponMass_tons, "
                           ":mount, :attackMode, :defenseMode,"
                           ":crew)"
                           ";")

SHIP_MISSILE_WEAPON_STMT = ("INSERT INTO TIMissiles"
                            "(module_name, thrust, warhead_class,"
                            "exhaust_velocity, acceleration, delta_v,"
                            "magazine, flat_damage, bombardment_value,"
                            "chipping, targetable, range, cone_angle,"
                            "ammo_mass, fuel_mass, system_mass, warhead_mass,"
                            "thrust_ramp, turn_ramp, maneuver_angle,"
                            "rotation, pivot_range)"
                            "VALUES "
                            "(:dataName, :_thrust, :warheadClass, "
                            ":EV_kps, :acceleration_g, :deltaV_kps, "
                            ":magazine, :flatDamage_MJ, :bombardmentValue,"
                            ":flatChipping, :isPointDefenseTargetable,"
                            ":targetingRange_km, :shapedChargeAngle, "
                            ":ammoMass_kg, :fuelMass_kg, :systemMass_kg,"
                            ":warheadMass_kg, :thrustRamp_s, :turnRamp_s,"
                            ":maneuver_angle, :rotation_degps, :pivotRange_deg)"
                            ";")

SHIP_LASER_WEAPON_STMT = ("INSERT INTO TILasers"
                          "(module_name, wavelength, mirror_radius,"
                          "beam_quality, jitter_radius, shot_power,"
                          "efficiency, cooldown, bombardment_value,"
                          "range, pivot, hit_points)"
                          "VALUES "
                          "(:dataName, :wavelength_nm, :mirrorRadius_cm,"
                          ":beam_quality, :jitter_Rad, :shotPower_MJ,"
                          ":efficiency, :cooldown_s, :bombardmentValue,"
                          ":targetingRange_km, :pivotRange_deg, :hp)"
                          ";")

SHIP_MAGNETIC_GUN_WEAPON_STMT = ("INSERT INTO TIMagneticGuns"
                                 "(module_name, magazine, muzzle_velocity,"
                                 "efficiency, chipping, ammo_mass, warhead_mass,"
                                 "targetable, bombardment_value, range, pivot, "
                                 "cooldown, salvo_count, salvo_cooldown)"
                                 "VALUES "
                                 "(:dataName, :magazine, :muzzleVelocity_kps, "
                                 ":efficiency, :flatChipping, :ammoMass_kg, "
                                 ":warheadMass_kg, :isPointDefenseTargetable,"
                                 ":bombardmentValue, :targetingRange_km, :pivotRange_deg, "
                                 ":cooldown_s, :salvo_shots, :intraSalvoCooldown_s)"
                                 ";")

SHIP_CONVENTIONAL_GUN_WEAPON_STMT = ("INSERT INTO TIConventionalGuns"
                                 "(module_name, magazine, muzzle_velocity,"
                                 "efficiency, chipping, ammo_mass, warhead_mass,"
                                 "targetable, bombardment_value, range, pivot, "
                                 "cooldown, salvo_count, salvo_cooldown)"
                                 "VALUES "
                                 "(:dataName, :magazine, :muzzleVelocity_kps, "
                                 ":efficiency, :flatChipping, :ammoMass_kg, "
                                 ":warheadMass_kg, :isPointDefenseTargetable,"
                                 ":bombardmentValue,:targetingRange_km, :pivotRange_deg, "
                                 ":cooldown_s, :salvo_shots, :intraSalvoCooldown_s)"
                                 ";")

SHIP_PLASMA_WEAPON_STMT = ("INSERT INTO TIPlasmaWeapons"
                           "(module_name, magazine, charging_energy,"
                           "muzzle_velocity, warhead_mass, efficiency,"
                           "chipping, cooldown, bombardment_value, targetable,"
                           "range, pivot)"
                           "VALUES "
                           "(:dataName, :magazine, :chargingEnergy_MJ,"
                           ":muzzleVelocity_kps, :warheadMass_kg, :efficiency, "
                           ":flatChipping, :cooldown_s, :bombardmentValue, "
                           ":isPointDefenseTargetable, :targetingRange_km,  "
                           ":pivotRange_deg)"
                           ";")

SHIP_PARTICLE_WEAPON_STMT = ("INSERT INTO TIParticleWeapons"
                             "(module_name, shot_power, efficiency,"
                             "heat_fraction, xray_fraction, baryon_fraction,"
                             "bombardment_value, cooldown, dispersion_model,"
                             "lens_radius, range, doubling_range, pivot)"
                             "VALUES "
                             "(:dataName, :shotPower_MJ, :efficiency,"
                             ":heatFraction, :xRayFraction, :baryonFraction,"
                             ":bombardmentValue, :cooldown_s, :dispersionModel,"
                             ":lensRadius_cm, :targetingRange_km, :doublingRange_km,"
                             ":pivotRange_deg)"
                             ";")

SHIP_ARMOR_MODULE_STMT = ("INSERT INTO TIArmor"
                          "(module_name, density, vaporization, "
                          "baryonic_rating, xray_rating)"
                          "VALUES "
                          "(:dataName, :density_kgm3,"
                          ":heatofVaporization_MJkg, "
                          ":baryonicHalfValue_cm,"
                          ":xRayHalfValue_cm )"
                          ";")

SHIP_ARMOR_SPECIALTY_STMT = ("INSERT INTO TIArmorSpecialization"
                             "(module_name, specialization, value)"
                             "VALUES "
                             "(:_dataName, :_spec, :_value)"
                             ";")





#Factions and technologies

def insert_global_technology(json_object, database):
    cursor = database.cursor()

    contents = { "_type" : "Global" }
    contents.update( json_object )

    #I don't know if there are any which don't have this field, but I am adding it anyway
    if not "AI_criticalTech" in json_object:
        contents["AI_criticalTech"] = False

    cursor.execute(TECH_ENTRY_STMT, contents)
    cursor.execute(GLOBAL_TECH_STMT, contents)
    cursor.close()

def insert_project_technology(json_object, database):
    cursor = database.cursor()

    contents = { "_type" : "Project" }
    contents.update( json_object )

    #This value doesn't always appear in the projects template file
    if not "AI_criticalTech" in json_object:
        contents["AI_criticalTech"] = False

    #There are some which don't always appear
    if not "oneTimeGlobally" in json_object:
        contents["oneTimeGlobally"] = False

    if not "repeatable" in json_object:
        contents["repeatable"] = False

    cursor.execute(TECH_ENTRY_STMT, contents)
    cursor.execute(PROJECT_TECH_STMT, contents)
    cursor.close()

def insert_tech_prerequisites(json_object, database):
    cursor = database.cursor()

    #Pavonis erroneously included some duplicated entries, which has to be handled here
    used = {}
    for prereq in json_object["prereqs"]:
        if not prereq in used:
            cursor.execute(TECH_PREREQ_STMT, { "_dataName": json_object["dataName"], "_pr" : prereq })
            used[prereq] = True

    cursor.close()

def insert_faction(json_object, database):
    cursor = database.cursor()
    cursor.execute(FACTION_STMT, json_object)
    cursor.close()

def insert_faction_requirements(json_object, database):
    cursor = database.cursor()
    for fp in json_object["factionPrereq"]:
        cursor.execute(FACTION_PREREQ_STMT, { "_dataName": json_object["dataName"], "_faction" : fp })
    cursor.close()




#Standard Modules

def insert_base_module(contents, cursor):
    if not "requiredProjectName" in contents or contents["requiredProjectName"].strip() == "":
        contents["requiredProjectName"] = "Base"

    #If Pavonis is using displayName instead of friendlyName
    if "displayName" in contents:
        contents["friendlyName"] = contents["displayName"]

    cursor.execute(SHIP_MODULE_STMT, contents)

def insert_hull_module(json_object, database):
    cursor = database.cursor()

    contents = { "_type" : "hull" }
    contents.update( json_object )
    insert_base_module(contents, cursor)
    cursor.execute(SHIP_HULL_MODULE_STMT, contents)
    cursor.close()

def insert_power_plant_module(json_object, database):
    cursor = database.cursor()

    contents = { "_type" : "power_plant" }
    contents.update( json_object )
    insert_base_module(contents, cursor)
    cursor.execute(SHIP_POWER_PLANT_MODULE_STMT, contents)
    cursor.close()

def insert_drive_module(json_object, database):
    cursor = database.cursor()

    contents = {"_type" : "drive" }

    #chop off the last 2 characters
    contents.update( {
        "_commonDrive": json_object["dataName"][:-2],
        "_requiredPower": json_object["req power"], #Pavonis added a space in the key name for some reason
    } )


    if not "helium3Fuel" in json_object:
        contents["helium3Fuel"] = False

    contents.update( json_object)

    insert_base_module(contents, cursor)
    cursor.execute(SHIP_DRIVE_MODULE_STMT, contents)
    cursor.close()

def insert_radiator_module( json_object, database ):
    cursor = database.cursor()
    contents = { "_type" : "radiator" }
    contents.update( json_object )

    insert_base_module(contents, cursor)
    cursor.execute(SHIP_RADIATOR_MODULE_STMT, contents)
    cursor.close()

def insert_battery_module( json_object, database ):
    cursor = database.cursor()
    contents = { "_type" : "battery" }
    contents.update( json_object )

    insert_base_module(contents, cursor)
    cursor.execute(SHIP_BATTERY_MODULE_STMT, contents)
    cursor.close()

def insert_heat_sink_module( json_object, database ):
    cursor = database.cursor()
    contents = { "_type" : "heat_sink" }
    contents.update( json_object )

    insert_base_module(contents, cursor)
    cursor.execute(SHIP_HEAT_SINK_MODULE_STMT, contents)
    cursor.close()

def insert_utility_module( json_object, database ):
    cursor = database.cursor()

    contents = {
        "_type" : "utility",
    }

    #Do not insert the 'Empty' module
    if json_object["dataName"] == "Empty":
        return

    if not "noCombatRepair" in json_object:
        contents["noCombatRepair"] = False

    contents.update( json_object )

    insert_base_module(contents, cursor)
    cursor.execute(SHIP_UTILITY_MODULE_STMT, contents)
    cursor.close()

def insert_utility_module_effects( json_object, database ):
    cursor = database.cursor()


    for effect in json_object["specialModuleRules"]:
        contents = {
            "_dataName": json_object["dataName"],
            "_rule": effect,
        }
        cursor.execute( SHIP_UTILITY_EFFECTS_STMT, contents )

    cursor.close()


#Weapons modules

def insert_base_weapon_module(contents, cursor):
    insert_base_module(contents, cursor)

    #For uncrewed alien weapons
    if not "crew" in contents:
        contents["crew"] = 0

    cursor.execute(SHIP_WEAPON_MODULE_STMT, contents)

def insert_missile_weapon_module(json_object, database ):
    cursor = database.cursor()

    contents = { "_type" : "hull_weapon" } #all of them are hull weapons

    #If not nuclear shaped charge, this value will not be present
    if json_object["warheadClass"] != "ShapedNuclear":
        contents["shapedChargeAngle"] = None

    #Likely a penetrator type warhead
    if not "flatDamage_MJ" in json_object:
        contents["flatDamage_MJ"] = None


    contents.update( json_object )

    #Pavonis for some reason used spaces in the name along with an inconsistent name
    contents["_thrust"] = json_object["Rocket Thrust"]

    insert_base_weapon_module(contents, cursor)
    cursor.execute(SHIP_MISSILE_WEAPON_STMT, contents)

    cursor.close()


def insert_laser_weapon_module(json_object, database ):
    cursor = database.cursor()

    #Skip region and base defense laser modules since we only want ship mounts
    if "Region" in json_object["mount"] or "Base" in json_object["mount"]:
        return

    #Check nose or hull
    mount_type = check_mount_type(json_object["mount"])

    contents = {"_type" : mount_type }
    contents.update( json_object )

    insert_base_weapon_module(contents, cursor)
    cursor.execute(SHIP_LASER_WEAPON_STMT, contents)
    cursor.close()

def insert_magnetic_gun_weapon_module(json_object, database ):
    cursor = database.cursor()

    #Check nose or hull
    mount_type = check_mount_type(json_object["mount"])

    contents = {"_type" : mount_type }

    if not "salvo_shots" in json_object:
        contents["salvo_shots"] = None
        contents["intraSalvoCooldown_s"] = None

    contents.update( json_object )

    insert_base_weapon_module(contents, cursor)
    cursor.execute(SHIP_MAGNETIC_GUN_WEAPON_STMT, contents)

    cursor.close()

def insert_conventional_gun_weapon_module(json_object, database ):
    cursor = database.cursor()

    #Check nose or hull
    mount_type = check_mount_type(json_object["mount"])

    contents = {"_type" : mount_type }
    contents.update( json_object )

    insert_base_weapon_module(contents, cursor)
    cursor.execute(SHIP_CONVENTIONAL_GUN_WEAPON_STMT, contents)

    cursor.close()


def insert_plasma_weapon_module(json_object, database ):
    cursor = database.cursor()

    #Check nose or hull
    mount_type = check_mount_type(json_object["mount"])

    contents = {"_type" : mount_type }
    contents.update( json_object )

    insert_base_weapon_module(contents, cursor)
    cursor.execute(SHIP_PLASMA_WEAPON_STMT, contents)

    cursor.close()

def insert_particle_weapon_module(json_object, database):
    cursor = database.cursor()

    # Check nose or hull
    mount_type = check_mount_type(json_object["mount"])

    contents = {"_type": mount_type}
    contents.update(json_object)


    #the particle beams don't have a doubling range, but do have an emitance
    if not "doublingRange_km" in json_object:
        contents["doublingRange_km"] = None

    if not "emittance_mrad" in json_object:
        contents["emittance_mrad"] = None

    insert_base_weapon_module(contents, cursor)
    cursor.execute(SHIP_PARTICLE_WEAPON_STMT, contents)

    cursor.close()

def insert_armor_module(json_object, database ):
    cursor = database.cursor()

    contents = {"_type": "armor"}
    contents.update(json_object)

    insert_base_module(contents, cursor)
    cursor.execute(SHIP_ARMOR_MODULE_STMT, contents)

    cursor.close()

def insert_armor_specialties(json_object, database ):
    cursor = database.cursor()

    for specialty_object in json_object["specialties"]:
        contents = {
            "_dataName": json_object["dataName"],
            "_spec": specialty_object["armorSpecialty"],
            "_value": specialty_object["value"]
        }
        cursor.execute(SHIP_ARMOR_SPECIALTY_STMT, contents)

    cursor.close()


#Utility functions
def check_mount_type(mount_string):
    if "Hull" in mount_string:
        return "hull_weapon"
    elif "Nose" in mount_string:
        return "nose_weapon"



def dispatch_to_table( template, json_object, database ):
    match template:
        case "TIBatteryTemplate":
            insert_battery_module(json_object, database)
        case "TIDriveTemplate":
            insert_drive_module(json_object, database)
        case "TIFactionTemplate":
            insert_faction(json_object, database)
        case "TIGunTemplate":
            insert_conventional_gun_weapon_module(json_object, database)
        case "TIHeatSinkTemplate":
            insert_heat_sink_module(json_object, database)
        case "TILaserWeaponTemplate":
            insert_laser_weapon_module(json_object, database)
        case "TIMagneticGunTemplate":
            insert_magnetic_gun_weapon_module(json_object, database)
        case "TIMissileTemplate":
            insert_missile_weapon_module(json_object, database)
        case "TIParticleWeaponTemplate":
            insert_particle_weapon_module(json_object, database)
        case "TIPlasmaWeaponTemplate":
            insert_plasma_weapon_module(json_object, database)
        case "TIPowerPlantTemplate":
            insert_power_plant_module(json_object, database)
        case "TIProjectTemplate":
            insert_project_technology(json_object, database)
        case "TIRadiatorTemplate":
            insert_radiator_module(json_object, database)
        case "TIShipArmorTemplate":
            insert_armor_module(json_object, database)
        case "TIShipHullTemplate":
            insert_hull_module(json_object, database)
        case "TITechTemplate":
            insert_global_technology(json_object, database)
        case "TIUtilityModuleTemplate":
            insert_utility_module(json_object, database)
        case _:
            raise ValueError(f"Unknown template: {template}")


def insert_json_objects(template, json_object_array, database):
    for json_object in json_object_array:
        if not entry_disabled(json_object):
            dispatch_to_table( template, json_object, database )

def insert_tech_prereqs(json_object_array, database):
    for json_object in json_object_array:
        if not entry_disabled(json_object) and "prereqs" in json_object:
            insert_tech_prerequisites(json_object, database)


def insert_faction_prereqs(json_object_array, database):
    for json_object in json_object_array:
        if not entry_disabled(json_object) and "factionPrereq" in json_object:
            insert_faction_requirements(json_object, database)

def insert_utility_effects(json_object_array, database):
    for json_object in json_object_array:
        if not entry_disabled(json_object) and "specialModuleRules" in json_object:
            insert_utility_module_effects(json_object, database)

def insert_armor_specializations(json_object_array, database):
    for json_object in json_object_array:
        if not entry_disabled(json_object) and "specialties" in json_object:
            insert_armor_specialties(json_object, database)

def entry_disabled(json_object):
    return "disable" in json_object and json_object["disable"]

def load_json( file ):
    return json.load( file )

def load_file( path, destination ):
    file = open( path, "r" )

    #we can infer the file via its name
    file_name = os.path.basename( file.name )
    readable_name = file_name.replace(".json", "")
    json_body = load_json( file )

    destination[readable_name] = {
        "file" : file_name,
        "path" : path,
        "body" : json_body,
    }


def load_directory(directory, destination ):
    for file in os.listdir(directory):
        file_path = os.path.join(directory, file)
        if os.path.isfile(file_path) and file.endswith(".json"):
            load_file(file_path, destination)

def update_db( config ):
    entries = {}

    load_directory( config["base-directory"], entries )
    #We can also supplant entries with user-defined replacements, such as with mods

    database = None
    try:
        database = sqlite3.connect(config["database"])
        database.row_factory = sqlite3.Row
    except sqlite3.Error as e:
        print_error(f"Error while connecting to database: {e}")
        exit(1)



    try:
        database.execute("PRAGMA foreign_keys = ON")
        database.execute("BEGIN TRANSACTION")

        #The order of operations is important
        insert_json_objects("TIFactionTemplate", entries["TIFactionTemplate"]["body"], database)
        insert_json_objects("TITechTemplate", entries["TITechTemplate"]["body"], database)
        insert_json_objects("TIProjectTemplate", entries["TIProjectTemplate"]["body"], database)

        #We can insert the rest of the modules once the base techs are inserted
        insert_json_objects("TIBatteryTemplate", entries["TIBatteryTemplate"]["body"], database)
        insert_json_objects("TIDriveTemplate", entries["TIDriveTemplate"]["body"], database)
        insert_json_objects("TIGunTemplate", entries["TIGunTemplate"]["body"], database)
        insert_json_objects("TIHeatSinkTemplate", entries["TIHeatSinkTemplate"]["body"], database)
        insert_json_objects("TILaserWeaponTemplate", entries["TILaserWeaponTemplate"]["body"], database)
        insert_json_objects("TIMagneticGunTemplate", entries["TIMagneticGunTemplate"]["body"], database)
        insert_json_objects("TIMissileTemplate", entries["TIMissileTemplate"]["body"], database)
        insert_json_objects("TIParticleWeaponTemplate", entries["TIParticleWeaponTemplate"]["body"], database)
        insert_json_objects("TIPlasmaWeaponTemplate", entries["TIPlasmaWeaponTemplate"]["body"], database)
        insert_json_objects("TIPowerPlantTemplate", entries["TIPowerPlantTemplate"]["body"], database)
        insert_json_objects("TIRadiatorTemplate", entries["TIRadiatorTemplate"]["body"], database)
        insert_json_objects("TIShipArmorTemplate", entries["TIShipArmorTemplate"]["body"], database)
        insert_json_objects("TIShipHullTemplate", entries["TIShipHullTemplate"]["body"], database)
        insert_json_objects("TIUtilityModuleTemplate", entries["TIUtilityModuleTemplate"]["body"], database)

        #Update relations
        insert_tech_prereqs( entries["TITechTemplate"]["body"], database )
        insert_tech_prereqs( entries["TIProjectTemplate"]["body"], database )
        insert_faction_prereqs( entries["TIProjectTemplate"]["body"], database )
        insert_utility_effects( entries["TIUtilityModuleTemplate"]["body"], database )
        insert_armor_specializations( entries["TIShipArmorTemplate"]["body"], database )

        database.commit()
    except sqlite3.Error as e:
        print_error(f"Database error: {e}")
        database.rollback()
        exit(1)

def print_error(msg):
    print(msg, file=sys.stderr)
    traceback.print_exc(file=sys.stderr)


if __name__ == "__main__":
    program_config = {"database": "./testfile",
                      "base-directory": "./testfiles"}

    update_db(program_config)

    exit(0)