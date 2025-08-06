# README: Source_Data Folder

## Purpose
This folder contains raw and authoritative GIS data used across Big Sky Ag projects, such as:

- County Assessor Parcel boundaries
- USDA CDL raster data
- Shapefiles and GeoJSON for zoning, land use, or field boundaries
- Basemap layers and reference rasters
- Clipped datasets used for QGIS and Pix4D processing

## Folder Contents

### Typical File Types:
- `.shp`, `.dbf`, `.shx`, `.prj`: ESRI shapefiles
- `.geojson`, `.kml`: boundary and zoning data
- `.tif`: raster datasets (e.g., CDL 2024 imagery)
- `.qgz`, `.qmd`: QGIS project or style templates

### Current Data:
- **CDL_2024_06029.tif / CDL_2024_06107.tif** – Cropland Data Layer for Kern and nearby counties
- **Assessor_Parcels_Land_2025.shp** – Kern County land parcel shapefile
- **Kern_County_Zoning.shp** – Zoning shapefile from local GIS department
- **BigSky_HQ.shp** – Drone base HQ boundary
- **TargetFarms_40to150ac** – Priority scouting zone for 2025 outreach
- **tl_2023_06_place / tl_2024_us_county** – TIGER/Line census base layers

## Usage Guidelines
- Do not overwrite source files — duplicate if modifying
- Always cite the data source (e.g., USDA, county GIS)
- Use this folder as the foundation for all project-specific clipping, analysis, and reports

## Notes
- Keep this folder clean — no project exports or temporary analysis files
- Archive legacy or unused layers in `Z_Archive/` if no longer needed

---

_Last updated: 2025-07-30_
