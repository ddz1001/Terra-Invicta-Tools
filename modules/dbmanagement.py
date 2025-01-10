import copy
import os
import sqlite3
import json
import sys
import logging
import re

class TerraInvictaDatabaseManager:
    __TECH_ENTRY_STMT = """ 
        INSERT INTO TITechEntries
           ( internal_name, friendly_name, ai_critical, tech_type, category, role, cost )
           VALUES
           ( :dataName, :friendlyName, :AI_criticalTech, :_type, :techCategory, :AI_techRole, :researchCost);
    """

    __GLOBAL_TECH_STMT = """
        INSERT INTO TIGlobalTechnologies
          (internal_name, end_game_tech)
          VALUES
          (:dataName, :endGameTech);
    """

    __PROJECT_TECH_STMT = """
        INSERT INTO TIProjects
             ( internal_name, globally_shared, repeatable )
             VALUES 
             ( :dataName, :oneTimeGlobally, :repeatable );
    """

    __TECH_PREREQ_STMT = """
        INSERT INTO TIPrerequisites
            (internal_name, requires)
            VALUES 
            (:_dataName, :_pr);
    """

    __FACTION_STMT = """
        INSERT INTO TIFactions
            (faction_internal, faction_common)
            VALUES 
            (:dataName, :friendlyName);
    """

    __FACTION_PREREQ_STMT = """
        INSERT INTO TIFactionPrerequisites
           (internal_name, faction)
           VALUES 
           (:_dataName, :_faction);
        """

    __SHIP_MODULE_STMT = """
        INSERT INTO TIShipModules
            (module_name, friendly_name, required_project, module_type)
            VALUES 
            (:dataName, :friendlyName, :requiredProjectName, :_type);
        """

    __SHIP_HULL_MODULE_STMT = """
        INSERT INTO TIShipHulls
             (module_name, alien_only, construction_tier,
             construction_time, maximum_officers,
             starting_crew, mission_control, 
             monthly_cost, base_mass, length,
             width, volume, structural_integrity,
             nose_hardpoints, hull_hardpoints,
             max_modules, thruster_multiplier)
             VALUES 
             (:dataName, :alien, :consTier, 
             :baseConstructionTime_days, 
             :maxOfficers, :crew, :missionControl,:monthlyIncome_Money,
             :mass_tons, :length_m, :width_m, :volume,
             :structuralIntegrity, :noseHardpoints, :hullHardpoints,
             :internalModules, :thrusterMultiplier);
        """

    __SHIP_POWER_PLANT_MODULE_STMT = """ 
        INSERT INTO TIPowerPlants
            (module_name, plant_class,
            max_power, specific_power,
            general_use, efficiency,
            crew_needed)
            VALUES 
            (:dataName, :powerPlantClass, :maxOutput_GW,
            :specificPower_tGW, :generalUse, :efficiency,
            :crew);
        """

    __SHIP_DRIVE_MODULE_STMT = """
        INSERT INTO TIDrives
             (module_name, common_drive_name, thruster_count,
             drive_class, power_plant_class, thrust,
             exhaust_velocity, efficiency, power_needed,
             rating, flat_mass, cooling_cycle, combat_cap)
             VALUES 
             (:dataName, :_commonDrive, :thrusters, 
             :driveClassification, :requiredPowerPlant,
             :thrust_N, :EV_kps, :efficiency, :_requiredPower, 
             :thrustRating_GW, :flatMass_tons, :cooling,
             :thrustCap );
        """

    __SHIP_DRIVE_PROPELLANT_STMT = """
        INSERT INTO TIDrivePropellant
              (module_name, uses_helium3, propellant,
              water, volatiles, metals, nobleMetals,
              fissiles, exotics, antimatter)
              VALUES 
              (:dataName, :helium3Fuel, :propellant,
              :water, :volatiles, :metals, :nobleMetals, 
              :fissiles, :exotics, :antimatter);
        """

    __SHIP_RADIATOR_MODULE_STMT = """ 
        INSERT INTO TIRadiators
             (module_name, specific_mass,
             specific_power, operating_temperature,
             emissivity, vulnerability, crew_needed,
             radiator_type, collector)
             VALUES 
             (:dataName, :specificMass_2s_kgm2,
             :specificPower_2s_KWkg, 
             :operatingTemp_K,
             :emissivity, :vulnerability,
             :crew, :radiatorType, :collector);
            """

    __SHIP_MODULE_MATERIALS_STMT = """
        INSERT INTO TIModuleMaterials
           (module_name, water, volatiles,
           metals, nobleMetals, fissiles,
           exotics, antimatter)
           VALUES 
           (:dataName, :water, :volatiles, 
           :metals, :nobleMetals, :fissiles, 
           :exotics, :antimatter);
        """

    __SHIP_BATTERY_MODULE_STMT = """ 
        INSERT INTO TIBatteries
            (module_name, capacity,
            recharge_rate, mass,
            crew_needed, hit_points)
            VALUES 
            (:dataName, :energyCapacity_GJ,
            :rechargeRate_GJs, :mass_tons,
            :crew, :hp);
        """

    __SHIP_HEAT_SINK_MODULE_STMT = """
        INSERT INTO TIHeatSinks
           (module_name, capacity, mass, crew_needed)
           VALUES 
           (:dataName, :heatCapacity_GJ, :mass_tons, :crew);
        """

    __SHIP_UTILITY_MODULE_STMT = """
        INSERT INTO TIUtilities
            (module_name, no_combat_repair, power_requirement)
            VALUES 
            (:dataName, :noCombatRepair, :powerRequirement_MW );
        """

    __SHIP_UTILITY_EFFECTS_STMT = """
        INSERT INTO TIUtilityEffects
             (module_name, rule)
             VALUES 
             (:_dataName, :_rule);
             """

    __SHIP_WEAPON_MODULE_STMT = """
        INSERT INTO TIWeapons
           (module_name, module_mass, mount_type,
           can_attack, can_defend, crew_needed)
           VALUES 
           (:dataName, :baseWeaponMass_tons, 
           :mount, :attackMode, :defenseMode,
           :crew);
        """

    __SHIP_MISSILE_WEAPON_STMT = """
        INSERT INTO TIMissiles
            (module_name, thrust, warhead_class,
            exhaust_velocity, acceleration, delta_v,
            magazine, flat_damage, bombardment_value,
            chipping, targetable, range, cone_angle,
            ammo_mass, fuel_mass, system_mass, warhead_mass,
            thrust_ramp, turn_ramp, maneuver_angle,
            rotation, pivot_range)
            VALUES 
            (:dataName, :_thrust, :warheadClass, 
            :EV_kps, :acceleration_g, :deltaV_kps, 
            :magazine, :flatDamage_MJ, :bombardmentValue,
            :flatChipping, :isPointDefenseTargetable,
            :targetingRange_km, :shapedChargeAngle, 
            :ammoMass_kg, :fuelMass_kg, :systemMass_kg,
            :warheadMass_kg, :thrustRamp_s, :turnRamp_s,
            :maneuver_angle, :rotation_degps, :pivotRange_deg);
    """

    __SHIP_LASER_WEAPON_STMT = """ 
        INSERT INTO TILasers
          (module_name, wavelength, mirror_radius,
          beam_quality, jitter_radius, shot_power,
          efficiency, cooldown, bombardment_value,
          range, pivot, hit_points)
          VALUES 
          (:dataName, :wavelength_nm, :mirrorRadius_cm,
          :beam_quality, :jitter_Rad, :shotPower_MJ,
          :efficiency, :cooldown_s, :bombardmentValue,
          :targetingRange_km, :pivotRange_deg, :hp);
        """

    __SHIP_MAGNETIC_GUN_WEAPON_STMT = """
        INSERT INTO TIMagneticGuns
             (module_name, magazine, muzzle_velocity,
             efficiency, chipping, ammo_mass, warhead_mass,
             targetable, bombardment_value, range, pivot, 
             cooldown, salvo_count, salvo_cooldown)
             VALUES 
             (:dataName, :magazine, :muzzleVelocity_kps, 
             :efficiency, :flatChipping, :ammoMass_kg, 
             :warheadMass_kg, :isPointDefenseTargetable,
             :bombardmentValue, :targetingRange_km, :pivotRange_deg, 
             :cooldown_s, :salvo_shots, :intraSalvoCooldown_s);
        """

    __SHIP_CONVENTIONAL_GUN_WEAPON_STMT = """
        INSERT INTO TIConventionalGuns
             (module_name, magazine, muzzle_velocity,
             efficiency, chipping, ammo_mass, warhead_mass,
             targetable, bombardment_value, range, pivot, 
             cooldown, salvo_count, salvo_cooldown)
             VALUES 
             (:dataName, :magazine, :muzzleVelocity_kps, 
             :efficiency, :flatChipping, :ammoMass_kg, 
             :warheadMass_kg, :isPointDefenseTargetable,
             :bombardmentValue,:targetingRange_km, :pivotRange_deg, 
             :cooldown_s, :salvo_shots, :intraSalvoCooldown_s);
        """

    __SHIP_PLASMA_WEAPON_STMT = """ 
        INSERT INTO TIPlasmaWeapons
           (module_name, magazine, charging_energy,
           muzzle_velocity, warhead_mass, efficiency,
           chipping, cooldown, bombardment_value, targetable,
           range, pivot)
           VALUES 
           (:dataName, :magazine, :chargingEnergy_MJ,
           :muzzleVelocity_kps, :warheadMass_kg, :efficiency, 
           :flatChipping, :cooldown_s, :bombardmentValue, 
           :isPointDefenseTargetable, :targetingRange_km,  
           :pivotRange_deg);
        """

    __SHIP_PARTICLE_WEAPON_STMT = """
        INSERT INTO TIParticleWeapons
             (module_name, shot_power, efficiency,
             heat_fraction, xray_fraction, baryon_fraction,
             bombardment_value, cooldown, dispersion_model,
             lens_radius, range, doubling_range, pivot)
             VALUES 
             (:dataName, :shotPower_MJ, :efficiency,
             :heatFraction, :xRayFraction, :baryonFraction,
             :bombardmentValue, :cooldown_s, :dispersionModel,
             :lensRadius_cm, :targetingRange_km, :doublingRange_km,
             :pivotRange_deg);
        """

    __SHIP_ARMOR_MODULE_STMT = """
        INSERT INTO TIArmor
          (module_name, density, vaporization, 
          baryonic_rating, xray_rating)
          VALUES 
          (:dataName, :density_kgm3,
          :heatofVaporization_MJkg, 
          :baryonicHalfValue_cm,
          :xRayHalfValue_cm );
        """

    __SHIP_ARMOR_SPECIALTY_STMT = """
        INSERT INTO TIArmorSpecialization
             (module_name, specialization, value)
             VALUES 
             (:_dataName, :_spec, :_value);
        """

    __LOCALIZATION_TECHS_STMT = """
        INSERT INTO LocalizationTITechEntries
            (internal_name, language_code,
            display_name_text, summary_text, description_text,
            quote_text)
            VALUES 
            (:internal, :langCode, :display,
            :summary, :description, :quote);
    """

    __LOCALIZATION_MODULES_STMT = """
        INSERT INTO LocalizationTIShipModules
            (module_name, language_code,
            display_name_text, description_text)
            VALUES 
            (:module, :langCode, :display,
            :description);
    """

    #Shorter way to built the templates
    @staticmethod
    def __mkctx( ctx_type, insert_cb ):
        return {
            "type": ctx_type,
            "callback": insert_cb,
        }

    #Our templates, defined in constructor
    __template_context = None

    #Our database connection, which is updated on execution
    __database = None

    __logger = logging.getLogger('TerraInvictaDatabaseManager')


    def __new__( cls ):
        return super( TerraInvictaDatabaseManager, cls ).__new__( cls )

    def __init__(self):
        self.__template_context = {
            "TIBatteryTemplate": self.__mkctx("ship_module", self.__insert_battery_module),
            "TIDriveTemplate": self.__mkctx("ship_module", self.__insert_drive_module),
            "TIFactionTemplate": self.__mkctx("faction", self.__insert_faction),
            "TIGunTemplate": self.__mkctx("ship_module", self.__insert_conventional_gun_weapon_module),
            "TIHeatSinkTemplate": self.__mkctx("ship_module", self.__insert_heat_sink_module),
            "TILaserWeaponTemplate": self.__mkctx("ship_module", self.__insert_laser_weapon_module),
            "TIMagneticGunTemplate": self.__mkctx("ship_module", self.__insert_magnetic_gun_weapon_module),
            "TIMissileTemplate": self.__mkctx("ship_module", self.__insert_missile_weapon_module),
            "TIParticleWeaponTemplate": self.__mkctx("ship_module", self.__insert_particle_weapon_module),
            "TIPlasmaWeaponTemplate": self.__mkctx("ship_module", self.__insert_plasma_weapon_module),
            "TIPowerPlantTemplate": self.__mkctx("ship_module", self.__insert_power_plant_module),
            "TIProjectTemplate": self.__mkctx("tech", self.__insert_project_technology),
            "TIRadiatorTemplate": self.__mkctx("ship_module", self.__insert_radiator_module),
            "TIShipArmorTemplate": self.__mkctx("ship_module", self.__insert_armor_module),
            "TIShipHullTemplate": self.__mkctx("ship_module", self.__insert_hull_module),
            "TITechTemplate": self.__mkctx("tech", self.__insert_global_technology),
            "TIUtilityModuleTemplate": self.__mkctx("ship_module", self.__insert_utility_module),
        }



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

        if "weightedBuildMaterials" in contents:
            self.__insert_module_composition(contents)

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

    def __insert_module_composition(self, json_object):
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
        contents.update({key: json_object["weightedBuildMaterials"][key] for key in contents if (key in json_object["weightedBuildMaterials"] and
                    json_object["weightedBuildMaterials"][key] is not None)})

        cursor.execute(self.__SHIP_MODULE_MATERIALS_STMT, contents)
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

    def __insert_tech_localization(self, contents):
        cursor = self.__database.cursor()

        try:
            cursor.execute(self.__LOCALIZATION_TECHS_STMT, contents)
        except sqlite3.IntegrityError as e:
            self.__logger.warning(f"IntegrityError encountered for tech { contents["internal"] }, continuing")

        cursor.close()

    def __insert_module_localization(self, contents):
        cursor = self.__database.cursor()

        #Its fine for us to ignore foreign key integrity errors in localizations since
        #Pavonis includes some localization entries for techs which are not fully implemented in game
        #or were removed from the game (such as the resisto-jets and redundant drives)
        try:
            cursor.execute(self.__LOCALIZATION_MODULES_STMT, contents)
        except sqlite3.IntegrityError as e:
            self.__logger.warning(f"IntegrityError encountered for module { contents["module"] }, continuing")


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

    def __handle_template(self, entries, template_name):
        callback = self.__template_context[template_name]["callback"]
        self.__handle_json_contents(entries, template_name, callback )

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


    def __handle_tech_localizations(self, language_code, localization_table):
        tech_list = localization_table.keys()

        for tech_key in tech_list:

            #We try to filter out most of the invalid entries, with integrity error checking as a last resort

            # Skip deprecated entries
            if "deprecated" in tech_key.lower():
                continue

            loc_entry = localization_table[tech_key]

            # We must have at least a displayName in our entry
            if not "displayName" in loc_entry:
                continue


            packed = {
                "internal": tech_key,
                "langCode": language_code,
                "display": loc_entry.get("displayName",None),
                "summary": loc_entry.get("summary", None),
                "description": loc_entry.get("description", None),
                "quote": loc_entry.get("quote", None),
            }
            self.__insert_tech_localization(packed)

    def __handle_module_localizations(self, language_code, localization_table):
        module_list = localization_table.keys()

        for module_key in module_list:

            #Skip deprecated entries
            if "deprecated" in module_key.lower():
                continue

            loc_entry = localization_table[module_key]

            #We must have at least a displayName in our entry
            if not "displayName" in loc_entry:
                continue

            packed = {
                "module": module_key,
                "langCode": language_code,
                "display": loc_entry.get("displayName", None),
                "description": loc_entry.get("description", None),
            }
            self.__insert_module_localization(packed)

    def __infer_localization_origin(self, principle):
        return self.__template_context[principle]["type"]



    def __load_localization_file(self, path, destination: dict):
        loc_file = open(path, "r", encoding="utf-8")
        for line in loc_file:
            line = line.strip()

            # We need to ensure that the entry matches the expected pattern
            result = re.search(r"\w+\.((displayName)|(quote)|(summary)|(description))\.[\w-]+=.*", line)
            if not result:
                continue

            entry = line.split(".", 2)

            target, value = entry[-1].split("=", 1)
            #destination[target][entry[1]] = value
            if not target in destination:
                destination[target] = {}

            destination[target][entry[1]] = value
        loc_file.close()


    def __load_json_file(self, path, destination):
        file = open( path, "r", encoding="utf-8" )

        #we can infer the file via its name
        file_name = os.path.basename( file.name )
        template_name = file_name.replace(".json", "")
        json_body = self.__load_json(file)

        destination[template_name] = {
            "file" : file_name,
            "path" : path,
            "body" : json_body,
        }

    def __load_json_paths(self, path_list, destination):
        for path in path_list:
            if os.path.isfile(path) and path.endswith(".json"):
                self.__load_json_file(path, destination)
            else:
                raise ValueError(f"File {path} does not exist")

    def __populate_localization_single(self, localization_path):

        file = open(localization_path, "r")
        file_name = os.path.basename( file.name )
        template_name, language_code = file_name.split(".")

        cnc = dict()
        self.__load_localization_file(localization_path, cnc)

        inferred = self.__infer_localization_origin(template_name)
        if inferred == "ship_module":
            self.__handle_module_localizations(language_code, cnc)
        elif inferred == "tech":
            self.__handle_tech_localizations(language_code, cnc)
        else:
            raise ValueError

    def __populate_localizations(self, database_url, localization_path_list):

        for path in localization_path_list:
            if not os.path.isfile(path):
                raise ValueError(f"File {path} does not exist")

        try:
            self.__database = sqlite3.connect(database_url)
            self.__database.row_factory = sqlite3.Row
        except sqlite3.Error as e:
            raise IOError(f"Error while connecting to database: {e}", e)


        try:

            self.__database.execute(" PRAGMA foreign_keys = ON ")
            self.__database.execute(" BEGIN TRANSACTION")


            for path in localization_path_list:
                self.__populate_localization_single(path)

            self.__database.commit()
        except sqlite3.Error as e:
            self.__database.rollback()
            raise IOError(f"Error while updating database. Transaction rolled back:", e)
        except KeyError as e:
            self.__database.rollback()
            raise KeyError(f"Key not found, transaction rolled back:", e)
        except:
            self.__database.rollback()
            print(f"Unexpected error {sys.exc_info()[0]} , transaction rolled back:")
            raise
        finally:
            try:
                self.__database.close()
            except sqlite3.Error as e:
                _eg, exception, _tb = sys.exc_info()
                if exception is not None:
                    nex = copy.copy(e)
                    nex.__cause__ = exception

                    raise IOError(f"Error while closing database: {e}", nex)
                else:
                    raise IOError(f"Error while closing database. {e}", e)

    def __populate_db(self, database_url, path_list):
        entries = {}

        self.__load_json_paths(path_list, entries)

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

            #Insert the default project for modules with no requirements
            self.__database.execute("INSERT INTO `TITechEntries` values( 'Base', 'Base project for game start', false, 'none', 'none', 'none', 0 );")

            #Handle factions, global techs, then project techs, the order is important
            self.__handle_template(entries, "TIFactionTemplate")
            self.__handle_template(entries, "TITechTemplate")
            self.__handle_template(entries, "TIProjectTemplate")

            #We can now update the prerequisites for techs
            self.__handle_tech_prerequisites(entries)
            self.__handle_faction_requirements(entries)

            #Add modules, order isn't important here, once techs are inserted
            self.__handle_template(entries, "TIShipHullTemplate")
            self.__handle_template(entries, "TIPowerPlantTemplate")
            self.__handle_template(entries, "TIBatteryTemplate")
            self.__handle_template(entries, "TIHeatSinkTemplate")
            self.__handle_template(entries, "TIRadiatorTemplate")
            self.__handle_template(entries, "TIDriveTemplate")
            self.__handle_template(entries, "TIUtilityModuleTemplate")
            self.__handle_template(entries, "TIShipArmorTemplate")

            #Ballistic Weapons
            self.__handle_template(entries, "TIGunTemplate")
            self.__handle_template(entries, "TIMagneticGunTemplate")
            self.__handle_template(entries, "TIMissileTemplate")

            #Energy weapons
            self.__handle_template(entries, "TILaserWeaponTemplate")
            self.__handle_template(entries, "TIPlasmaWeaponTemplate")
            self.__handle_template(entries, "TIParticleWeaponTemplate")


            self.__database.execute("UPDATE TIDatabaseInfo set entry_value = 'true' where entry_name = 'db_populated';")

            self.__database.commit()
        except sqlite3.Error as e:
            self.__database.rollback()
            raise IOError(f"Error while updating database. Transaction rolled back:", e)
        except KeyError as e:
            self.__database.rollback()
            raise KeyError(f"Key not found, transaction rolled back:", e)
        except:
            self.__database.rollback()
            print(f"Unexpected error {sys.exc_info()[0]} , transaction rolled back:")
            raise
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


    def __wipe_db(self, database_url):

        try:
            self.__database = sqlite3.connect(database_url)
            self.__database.row_factory = sqlite3.Row
        except sqlite3.Error as e:
            raise IOError(f"Error while connecting to database: {e}", e)

        try:
            cursor = self.__database.cursor()

            cursor.execute(" PRAGMA foreign_keys = ON ")
            cursor.execute(" BEGIN TRANSACTION")

            #This should just wipe the whole database due to cascading rules
            cursor.execute( "DELETE FROM TITechEntries;" )
            cursor.execute( "DELETE FROM TIFactions;" )

            cursor.execute( "UPDATE TIDatabaseInfo SET entry_value = 'false' WHERE entry_name = 'db_populated';" )

            cursor.close()

            self.__database.commit()
        except sqlite3.Error as e:
            self.__database.rollback()
            raise IOError("Error while attempting to wipe database, transaction rolled back:", e)
        except:
            self.__database.rollback()
            print(f"Unexpected error {sys.exc_info()[0]} , transaction rolled back:")
            raise
        finally:
            try:
                self.__database.close()
            except sqlite3.Error as e:
                _eg, exception, _tb = sys.exc_info()
                if exception is not None:
                    nex = copy.copy( e )
                    nex.__cause__ = exception

                    raise IOError(f"Error while closing database:", nex)
                else:
                    raise IOError(f"Error while closing database:", e)

    #public interface

    def populate_db(self, database_url, path_list):
        self.__populate_db(database_url, path_list)

    def wipe_db(self, database_url):
        self.__wipe_db(database_url)

    def localize_db(self, database_url, loc_path_list):
        self.__populate_localizations(database_url, loc_path_list)

if __name__ == "__main__":
    dbhandler = TerraInvictaDatabaseManager()

    #delete the database every time
    if os.path.exists("../test_database.db"):
        os.remove("../test_database.db")

    script = open("../tidb.sql", "r").read()

    sqlite3.connect("../test_database.db").executescript(script).close()

    json_path_list = []
    for root, dirs, files in os.walk("../testfiles"):
        for name in files:
            json_path_list.append(os.path.abspath( os.path.join( root, name ) ))
        break


    localization_path_list = []
    for root, dirs, files in os.walk("../testfiles/localization"):
        for name in files:
            localization_path_list.append(os.path.abspath( os.path.join( root, name ) ))
        break


    dbhandler.populate_db( "../test_database.db", json_path_list )
    dbhandler.localize_db( "../test_database.db", localization_path_list )
