PRAGMA foreign_keys;
PRAGMA foreign_keys = ON;


CREATE TABLE `TITechEntries` (
  `internal_name` TEXT UNIQUE PRIMARY KEY,
  `friendly_name` TEXT NOT NULL,
  `ai_critical` BOOLEAN NOT NULL,
  `tech_type` TEXT NOT NULL,
  `category` TEXT NOT NULL,
  `role` TEXT NOT NULL,
  `cost` INTEGER NOT NULL
  
);

CREATE TABLE `TIPrerequisites` (
  `internal_name` TEXT NOT NULL,
  `requires` TEXT NOT NULL,
  PRIMARY KEY (`internal_name`, `requires`),
  
  FOREIGN KEY (`internal_name`) REFERENCES `TITechEntries` (`internal_name`) ON DELETE CASCADE,
  FOREIGN KEY (`requires`) REFERENCES `TITechEntries` (`internal_name`) ON DELETE CASCADE

);

CREATE TABLE `TIFactionPrerequisites` (
  `internal_name` TEXT NOT NULL,
  `faction` TEXT NOT NULL,
  PRIMARY KEY (`internal_name`, `faction`),
  
  FOREIGN KEY (`internal_name`) REFERENCES `TITechEntries` (`internal_name`) ON DELETE CASCADE,
  FOREIGN KEY (`faction`) REFERENCES `TIFactions` (`faction_internal`) ON DELETE CASCADE
);

CREATE TABLE `TIFactions` (
  `faction_internal` TEXT UNIQUE PRIMARY KEY,
  `faction_common` TEXT NOT NULL
);

CREATE TABLE `TIGlobalTechnologies` (
  `internal_name` TEXT UNIQUE PRIMARY KEY,
  `end_game_tech` BOOLEAN NOT NULL,

  FOREIGN KEY (`internal_name`) REFERENCES `TITechEntries` (`internal_name`) ON DELETE CASCADE
);

CREATE TABLE `TIProjects` (
  `internal_name` TEXT UNIQUE PRIMARY KEY,
  `globally_shared` BOOLEAN NOT NULL,
  `repeatable` BOOLEAN NOT NULL,


  FOREIGN KEY (`internal_name`) REFERENCES `TITechEntries` (`internal_name`) ON DELETE CASCADE
);

CREATE TABLE `TIShipModules` (
  `module_name` TEXT UNIQUE PRIMARY KEY,
  `friendly_name` TEXT NOT NULL,
  `required_project` TEXT NOT NULL,
  `module_type` TEXT NOT NULL CHECK (`module_type` IN ('hull', 'drive', 'nose_weapon', 'hull_weapon', 'heat_sink', 'power_plant', 'radiator', 'battery', 'utility', 'armor')),
  FOREIGN KEY (`required_project`) REFERENCES `TITechEntries` (`internal_name`) ON DELETE CASCADE
);

CREATE TABLE `TIModuleMaterials` (
    'module_name' TEXT UNIQUE PRIMARY KEY,
    `water` STRING NOT NULL,
    `volatiles` STRING NOT NULL,
    `metals` STRING NOT NULL,
    `nobleMetals` STRING NOT NULL,
    `fissiles` STRING NOT NULL,
    `exotics` STRING NOT NULL,
    `antimatter` STRING NOT NULL,

    FOREIGN KEY (`module_name`) REFERENCES `TIShipModules` (`module_name`) ON DELETE CASCADE
);


CREATE TABLE `TIShipHulls` (
  `module_name` TEXT UNIQUE PRIMARY KEY,
  `alien_only` BOOLEAN NOT NULL,
  `construction_tier` INTEGER NOT NULL,
  `construction_time` INTEGER NOT NULL,
  `maximum_officers` INTEGER NOT NULL,
  `starting_crew` INTEGER NOT NULL,
  `mission_control` INTEGER NOT NULL,
  `monthly_cost` INTEGER NOT NULL,
  `base_mass` INTEGER NOT NULL,
  `length` INTEGER NOT NULL,
  `width` INTEGER NOT NULL,
  `volume` INTEGER NOT NULL,
  `structural_integrity` INTEGER NOT NULL,
  `thruster_multiplier` INTEGER NOT NULL,
  `nose_hardpoints` INTEGER NOT NULL,
  `hull_hardpoints` INTEGER NOT NULL,
  `max_modules` INTEGER NOT NULL,
  
   FOREIGN KEY (`module_name`) REFERENCES `TIShipModules` (`module_name`) ON DELETE CASCADE
);

