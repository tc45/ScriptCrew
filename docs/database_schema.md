# VAR AI Database Schema

This document contains the database schema for the VAR AI project in Mermaid format.

```mermaid
erDiagram
    User ||--o{ Client : creates
    User ||--o{ Project : creates
    User ||--o{ Device : creates
    User ||--o{ Interface : creates
    User ||--o{ VRF : creates
    User ||--o{ ACL : creates
    User ||--o{ RouteTable : creates
    User ||--o{ InventoryItem : creates
    User ||--o{ Report : creates

    Client ||--o{ Project : has
    Client {
        int id PK
        string name
        string industry
        string primary_contact_name
        string primary_contact_email
        string primary_contact_phone
        string secondary_contact_name
        string secondary_contact_email
        string secondary_contact_phone
        string website
        text notes
        datetime created_at
        datetime updated_at
        int created_by FK
    }

    Project ||--o{ Device : has
    Project ||--o{ DeviceFile : has
    Project ||--o{ Report : has
    Project {
        int id PK
        int client_id FK
        string name
        text intent
        string status
        date start_date
        date end_date
        boolean is_split_off
        int parent_project_id FK
        text notes
        datetime created_at
        datetime updated_at
        int created_by FK
    }

    DeviceType ||--o{ Device : categorizes
    DeviceType ||--o{ DeviceFile : categorizes
    DeviceType {
        int id PK
        string name
        string slug
        text description
        datetime created_at
        datetime updated_at
    }

    Device ||--o{ Interface : has
    Device ||--o{ VRF : has
    Device ||--o{ ACL : has
    Device ||--o{ RouteTable : has
    Device ||--o{ InventoryItem : has
    Device {
        int id PK
        int project_id FK
        string name
        int device_type_id FK
        string model
        string firmware_version
        string serial_number
        string management_ip
        int interface_count
        int route_count
        int acl_count
        int sfp_count
        int ipsec_tunnel_count
        json routing_protocols
        datetime last_config_snapshot
        text notes
        datetime created_at
        datetime updated_at
        int created_by FK
    }

    Interface {
        int id PK
        int device_id FK
        string name
        string description
        string ip_address
        string subnet_mask
        string mac_address
        boolean is_up
        boolean is_enabled
        int speed
        int mtu
        datetime created_at
        datetime updated_at
        int created_by FK
    }

    VRF ||--o{ RouteTable : has
    VRF {
        int id PK
        int device_id FK
        string name
        string description
        string route_distinguisher
        datetime created_at
        datetime updated_at
        int created_by FK
    }

    ACL {
        int id PK
        int device_id FK
        string name
        string type
        json rules
        datetime created_at
        datetime updated_at
        int created_by FK
    }

    RouteTable {
        int id PK
        int device_id FK
        int vrf_id FK
        json routes
        datetime created_at
        datetime updated_at
        int created_by FK
    }

    InventoryItem {
        int id PK
        int device_id FK
        string item_type
        string name
        text description
        json data
        boolean is_active
        datetime last_seen
        datetime created_at
        datetime updated_at
        int created_by FK
    }

    DeviceFile {
        int id PK
        int project_id FK
        int device_type_id FK
        string file
        string name
        boolean parsed
        text parse_errors
        text notes
        datetime created_at
        datetime updated_at
    }

    ReportType ||--o{ Report : categorizes
    ReportType {
        int id PK
        string name
        string slug
        text description
        datetime created_at
        datetime updated_at
    }

    Report {
        uuid id PK
        int project_id FK
        int report_type_id FK
        string name
        text description
        json parameters
        string file
        string status
        text error_message
        datetime created_at
        datetime updated_at
        int created_by FK
    }
```

## Schema Description

The database schema represents a network device inventory and reporting system with the following key components:

1. **Client Management**
   - Clients can have multiple projects
   - Each client has contact information and metadata

2. **Project Management**
   - Projects belong to clients
   - Projects can have parent-child relationships
   - Projects contain devices and reports

3. **Device Management**
   - Devices belong to projects
   - Devices have multiple components (interfaces, VRFs, ACLs, etc.)
   - Devices are categorized by device types

4. **Configuration Management**
   - Device configurations are stored as files
   - Configurations are parsed and stored in structured format
   - Inventory items track device components

5. **Reporting System**
   - Reports are generated for projects
   - Reports are categorized by report types
   - Reports track their generation status and parameters

6. **User Integration**
   - All major entities track their creator
   - Audit fields (created_at, updated_at) are present on all models

## Key Relationships

- A Client can have multiple Projects
- A Project can have multiple Devices and Reports
- A Device can have multiple Interfaces, VRFs, ACLs, and Inventory Items
- A VRF can have multiple Route Tables
- All entities are linked to Users for tracking creation
- Device Types categorize both Devices and Device Files
- Report Types categorize Reports 