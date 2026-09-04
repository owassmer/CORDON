# Puglia orthophoto ImageServers

Source: `https://webapps.sit.puglia.it/arcgis/rest/services/BaseMaps`

Export Image works from this machine (HTTP 200, georeferenced PNG). Pattern:

`https://webapps.sit.puglia.it/arcgis/rest/services/BaseMaps/<NAME>/ImageServer/exportImage?bbox=<xmin>,<ymin>,<xmax>,<ymax>&bboxSR=32633&imageSR=32633&size=<w>,<h>&format=png&f=image`

CRS: EPSG:32633.

| Layer | Pixel size | Bands | Notes |
|---|---:|---:|---|
| Ortofoto1997 | — | — | present |
| Ortofoto2006 | — | — | present |
| Ortofoto2010 | — | — | present |
| Ortofoto2011 | — | — | present |
| Ortofoto2013 | — | — | present |
| Ortofoto2015 | — | 3 | RGB service |
| Ortofoto2015_IR | 0.15 m | 3 U8 | Color-infrared. Chip at 710000,4510000: vegetation magenta, soil cyan. Not calibrated reflectance |
| Ortofoto2016 | — | — | present |
| Ortofoto2019 | — | 3 | RGB |
| Ortofoto2022 | 0.20 m | 3 U8 | RGB |
| Ortofoto2023 | 0.20 m | 3 U8 | RGB |

Use 2015_IR / 2019 / 2022 / 2023 for crown and soil fraction. Do not treat 2015_IR as NDMI.