CREATE TABLE `TIArmor` (
  `module_name` TEXT UNIQUE PRIMARY KEY,
  `density` INTEGER NOT NULL,
  `vaporization` STRING NOT NULL,
  `baryonic_rating` STRING NOT NULL,
  `xray_rating` STRING NOT NULL,

  FOREIGN KEY (`module_name`) REFERENCES `TIShipModules` (`module_name`) ON DELETE CASCADE
);

CREATE TABLE `TIArmorSpecialization` (
  `module_name` TEXT NOT NULL,
  `specialization` TEXT NOT NULL,
  `value` STRING not null,

  PRIMARY KEY (`module_name`, `specialization`),
  FOREIGN KEY (`module_name`) REFERENCES `TIArmor`(`module_name`) ON DELETE CASCADE
);

CREATE TABLE `TIPowerPlants` (
  `module_name` TEXT UNIQUE PRIMARY KEY,
  `plant_class` TEXT NOT NULL,
  `max_power` STRING NOT NULL,
  `specific_power` STRING NOT NULL,
  `general_use` BOOLEAN NOT NULL,
  `efficiency` STRING NOT NULL,
  `crew_needed` INTEGER NOT NULL,
  
  FOREIGN KEY (`module_name`) REFERENCES `TIShipModules` (`module_name`) ON DELETE CASCADE
);

CREATE TABLE `TIDrives` (
  `module_name` TEXT UNIQUE PRIMARY KEY,
  `common_drive_name` TEXT NOT NULL,
  `thruster_count` INTEGER NOT NULL,
  `drive_class` TEXT NOT NULL,
  `power_plant_class` TEXT NOT NULL,
  `thrust` INTEGER NOT NULL,
  `exhaust_velocity` STRING NOT NULL,
  `efficiency` STRING NOT NULL,
  `power_needed` STRING NOT NULL,
  `rating` STRING NOT NULL,
  `flat_mass` INTEGER NOT NULL,
  `cooling_cycle` TEXT NOT NULL,
  `combat_cap` INTEGER NOT NULL,

   FOREIGN KEY (`module_name`) REFERENCES `TIShipModules` (`module_name`) ON DELETE CASCADE
);

CREATE TABLE `TIDrivePropellant` (
  `module_name` TEXT UNIQUE PRIMARY KEY,
  `uses_helium3` BOOLEAN NOT NULL,
  `propellant` TEXT NOT NULL,
  `water` STRING NOT NULL,
  `volatiles` STRING NOT NULL,
  `metals` STRING NOT NULL,
  `nobleMetals` STRING NOT NULL,
  `fissiles` STRING NOT NULL,
  `exotics` STRING NOT NULL,
  `antimatter` STRING NOT NULL,

   FOREIGN KEY (`module_name`) references `TIDrives` (`module_name`) ON DELETE CASCADE
);

CREATE TABLE `TIRadiators` (
  `module_name` TEXT UNIQUE PRIMARY KEY,
  `specific_mass` STRING NOT NULL,
  `specific_power` STRING NOT NULL,
  `operating_temperature` INTEGER NOT NULL,
  `emissivity` STRING NOT NULL,
  `vulnerability` INTEGER NOT NULL,
  `crew_needed` INTEGER NOT NULL,
  `radiator_type` TEXT NOT NULL,
  `collector` BOOLEAN NOT NULL,
  
  FOREIGN KEY (`module_name`) REFERENCES `TIShipModules` (`module_name`) ON DELETE CASCADE
);

