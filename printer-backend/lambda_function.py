import boto3
import json
from decimal import Decimal

dynamodb = boto3.resource("dynamodb")
client = boto3.client("iot-data")
table = dynamodb.Table('PrinterProfiles')

def lambda_handler(event, context):
    # If called by API Gateway (GET /printers), just return all devices
    if event.get("httpMethod") == "GET":
        return get_printers()

    # Otherwise, assume IoT payload
    device_id = event.get("PrinterId")
    if device_id:
        device_id = device_id.capitalize()
    else:
        return response_json({"error": "Missing PrinterId"}, 400)

    sensor_value = event["data"]["value"]

    # Fetch device profile
    response = table.get_item(Key={"PrinterId": device_id})
    if "Item" in response:
        device_profile = response["Item"]
        lower_threshold = float(device_profile["Thresholds"]["Lower"])
        upper_threshold = float(device_profile["Thresholds"]["Upper"])
        time_window = int(device_profile["Window"])

        is_out_of_bounds = sensor_value < lower_threshold or sensor_value > upper_threshold

        if is_out_of_bounds:
            device_profile["OutOfBoundsCount"] = int(device_profile.get("OutOfBoundsCount", 0)) + 1
        else:
            device_profile["OutOfBoundsCount"] = 0

        if device_profile["OutOfBoundsCount"] >= time_window:
            device_profile["EventCount"] = int(device_profile.get("EventCount", 0)) + 1
            device_profile["OutOfBoundsCount"] = 0
            iot_republish(device_id, device_profile)

        table.update_item(
            Key={"PrinterId": device_id},
            UpdateExpression="SET OutOfBoundsCount = :oob, EventCount = :ec",
            ExpressionAttributeValues={
                ":oob": device_profile["OutOfBoundsCount"],
                ":ec": device_profile["EventCount"]
            },
            ReturnValues="UPDATED_NEW"
        )

        # Generate output for visibility
        generate_output()

    return response_json({"status": "processed"})

def get_printers():
    """Return all printer profiles for API Gateway GET request"""
    response = table.scan()
    items = response.get('Items', [])
    # convert Decimal values to int
    for item in items:
        item["EventCount"] = int(item["EventCount"])
    return response_json(items)

def response_json(data, status=200):
    """Helper to return proper HTTP response with CORS"""
    return {
        "statusCode": status,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type,Authorization,X-Api-Key,X-Amz-Date,X-Amz-Security-Token",
            "Access-Control-Allow-Methods": "GET,OPTIONS,POST"
        },
        "body": json.dumps(data, default=str)
    }

def iot_republish(device_id, new_record):
    event_count = int(new_record["EventCount"])
    payload = json.dumps({"PrinterId": device_id, "events": event_count})
    client.publish(topic="anom/pred", qos=1, payload=payload)

def generate_output():
    response = table.scan()
    devices = response.get('Items', [])
    sorted_devices = sorted(devices, key=lambda d: int(d['EventCount']), reverse=True)
    output = [(device['PrinterId'], int(device['EventCount'])) for device in sorted_devices]
    print("Sorted output (PrinterId, EventCount):")
    for device_id, event_count in output:
        print(f"{device_id}, {event_count}")
    return output
