import os
from pathlib import Path

import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse, StreamingResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from app.core.arduino import find_arduino_port
from app.core.robot import RobotController
from app.comm.arduino import ArduinoProtocol
from app.comm.websocket import ConnectionManager, router as ws_router
from app.services.control_loop import control_loop
from app.services.telemetry_loop import telemetry_loop

import serial_asyncio

BASE_DIR = Path(__file__).resolve().parent
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

robot = RobotController()
manager = ConnectionManager()
arduino_proto = None

app.include_router(ws_router(manager, robot))

@app.on_event("startup")
async def startup():
    global arduino_proto

    loop = asyncio.get_running_loop()
    port = find_arduino_port()
    transport, protocol = await serial_asyncio.create_serial_connection(
        loop,
        lambda: ArduinoProtocol(robot),
        url=port,
        baudrate=115200
    )

    arduino_proto = protocol

    asyncio.create_task(control_loop(robot, lambda: arduino_proto))
    asyncio.create_task(telemetry_loop(robot, manager))

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

SPA_DIR = BASE_DIR / "static" / "spa"
SPA_ASSETS = SPA_DIR / "assets"
if SPA_ASSETS.is_dir():
    app.mount("/assets", StaticFiles(directory=str(SPA_ASSETS)), name="spa_assets")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    spa_index = SPA_DIR / "index.html"
    if spa_index.is_file():
        return FileResponse(spa_index)
    return templates.TemplateResponse("index.html", {"request": request})