CREATE TABLE `TIBatteries` (
  `module_name` TEXT UNIQUE PRIMARY KEY,
  `capacity` STRING NOT NULL,
  `recharge_rate` STRING NOT NULL,
  `mass` INTEGER NOT NULL,
  `crew_needed` INTEGER NOT NULL,
  `hit_points` INTEGER NOT NULL,
  
  FOREIGN KEY (`module_name`) REFERENCES `TIShipModules` (`module_name`) ON DELETE CASCADE
);

CREATE TABLE `TIHeatSinks` (
  `module_name` TEXT UNIQUE PRIMARY KEY,
  `capacity` INTEGER NOT NULL,
  `mass` INTEGER NOT NULL,
  `crew_needed` INTEGER NOT NULL,
  
  FOREIGN KEY (`module_name`) REFERENCES `TIShipModules` (`module_name`) ON DELETE CASCADE
);

CREATE TABLE `TIUtilities` (
  `module_name` TEXT UNIQUE PRIMARY KEY,
  `no_combat_repair` BOOLEAN NOT NULL,
  `power_requirement` INTEGER NOT NULL,

  FOREIGN KEY (`module_name`) REFERENCES `TIShipModules` (`module_name`) ON DELETE CASCADE
);

CREATE TABLE `TIUtilityEffects` (
  `module_name` TEXT,
  `rule` TEXT,
  PRIMARY KEY (`module_name`, `rule`),
  
  FOREIGN KEY (`module_name`) REFERENCES `TIUtilities` (`module_name`) ON DELETE CASCADE
);

CREATE TABLE `TIWeapons` (
  `module_name` TEXT UNIQUE PRIMARY KEY,
  `module_mass` INTEGER NOT NULL,
  `mount_type` TEXT NOT NULL,
  `can_attack` BOOLEAN NOT NULL,
  `can_defend` BOOLEAN NOT NULL,
  `crew_needed` INTEGER NOT NULL,

  FOREIGN KEY (`module_name`) REFERENCES `TIShipModules` (`module_name`) ON DELETE CASCADE
);

CREATE TABLE `TIMissiles` (
  `module_name` TEXT UNIQUE PRIMARY KEY,
  `thrust` INTEGER NOT NULL,
  `warhead_class` TEXT NOT NULL,
  `exhaust_velocity` STRING NOT NULL,
  `acceleration` STRING NOT NULL,
  `delta_v` STRING NOT NULL,
  `magazine` INTEGER NOT NULL,
  `flat_damage` INTEGER,
  `bombardment_value` INTEGER NOT NULL,
  `chipping` STRING NOT NULL,
  `targetable` BOOLEAN NOT NULL,
  `range` INTEGER NOT NULL,
  `cone_angle` STRING,
  `ammo_mass` STRING NOT NULL,
  `fuel_mass` STRING NOT NULL,
  `system_mass` STRING NOT NULL,
  `warhead_mass` STRING NOT NULL,
  `thrust_ramp` INTEGER NOT NULL,
  `turn_ramp` INTEGER NOT NULL,
  `maneuver_angle` INTEGER NOT NULL,
  `rotation` INTEGER NOT NULL,
  `pivot_range` INTEGER NOT NULL,
  
  FOREIGN KEY (`module_name`) REFERENCES `TIWeapons` (`module_name`) ON DELETE CASCADE
);

CREATE TABLE `TILasers` (
  `module_name` TEXT UNIQUE PRIMARY KEY,
  `wavelength` INTEGER NOT NULL,
  `mirror_radius` INTEGER NOT NULL,
  `beam_quality` STRING NOT NULL,
  `jitter_radius` TEXT NOT NULL,
  `shot_power` STRING NOT NULL,
  `efficiency` STRING NOT NULL,
  `cooldown` STRING NOT NULL,
  `bombardment_value` INTEGER NOT NULL,
  `range` INTEGER NOT NULL,
  `pivot` INTEGER NOT NULL,
  `hit_points` INTEGER NOT NULL,
  
   FOREIGN KEY (`module_name`) REFERENCES `TIWeapons` (`module_name`) ON DELETE CASCADE
);

