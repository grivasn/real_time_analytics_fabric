from ultralytics import YOLO
from azure.eventhub import EventHubProducerClient, EventData
from datetime import datetime
import json
from dotenv import load_dotenv
load_dotenv()
import os

CONN_URL = os.getenv("CONN_URL")


idler = set()

client = EventHubProducerClient.from_connection_string(CONN_URL)

model = YOLO("yolo11s.pt")

with client:
    results = model.track(source = "video.mp4", show = True, stream = True, tracker = "botsort.yaml", verbose = False, classes = 0, conf = 0.5)
    for result in results:
        if result.boxes.id is not None:
            ids = result.boxes.id.cpu().numpy().astype(int)
            confs = result.boxes.conf.cpu().numpy()

            batch = client.create_batch()
            data_added = False

            for id,conf in zip(ids,confs):
                if id not in idler:
                    idler.add(id)

                    payload = {
                        "ID": int(id),
                        "Confidence": float(conf),
                        "Timestamp": datetime.now().isoformat(),
                        "source": "video.mp4",
                        "Time": datetime.now().strftime("%Y-%m-%d %H:%M")
                    }

                    batch.add(EventData(json.dumps(payload)))
                    data_added = True
                    print(f"Yeni ID bulundu: {id}, Confidence: {conf}, payload: {payload['Time']}")
                    
            if data_added:
                client.send_batch(batch)