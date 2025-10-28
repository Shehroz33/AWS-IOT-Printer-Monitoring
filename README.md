# AWS IoT Printer Monitoring

![CI](https://github.com/Shehroz33/AWS-IOT-Printer-Monitoring/actions/workflows/ci.yml/badge.svg)


Real-time **IoT printer monitoring** on AWS using **IoT Core → Lambda → DynamoDB → (optional) API → React Dashboard**.  
Includes environment templates and CI workflow to make the repo look production-ready.

---

## ✨ Features
- Realtime telemetry (MQTT topic: `printers/telemetry`)
- Ingestion via **AWS Lambda** (validate → store)
- Storage in **DynamoDB** (`printer_metrics`)
- (Optional) **API Gateway** for read endpoints
- **React dashboard** to visualize metrics
- GitHub Actions **CI** (installs & builds)

---


## Architecture

![1737527088748](https://github.com/user-attachments/assets/7e28ca09-0bf2-44e0-bd0c-4b4a1fd89e51)


## 📸 Screenshots

**IoT Connection**
![Connection Success](./docs/IOTConnection.png)




**AWS CloudFormation**
![Cloud Formation](./docs/CLOUD-FORMATION.png)




**DynamoDB**
![DynamoDB](./docs/DynamoDB.png)