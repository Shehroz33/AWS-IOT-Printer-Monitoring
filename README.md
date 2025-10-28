# AWS IoT Printer Monitoring

# AWS IoT Printer Monitoring

Real-time **IoT printer monitoring** on AWS using **IoT Core → Lambda → DynamoDB → (optional) API → React Dashboard**.  
Includes environment templates and CI workflow to make the repo look production-ready.

> Inspired by the instructor repo. This is my **documented, refactored** version with a clearer structure and README.

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

![AWS IoT architecture diagram showing printer device connecting through IoT Core to Lambda, DynamoDB, and React dashboard](https://github.com/user-attachments/assets/7e28ca09-0bf2-44e0-bd0c-4b4a1fd89e51)

---

## 🗺️ Architecture (High Level)

```mermaid
flowchart LR
  A[Printer Device / Simulator] --> B((AWS IoT Core MQTT))
  B --> C[AWS IoT Rule]
  C --> D[Lambda Function - Ingest & Validate]
  D --> E[(DynamoDB Table: printer_metrics)]
  E --> F[API Gateway (optional)]
  F --> G[React Dashboard]
  D --> H[CloudWatch Logs / Alarms]
```

## 📸 Screenshots
### IoT Connection 
![Line graph showing successful IoT connections over time, with metrics ranging from 0 to 3 connections on Y-axis and time in hours on X-axis](./docs/IOTConnection.png)

### AWS CloudFormation
![AWS CloudFormation stack details showing resource creation status and deployment progress](./docs/CLOUD-FORMATION.png)

### DynamoDB
![DynamoDB table interface displaying printer metrics data with timestamp and telemetry information](./docs/DynamoDB.png)