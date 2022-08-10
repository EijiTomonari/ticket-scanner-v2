# Ticket Scanner V2

### Flask Application with OpenCV to scan tickets in a local restaurant

## Routes

### Settings

- **/settings/read** - Returns a JSON with all settings
- **/settings/write** - Updates a setting in the database. Accepts a POST request with {name:string,value:number} body format

### Calibration

- **/calibration/omr/feed** - Returns live feed from OMR camera
- **/calibration/barcodes/feed** - Returns live feed from Barcodes camera

### Operations

- **/omr/scan** - Perform OMR on ticket
- **/barcodes/scan** - Perform barcodes scan on ticket