CREATE TABLE `TIMagneticGuns` (
  `module_name` TEXT UNIQUE PRIMARY KEY,
  `magazine` INTEGER NOT NULL,
  `muzzle_velocity` STRING NOT NULL,
  `efficiency` STRING NOT NULL,
  `chipping` STRING NOT NULL,
  `ammo_mass` STRING NOT NULL,
  `warhead_mass` STRING NOT NULL,
  `targetable` BOOLEAN NOT NULL,
  `bombardment_value` INTEGER NOT NULL,
  `range` INTEGER NOT NULL,
  `pivot` INTEGER NOT NULL,
  `cooldown` STRING NOT NULL,
  `salvo_count` INTEGER,
  `salvo_cooldown` STRING,
  
  FOREIGN KEY (`module_name`) REFERENCES `TIWeapons` (`module_name`) ON DELETE CASCADE
);

CREATE TABLE `TIConventionalGuns` (
  `module_name` TEXT UNIQUE PRIMARY KEY,
  `magazine` INTEGER NOT NULL,
  `muzzle_velocity` STRING NOT NULL,
  `efficiency` STRING NOT NULL,
  `chipping` STRING NOT NULL,
  `ammo_mass` STRING NOT NULL,
  `warhead_mass` STRING NOT NULL,
  `bombardment_value` INTEGER NOT NULL,
  `range` INTEGER NOT NULL,
  `pivot` INTEGER NOT NULL,
  `targetable` BOOLEAN NOT NULL,
  `cooldown` STRING NOT NULL,
  `salvo_count` STRING NOT NULL,
  `salvo_cooldown` STRING NOT NULL,
  
  FOREIGN KEY (`module_name`) REFERENCES `TIWeapons` (`module_name`) ON DELETE CASCADE
);

CREATE TABLE `TIPlasmaWeapons` (
  `module_name` TEXT UNIQUE PRIMARY KEY,
  `magazine` INTEGER NOT NULL,
  `charging_energy` STRING NOT NULL,
  `muzzle_velocity` STRING NOT NULL,
  `warhead_mass` STRING NOT NULL,
  `efficiency` STRING NOT NULL,
  `chipping` STRING NOT NULL,
  `cooldown` STRING NOT NULL,
  `bombardment_value` STRING NOT NULL,
  `targetable` BOOLEAN NOT NULL,
  `range` INTEGER NOT NULL,
  `pivot` INTEGER NOT NULL,
  
  FOREIGN KEY (`module_name`) REFERENCES `TIWeapons` (`module_name`) ON DELETE CASCADE
);

CREATE TABLE `TIParticleWeapons` (
  `module_name` TEXT UNIQUE PRIMARY KEY,
  `shot_power` STRING NOT NULL,
  `efficiency` STRING NOT NULL,
  `heat_fraction` STRING NOT NULL,
  `xray_fraction` STRING NOT NULL,
  `baryon_fraction` STRING NOT NULL,
  `bombardment_value` STRING NOT NULL,
  `cooldown` STRING NOT NULL,
  `dispersion_model` TEXT NOT NULL,
  `lens_radius` STRING NOT NULL,
  `range` INTEGER NOT NULL,
  `doubling_range` INTEGER,
  `emittance_mrad` STRING,
  `pivot` INTEGER NOT NULL,
  
  FOREIGN KEY (`module_name`) REFERENCES `TIWeapons` (`module_name`) ON DELETE CASCADE
);

CREATE TABLE `TIDatabaseInfo` (
    `entry_name` TEXT UNIQUE PRIMARY KEY,
    `entry_value` TEXT
);

INSERT INTO `TIDatabaseInfo` values('db_version', '0.1');
INSERT INTO `TIDatabaseInfo` values('db_populated', 'false');

--UPDATE TIDatabaseInfo set entry_value = 'true' where entry_name = 'db_populated';


