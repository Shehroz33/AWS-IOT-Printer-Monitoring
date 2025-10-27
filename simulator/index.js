// simulator/index.js
// Publishes fake printer telemetry to AWS IoT Core over MQTT (WebSockets + SigV4).

import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import dotenv from "dotenv";
import { mqtt, iot } from "aws-iot-device-sdk-v2";

import { SignatureV4 } from "@aws-sdk/signature-v4";
import { defaultProvider } from "@aws-sdk/credential-provider-node";
import { Sha256 } from "@aws-crypto/sha256-js";
import { HttpRequest } from "@aws-sdk/protocol-http";

// ---------- load .env from REPO ROOT ----------
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
dotenv.config({ path: path.resolve(__dirname, "../.env") });

// ---------- env ----------
const region = process.env.AWS_REGION || "us-east-1";
const IOT_ENDPOINT = process.env.IOT_ENDPOINT; // like a1b2c3-ats.iot.us-east-1.amazonaws.com
const IOT_TOPIC = process.env.IOT_TOPIC || "printers/telemetry";
const AWS_IOT_IDENTITY = process.env.AWS_IOT_IDENTITY || "sim-printer-01";

if (!IOT_ENDPOINT) {
  console.error("❌ Missing IOT_ENDPOINT in .env at repo root");
  process.exit(1);
}

// ---------- Build a SigV4 handshake transformer ----------
function websocketSigV4Transform(endpointHost, awsRegion) {
  return async (req, done) => {
    try {
      const signer = new SignatureV4({
        service: "iotdevicegateway",
        region: awsRegion,
        credentials: defaultProvider(),
        sha256: Sha256,
      });

      const requestToSign = new HttpRequest({
        protocol: "wss:",
        method: "GET",
        headers: req.headers, // sdk provides host header etc.
        hostname: endpointHost,
        path: req.path,
        query: req.query,
      });

      const signed = await signer.sign(requestToSign);
      // Apply the signed headers back to the request the CRT will send
      req.headers = signed.headers;
      done();
    } catch (err) {
      done(err);
    }
  };
}

// ---------- mqtt client (WebSockets + SigV4) ----------
const configBuilder = iot.AwsIotMqttConnectionConfigBuilder.new_with_websockets();
configBuilder.with_clean_session(true);
configBuilder.with_client_id(`${AWS_IOT_IDENTITY}-${Date.now()}`);
configBuilder.with_endpoint(IOT_ENDPOINT);
configBuilder.with_keep_alive_seconds(30);
configBuilder.with_websocket_handshake_transform(
  websocketSigV4Transform(IOT_ENDPOINT, region)
);

const client = new mqtt.MqttClient();
const connection = client.new_connection(configBuilder.build());

// ---------- load base payload ----------
const dataFile = path.resolve(__dirname, "./printer_iot_data.json");
const base = JSON.parse(fs.readFileSync(dataFile, "utf8"));

function mutate(prev) {
  return {
    ...prev,
    metrics: {
      ...prev.metrics,
      jobsPrinted: prev.metrics.jobsPrinted + (Math.random() > 0.6 ? 1 : 0),
      tempC: 35 + Math.floor(Math.random() * 15),
      errors: Math.random() > 0.95 ? 1 : 0,
    },
    ts: new Date().toISOString(),
  };
}

async function main() {
  try {
    await connection.connect();
    console.log("✅ Connected to AWS IoT Core:", IOT_ENDPOINT);
    console.log("➡️  Publishing to topic:", IOT_TOPIC);

    let current = { ...base, ts: new Date().toISOString() };

    setInterval(async () => {
      try {
        current = mutate(current);
        const msg = JSON.stringify(current);
        await connection.publish(IOT_TOPIC, msg, mqtt.QoS.AtLeastOnce);
        console.log("📨 Published:", msg);
      } catch (e) {
        console.error("Publish error:", e?.message || e);
      }
    }, 3000);
  } catch (err) {
    console.error("Connection error:", err?.message || err);
    process.exit(1);
  }
}

main();
