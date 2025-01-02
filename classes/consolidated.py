import copy
import os
import sqlite3
import json
import sys

class TerraInvictaDatabaseLoader:
    __TECH_ENTRY_STMT = ("INSERT INTO TITechEntries"
                       "( internal_name, friendly_name, ai_critical, tech_type, category, role, cost )"
                       "VALUES"
                       "( :dataName, :friendlyName, :AI_criticalTech, :_type, :techCategory, :AI_techRole, :researchCost)"
                       ";")

    __GLOBAL_TECH_STMT = ("INSERT INTO TIGlobalTechnologies"
                              "(internal_name, end_game_tech)"
                              "VALUES"
                              "(:dataName, :endGameTech)"
                        ";")

    __PROJECT_TECH_STMT = ("INSERT INTO TIProjects"
                         "( internal_name, globally_shared, repeatable )"
                         "VALUES "
                         "( :dataName, :oneTimeGlobally, :repeatable )"
                         ";")

    __TECH_PREREQ_STMT = ("INSERT INTO TIPrerequisites"
                        "(internal_name, requires)"
                        "VALUES "
                        "(:_dataName, :_pr)"
                        ";")

    __FACTION_STMT = ("INSERT INTO TIFactions"
                    "(faction_internal, faction_common)"
                    "VALUES "
                    "(:dataName, :friendlyName)"
                    ";")

    __FACTION_PREREQ_STMT = ("INSERT INTO TIFactionPrerequisites"
                           "(internal_name, faction)"
                           "VALUES "
                           "(:_dataName, :_faction)"
                           ";")

    __SHIP_MODULE_STMT = ("INSERT INTO TIShipModules"
                        "(module_name, friendly_name, required_project, module_type)"
                        "VALUES "
                        "(:dataName, :friendlyName, :requiredProjectName, :_type)"
                        ";")

    __SHIP_HULL_MODULE_STMT = ("INSERT INTO TIShipHulls"
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

    __SHIP_POWER_PLANT_MODULE_STMT = ("INSERT INTO TIPowerPlants"
                                    "(module_name, plant_class,"
                                    "max_power, specific_power,"
                                    "general_use, efficiency,"
                                    "crew_needed)"
                                    "VALUES "
                                    "(:dataName, :powerPlantClass, :maxOutput_GW,"
                                    ":specificPower_tGW, :generalUse, :efficiency,"
                                    ":crew)"
                                    ";")

    __SHIP_DRIVE_MODULE_STMT = ("INSERT INTO TIDrives"
                              "(module_name, common_drive_name, thruster_count,"
                              "drive_class, power_plant_class, thrust,"
                              "exhaust_velocity, efficiency, power_needed,"
                              "rating, flat_mass, cooling_cycle, combat_cap)"
                              "VALUES "
                              "(:dataName, :_commonDrive, :thrusters, "
                              ":driveClassification, :requiredPowerPlant,"
                              ":thrust_N, :EV_kps, :efficiency, :_requiredPower, "
                              ":thrustRating_GW, :flatMass_tons, :cooling,"
                              ":thrustCap )"
                              ";")

    __SHIP_DRIVE_PROPELLANT_STMT = ("INSERT INTO TIDrivePropellant"
                                  "(module_name, uses_helium3, propellant,"
                                  "water, volatiles, metals, nobleMetals,"
                                  "fissiles, exotics, antimatter)"
                                  "VALUES "
                                  "(:dataName, :helium3Fuel, :propellant,"
                                  ":water, :volatiles, :metals, :nobleMetals, "
                                  ":fissiles, :exotics, :antimatter)"
                                  ";")

    __SHIP_RADIATOR_MODULE_STMT = ("INSERT INTO TIRadiators"
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

    __SHIP_RADIATOR_COMPOSITION_STMT = ("INSERT INTO TIRadiatorComposition"
                                   "(module_name, water, volatiles,"
                                   "metals, nobleMetals, fissiles,"
                                   "exotics, antimatter)"
                                   "VALUES "
                                   "(:dataName, :water, :volatiles, "
                                   ":metals, :nobleMetals, :fissiles, "
                                   ":exotics, :antimatter)"
                                   ";")

    __SHIP_BATTERY_MODULE_STMT = ("INSERT INTO TIBatteries"
                                "(module_name, capacity,"
                                "recharge_rate, mass,"
                                "crew_needed, hit_points)"
                                "VALUES "
                                "(:dataName, :energyCapacity_GJ,"
                                ":rechargeRate_GJs, :mass_tons,"
                                ":crew, :hp)"
                                ";")

    __SHIP_HEAT_SINK_MODULE_STMT = ("INSERT INTO TIHeatSinks"
                               "(module_name, capacity, mass, crew_needed)"
                               "VALUES "
                               "(:dataName, :heatCapacity_GJ, :mass_tons, :crew)"
                               ";")

    __SHIP_UTILITY_MODULE_STMT = ("INSERT INTO TIUtilities"
                                "(module_name, no_combat_repair, power_requirement)"
                                "VALUES "
                                "(:dataName, :noCombatRepair, :powerRequirement_MW )"
                                ";")

    __SHIP_UTILITY_EFFECTS_STMT = ("INSERT INTO TIUtilityEffects"
                                 "(module_name, rule)"
                                 "VALUES "
                                 "(:_dataName, :_rule)"
                                 ";")

    __SHIP_WEAPON_MODULE_STMT = ("INSERT INTO TIWeapons"
                               "(module_name, module_mass, mount_type,"
                               "can_attack, can_defend, crew_needed)"
                               "VALUES "
                               "(:dataName, :baseWeaponMass_tons, "
                               ":mount, :attackMode, :defenseMode,"
                               ":crew)"
                               ";")

    __SHIP_MISSILE_WEAPON_STMT = ("INSERT INTO TIMissiles"
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

    __SHIP_LASER_WEAPON_STMT = ("INSERT INTO TILasers"
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

    __SHIP_MAGNETIC_GUN_WEAPON_STMT = ("INSERT INTO TIMagneticGuns"
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

    __SHIP_CONVENTIONAL_GUN_WEAPON_STMT = ("INSERT INTO TIConventionalGuns"
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

    __SHIP_PLASMA_WEAPON_STMT = ("INSERT INTO TIPlasmaWeapons"
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

    __SHIP_PARTICLE_WEAPON_STMT = ("INSERT INTO TIParticleWeapons"
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

    __SHIP_ARMOR_MODULE_STMT = ("INSERT INTO TIArmor"
                              "(module_name, density, vaporization, "
                              "baryonic_rating, xray_rating)"
                              "VALUES "
                              "(:dataName, :density_kgm3,"
                              ":heatofVaporization_MJkg, "
                              ":baryonicHalfValue_cm,"
                              ":xRayHalfValue_cm )"
                              ";")

    __SHIP_ARMOR_SPECIALTY_STMT = ("INSERT INTO TIArmorSpecialization"
                                 "(module_name, specialization, value)"
                                 "VALUES "
                                 "(:_dataName, :_spec, :_value)"
                                 ";")

    __SHIP_ARMOR_COMPOSITION_STMT = ("INSERT INTO TIArmorComposition"
                                   "(module_name, water, volatiles,"
                                   "metals, nobleMetals, fissiles,"
                                   "exotics, antimatter)"
                                   "VALUES "
                                   "(:dataName, :water, :volatiles, "
                                   ":metals, :nobleMetals, :fissiles, "
                                   ":exotics, :antimatter)"
                                   ";")

    #Our database connection, which is updated on execution
    __database = None



    #Factions and technologies

    def __insert_global_technology(self, json_object):
        cursor = self.__database.cursor()

        contents = { "_type" : "Global" }
        contents.update( json_object )

        #I don't know if there are any which don't have this field, but I am adding it anyway
        if not "AI_criticalTech" in json_object:
            contents["AI_criticalTech"] = False

        cursor.execute(self.__TECH_ENTRY_STMT, contents)
        cursor.execute(self.__GLOBAL_TECH_STMT, contents)
        cursor.close()

    def __insert_project_technology(self, json_object):
        cursor = self.__database.cursor()

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

        cursor.execute(self.__TECH_ENTRY_STMT, contents)
        cursor.execute(self.__PROJECT_TECH_STMT, contents)
        cursor.close()

    def __insert_tech_prerequisites(self, json_object):
        cursor = self.__database.cursor()

        #Pavonis erroneously included some duplicated entries, which has to be handled here
        used = {}
        for prereq in json_object["prereqs"]:
            if not prereq in used:
                cursor.execute(self.__TECH_PREREQ_STMT, {"_dataName": json_object["dataName"], "_pr" : prereq})
                used[prereq] = True

        cursor.close()

    def __insert_faction(self, json_object):
        cursor = self.__database.cursor()
        cursor.execute(self.__FACTION_STMT, json_object)
        cursor.close()

    def __insert_faction_requirements(self, json_object):
        cursor = self.__database.cursor()
        for fp in json_object["factionPrereq"]:
            cursor.execute(self.__FACTION_PREREQ_STMT, {"_dataName": json_object["dataName"], "_faction" : fp})
        cursor.close()




    #Standard Modules

    def __insert_base_module(self, contents, cursor):
        if not "requiredProjectName" in contents or contents["requiredProjectName"].strip() == "":
            contents["requiredProjectName"] = "Base"

        #If Pavonis is using displayName instead of friendlyName
        if "displayName" in contents:
            contents["friendlyName"] = contents["displayName"]

        cursor.execute(self.__SHIP_MODULE_STMT, contents)

    def __insert_hull_module(self, json_object):
        cursor = self.__database.cursor()

        contents = { "_type" : "hull" }
        contents.update( json_object )
        self.__insert_base_module(contents, cursor)
        cursor.execute(self.__SHIP_HULL_MODULE_STMT, contents)
        cursor.close()

    def __insert_power_plant_module(self, json_object):
        cursor = self.__database.cursor()

        contents = { "_type" : "power_plant" }
        contents.update( json_object )
        self.__insert_base_module(contents, cursor)
        cursor.execute(self.__SHIP_POWER_PLANT_MODULE_STMT, contents)
        cursor.close()

    def __insert_drive_propellant(self, common_name, json_object):
        contents = {
            "dataName": None,
            "helium3Fuel": False,
            "propellant": None,
            "water": "0",
            "volatiles": "0",
            "metals": "0",
            "nobleMetals": "0",
            "fissiles": "0",
            "exotics": "0",
            "antimatter": "0"
        }


        contents.update( { key: json_object[key] for key in contents if key in json_object } )
        contents.update( {key: json_object["perTankPropellantMaterials"][key] for key in contents if key in json_object["perTankPropellantMaterials"] } )

        cursor = self.__database.cursor()
        cursor.execute(self.__SHIP_DRIVE_PROPELLANT_STMT, contents)

        cursor.close()


    def __insert_drive_module(self, json_object):
        cursor = self.__database.cursor()

        contents = {"_type" : "drive" }

        #chop off the last 2 characters
        common_drive_name = json_object["dataName"][:-2]

        contents.update( {
            "_commonDrive": common_drive_name,
            "_requiredPower": json_object["req power"], #Pavonis added a space in the key name for some reason, which will break the query
        } )


        #
        #if not "helium3Fuel" in json_object:
        #    contents["helium3Fuel"] = False#
        #

        contents.update( json_object)

        self.__insert_base_module(contents, cursor)
        cursor.execute(self.__SHIP_DRIVE_MODULE_STMT, contents)

        self.__insert_drive_propellant(common_drive_name, json_object)

        cursor.close()

    def __insert_radiator_module(self, json_object):
        cursor = self.__database.cursor()
        contents = { "_type" : "radiator" }
        contents.update( json_object )

        self.__insert_base_module(contents, cursor)
        cursor.execute(self.__SHIP_RADIATOR_MODULE_STMT, contents)
        self.__insert_radiator_composition(json_object)

        cursor.close()

    def __insert_radiator_composition(self, json_object):

        contents = {
            "dataName": json_object["dataName"],
            "water": "0",
            "volatiles": "0",
            "metals": "0",
            "nobleMetals": "0",
            "fissiles": "0",
            "exotics": "0",
            "antimatter": "0"
        }
        contents.update( {key: json_object["weightedBuildMaterials"][key] for key in contents if key in json_object["weightedBuildMaterials"] } )

        cursor = self.__database.cursor()
        cursor.execute(self.__SHIP_RADIATOR_COMPOSITION_STMT, contents)
        cursor.close()


    def __insert_battery_module(self, json_object):
        cursor = self.__database.cursor()
        contents = { "_type" : "battery" }
        contents.update( json_object )

        self.__insert_base_module(contents, cursor)
        cursor.execute(self.__SHIP_BATTERY_MODULE_STMT, contents)
        cursor.close()

    def __insert_heat_sink_module(self, json_object):
        cursor = self.__database.cursor()
        contents = { "_type" : "heat_sink" }
        contents.update( json_object )

        self.__insert_base_module(contents, cursor)
        cursor.execute(self.__SHIP_HEAT_SINK_MODULE_STMT, contents)
        cursor.close()

    def __insert_utility_module(self, json_object):
        cursor = self.__database.cursor()

        contents = {
            "_type" : "utility",
        }

        #Do not insert the 'Empty' module
        #I don't know why its in the file, but it is
        if json_object["dataName"] == "Empty":
            return

        if not "noCombatRepair" in json_object:
            contents["noCombatRepair"] = False

        contents.update( json_object )

        self.__insert_base_module(contents, cursor)
        cursor.execute(self.__SHIP_UTILITY_MODULE_STMT, contents)

        if "specialModuleRules" in json_object:
            self.__insert_utility_module_effects(json_object)

        cursor.close()

    def __insert_utility_module_effects(self, json_object):
        cursor = self.__database.cursor()


        for effect in json_object["specialModuleRules"]:
            contents = {
                "_dataName": json_object["dataName"],
                "_rule": effect,
            }
            cursor.execute(self.__SHIP_UTILITY_EFFECTS_STMT, contents)

        cursor.close()


    #Weapons modules

    def __insert_base_weapon_module(self, contents, cursor):
        self.__insert_base_module(contents, cursor)

        #For uncrewed alien weapons
        if not "crew" in contents:
            contents["crew"] = 0

        cursor.execute(self.__SHIP_WEAPON_MODULE_STMT, contents)

    def __insert_missile_weapon_module(self, json_object):
        cursor = self.__database.cursor()

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

        self.__insert_base_weapon_module(contents, cursor)
        cursor.execute(self.__SHIP_MISSILE_WEAPON_STMT, contents)

        cursor.close()


    def __insert_laser_weapon_module(self, json_object):
        cursor = self.__database.cursor()

        #Skip region and base defense laser modules since we only want ship mounts
        if "Region" in json_object["mount"] or "Base" in json_object["mount"]:
            return

        #Check nose or hull
        mount_type = self.__check_mount_type(json_object["mount"])

        contents = {"_type" : mount_type }
        contents.update( json_object )

        self.__insert_base_weapon_module(contents, cursor)
        cursor.execute(self.__SHIP_LASER_WEAPON_STMT, contents)
        cursor.close()

    def __insert_magnetic_gun_weapon_module(self, json_object):
        cursor = self.__database.cursor()

        #Check nose or hull
        mount_type = self.__check_mount_type(json_object["mount"])

        contents = {"_type" : mount_type }

        if not "salvo_shots" in json_object:
            contents["salvo_shots"] = None
            contents["intraSalvoCooldown_s"] = None

        contents.update( json_object )

        self.__insert_base_weapon_module(contents, cursor)
        cursor.execute(self.__SHIP_MAGNETIC_GUN_WEAPON_STMT, contents)

        cursor.close()

    def __insert_conventional_gun_weapon_module(self, json_object):
        cursor = self.__database.cursor()

        #Check nose or hull
        mount_type = self.__check_mount_type(json_object["mount"])

        contents = {"_type" : mount_type }
        contents.update( json_object )

        self.__insert_base_weapon_module(contents, cursor)
        cursor.execute(self.__SHIP_CONVENTIONAL_GUN_WEAPON_STMT, contents)

        cursor.close()


    def __insert_plasma_weapon_module(self, json_object):
        cursor = self.__database.cursor()

        #Check nose or hull
        mount_type = self.__check_mount_type(json_object["mount"])

        contents = {"_type" : mount_type }
        contents.update( json_object )

        self.__insert_base_weapon_module(contents, cursor)
        cursor.execute(self.__SHIP_PLASMA_WEAPON_STMT, contents)

        cursor.close()

    def __insert_particle_weapon_module(self, json_object):
        cursor = self.__database.cursor()

        # Check nose or hull
        mount_type = self.__check_mount_type(json_object["mount"])

        contents = {"_type": mount_type}
        contents.update(json_object)


        #the particle beams don't have a doubling range, but do have an emitance
        if not "doublingRange_km" in json_object:
            contents["doublingRange_km"] = None

        if not "emittance_mrad" in json_object:
            contents["emittance_mrad"] = None

        self.__insert_base_weapon_module(contents, cursor)
        cursor.execute(self.__SHIP_PARTICLE_WEAPON_STMT, contents)

        cursor.close()

    def __insert_armor_module(self, json_object):
        cursor = self.__database.cursor()

        contents = {"_type": "armor"}
        contents.update(json_object)

        self.__insert_base_module(contents, cursor)
        cursor.execute(self.__SHIP_ARMOR_MODULE_STMT, contents)

        #insert build materials
        self.__insert_armor_composition(json_object)

        if "specialties" in json_object:
            self.__insert_armor_specialties(json_object)

        cursor.close()

    def __insert_armor_specialties(self, json_object):
        cursor = self.__database.cursor()

        for specialty_object in json_object["specialties"]:
            contents = {
                "_dataName": json_object["dataName"],
                "_spec": specialty_object["armorSpecialty"],
                "_value": specialty_object["value"]
            }
            cursor.execute(self.__SHIP_ARMOR_SPECIALTY_STMT, contents)

        cursor.close()

    def __insert_armor_composition(self, json_object):
        cursor = self.__database.cursor()

        contents = {
            "dataName": None,
            "water": "0",
            "volatiles": "0",
            "metals": "0",
            "nobleMetals": "0",
            "fissiles": "0",
            "exotics": "0",
            "antimatter": "0"
        }


        contents.update( { key: json_object[key] for key in contents if key in json_object } )
        contents.update( {key: json_object["weightedBuildMaterials"][key] for key in contents if key in json_object["weightedBuildMaterials"] } )


        cursor.execute(self.__SHIP_ARMOR_COMPOSITION_STMT, contents)
        cursor.close()

    #Utility functions
    @staticmethod
    def __check_mount_type(mount_string):
        if "Hull" in mount_string:
            return "hull_weapon"
        elif "Nose" in mount_string:
            return "nose_weapon"

    @staticmethod
    def __entry_disabled(json_object):
        return "disable" in json_object and json_object["disable"]

    @staticmethod
    def __load_json(file):
        return json.load( file )


    def __handle_json_contents(self, entries, template_name, callback):
        json_object_array = entries[template_name]["body"]
        for json_object in json_object_array:
            if not self.__entry_disabled(json_object):
                callback(json_object)

    def __handle_tech_prerequisites(self, entries):
        json_object_array_global = entries["TITechTemplate"]["body"]
        json_object_array_projects = entries["TIProjectTemplate"]["body"]

        for json_object in json_object_array_global:
            if not self.__entry_disabled(json_object) and "prereqs" in json_object:
                self.__insert_tech_prerequisites(json_object)

        for json_object in json_object_array_projects:
            if not self.__entry_disabled(json_object) and "prereqs" in json_object:
                self.__insert_tech_prerequisites(json_object)

    def __handle_faction_requirements(self, entries):
        json_object_array = entries.get("TIProjectTemplate")["body"]
        for json_object in json_object_array:
            if not self.__entry_disabled(json_object) and "factionPrereq" in json_object:
                self.__insert_faction_requirements(json_object)


    def __load_file(self, path, destination):
        file = open( path, "r" )

        #we can infer the file via its name
        file_name = os.path.basename( file.name )
        template_name = file_name.replace(".json", "")
        json_body = self.__load_json(file)

        destination[template_name] = {
            "file" : file_name,
            "path" : path,
            "body" : json_body,
        }

    def __load_paths(self, path_list, destination):
        for path in path_list:
            if os.path.isfile(path) and path.endswith(".json"):
                self.__load_file(path, destination)
            else:
                raise ValueError(f"File {path} does not exist")

    def update_db( self, path_list, database_url ):
        entries = {}
        self.__load_paths(path_list, entries)

        try:
            self.__database = sqlite3.connect(database_url)
            self.__database.row_factory = sqlite3.Row
        except sqlite3.Error as e:
            raise IOError(f"Error while connecting to database: {e}", e)

        try:
            # Check if the database is already filled, we don't want to populate with double values

            cursor = self.__database.cursor()
            cursor.execute("SELECT entry_value from TIDatabaseInfo where entry_name = 'db_populated';")
            value = cursor.fetchone()["entry_value"]
            if value.lower() == "true":
                cursor.close()
                raise ValueError(f"{database_url} is already populated")


            self.__database.execute("PRAGMA foreign_keys = ON")
            self.__database.execute("BEGIN TRANSACTION")

            #Handle factions, global techs, then project techs, the order is important
            self.__handle_json_contents(entries, "TIFactionTemplate", self.__insert_faction)
            self.__handle_json_contents(entries, "TITechTemplate", self.__insert_global_technology)
            self.__handle_json_contents(entries, "TIProjectTemplate", self.__insert_project_technology)

            #We can now update the prerequisites for techs
            self.__handle_tech_prerequisites(entries)
            self.__handle_faction_requirements(entries)

            #Add modules, order isn't important here, once techs are inserted
            self.__handle_json_contents(entries, "TIShipHullTemplate", self.__insert_hull_module)
            self.__handle_json_contents(entries, "TIPowerPlantTemplate", self.__insert_power_plant_module)
            self.__handle_json_contents(entries, "TIBatteryTemplate", self.__insert_battery_module)
            self.__handle_json_contents(entries, "TIHeatSinkTemplate", self.__insert_heat_sink_module)
            self.__handle_json_contents(entries, "TIRadiatorTemplate", self.__insert_radiator_module)
            self.__handle_json_contents(entries, "TIDriveTemplate", self.__insert_drive_module)
            self.__handle_json_contents(entries, "TIUtilityModuleTemplate", self.__insert_utility_module)
            self.__handle_json_contents(entries, "TIShipArmorTemplate", self.__insert_armor_module)

            #Ballistic Weapons
            self.__handle_json_contents(entries, "TIGunTemplate", self.__insert_conventional_gun_weapon_module)
            self.__handle_json_contents(entries, "TIMagneticGunTemplate", self.__insert_magnetic_gun_weapon_module)
            self.__handle_json_contents(entries, "TIMissileTemplate", self.__insert_missile_weapon_module)

            #Energy weapons
            self.__handle_json_contents(entries, "TILaserWeaponTemplate", self.__insert_laser_weapon_module)
            self.__handle_json_contents(entries, "TIPlasmaWeaponTemplate", self.__insert_plasma_weapon_module)
            self.__handle_json_contents(entries, "TIParticleWeaponTemplate", self.__insert_particle_weapon_module)


            self.__database.execute("UPDATE TIDatabaseInfo set entry_value = 'true' where entry_name = 'db_populated';")

            self.__database.commit()
        except sqlite3.Error as e:
            self.__database.rollback()
            raise IOError(f"Error while updating database. Transaction rolled back: {e}", e)
        finally:
            try:
                self.__database.close()
            except sqlite3.Error as e:
                _eg, exception, _tb = sys.exc_info()
                if exception is not None:
                    nex = copy.copy( e )
                    nex.__cause__ = exception

                    raise IOError(f"Error while closing database: {e}", nex)
                else:
                    raise IOError(f"Error while closing database. {e}", e)






if __name__ == "__main__":
    dbhandler = TerraInvictaDatabaseLoader()

    #delete the database every time
    if os.path.exists("../test_database.db"):
        os.remove("../test_database.db")

    sqlite3.connect("../test_database.db").executescript(open("../tidb.sql", "r").read()).close()

    path_list = []
    for root, dirs, files in os.walk("../testfiles"):
        for name in files:
            path_list.append(os.path.abspath( os.path.join( root, name ) ))

    dbhandler.update_db(path_list, "./test_database.db")

