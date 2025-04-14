# Waste management / monitor platform
Waste management is a critical challenge for modern cities, as the growing urban population and increasing waste generation demand more efficient and sustainable solutions. Traditional waste collection relies on predetermined routes, which often leads to resource waste, increased emissions, and delays in emptying full bins.

Smart waste bin management is an innovative approach that utilizes sensors, communication networks, and advanced software to optimize waste collection. Through this technology, sanitation services can receive real-time information about the status of bins and adjust garbage truck routes accordingly, reducing operational costs and environmental impact.

<img width="800" alt="image" src="https://github.com/user-attachments/assets/47dcacf0-4100-4416-b622-f49e2837935e" />

### Management Platform

The management platform forms the core of the smart waste bin management system and is responsible for the collection, storage, processing, and visualization of sensor data. The architecture of the platform is based on three main pillars:
* The LoRaWAN network via The Things Network (TTN)
* Data storage and processing through a Python script using Flask
* Data management and visualization through the TagoIO platform

### Platform Architecture
The system relies on the use of LoRaWAN for communication between the sensors and the platform. The data flow follows these stages:

### Data Collection from Sensors
The sensors installed in the bins collect various types of data, such as:
* Volatile Organic Compounds (VOC) – Measurement of gases related to air pollution
* Equivalent CO2 (CO2_eq) – Estimation of carbon dioxide concentration
* Movement detection (movement_detected) – Detection of bin movement (e.g., theft or tipping)
* Battery level (battery) – Monitoring of remaining energy
* Distance from waste to sensor (distance) – Used to estimate the bin’s fill level
* Geographical location (latitude, longitude) – GPS data for the bin’s location (optional)

The data is transmitted via LoRaWAN to a local gateway, which communicates with The Things Network (TTN).

### Data Transmission via The Things Network (TTN)
* TTN acts as an intermediate network layer, receiving data from the sensors and routing it to the central platform.
* The data is transmitted in JSON format, and there is the capability to apply filters and conversions using TTN payload formatters.
* The TTN Application Server is responsible for forwarding the data to the next layer.

### Data Forwarding and Processing via Flask API & Cloudflare
A Python script, based on the Flask framework, functions as a web API that receives data from TTN and forwards it to the TagoIO platform.
The Flask API handles:
* Receiving data from TTN via HTTP Webhooks
* Processing the data (parsing JSON, converting measurement units)
* Sending the data to the TagoIO platform via REST API
  
<img width="600" alt="image" src="https://github.com/user-attachments/assets/3e5e8a83-75eb-4c83-9b4a-d84b37745b1e" />


The application runs on a server and is exposed to the internet via Cloudflare, offering:
* Security through DDoS protection and SSL encryption
* Improved performance via caching and edge servers
* High availability through Cloudflare tunneling and load balancing

<img width="750" alt="image" src="https://github.com/user-attachments/assets/5427ad57-f819-4f84-be27-5e945f50c845" />


* Processing of data and conversion into the appropriate format
* Sending data to the TagoIO platform every 2 minutes
* Sending alerts when measurements exceed predefined thresholds for critical parameters
* Data Storage & Export: Storage of data with the ability to export in CSV/JSON formaτ

### Data Visualization and Management via TagoIO
* TagoIO serves as the central management platform and provides a set of dashboards that allow users to view and analyze the data.
* The platform's core functionalities include:

* Real-time dashboards: Visualization of data through charts, maps, and lists
* Live map showing the location of each bin
* Graphs showing fluctuations in VOC and CO2 concentrations
* Alerts for full bins, motion detection, or low battery levels
* Data export for further analysis

<img width="900" alt="image" src="https://github.com/user-attachments/assets/d3113c17-4198-4d9d-bac3-2c22b5c0863e" />


