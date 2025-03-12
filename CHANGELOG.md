# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

## [1.0.0] - 2023-11-24

### Fixed
- Fixed critical issue with device-related entities (interfaces, VRFs, ACLs, route tables) not being persisted to the database
- Added explicit transaction handling with `connection.commit()` calls for all entity creation
- Resolved database synchronization issues by updating transaction handling methodology

### Added
- Created new diagnostic script `debug_devices.py` to analyze device creation issues
- Created new `create_minimal_data.py` script for testing entity relationships with minimal data
- Added more detailed logging throughout data generation process
- Enhanced verification steps to confirm entity creation in database

### Changed
- Updated `generate_dummy_data.py` to use explicit `objects.create()` followed by `save()` instead of `get_or_create()`
- Modified transaction handling to commit after each batch of related entities
- Restructured entity creation to ensure proper relationships between parent and child objects
- Improved error handling and reporting during data generation
- Reduced maximum entity counts to prevent excessive database load

### Technical Details
- Root cause: Entities created with `get_or_create()` weren't being properly committed to the database
- Solution: Implemented explicit transaction handling with `connection.commit()` after creating related entities
- Validation: Successfully created and verified all entity types (devices, interfaces, VRFs, ACLs, route tables)
- Database integrity: Ensured proper relationships between entities to maintain referential integrity

## [0.9.0] - 2023-11-20

### Added
- Initial database utilities implementation
- Created data generation utilities in `utils/database/` directory
- Added scripts for generating and cleaning up dummy data 