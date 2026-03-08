const wsStatus = document.getElementById("wsStatus");
const ws = new WebSocket(`ws://${location.host}/ws`);

let gas = 0;
let steer = 0;
let currentSpeed = 150;

// WS статус
ws.onopen = () => wsStatus.textContent = "🟢 ONLINE";
ws.onclose = () => wsStatus.textContent = "🔴 OFFLINE";
ws.onerror = () => wsStatus.textContent = "🔴 ERROR";

// данные
ws.onmessage = (event) => {
    try {
        const data = JSON.parse(event.data);
        console.log("batDrive: ", data.battery.drive.bus_V)
        console.log("batRaspberry: ", data.battery.raspberry.bus_V)
//        toString()
        if (data.battery) {
            updateBattery("batDriveBus_V", data.battery.drive.bus_V, "V");
            updateBattery("batRaspberryBus_V", data.battery.raspberry.bus_V, "V");

            updateBattery("batRaspberryCurrent_mA", data.battery.raspberry.current_mA, "mA");
            updateBattery("batDriveCurrent_mA", data.battery.drive.current_mA, "mA");

            updateBattery("batDrivePower_mW", data.battery.drive.power_mW, "mW");
            updateBattery("batRaspberryPower_mW", data.battery.raspberry.power_mW, "mW");

            updateBattery("batDriveOverflow", data.battery.drive.overflow);
            updateBattery("batRaspberryOverflow", data.battery.raspberry.overflow);


        }
        if (data.raspi_temp !== undefined) {
            updateTemp(data.raspi_temp);
        }
        if (data.system_info) {
            setText("cpuLoad", data.system_info.cpu_percent, "%");
            setText("ramLoad", data.system_info.memory_percent, "%");
            setText("diskLoad", data.system_info.disk_percent, "%");
        }
        if (data.throttled_status) {
	        document.getElementById("throttled").textContent = data.throttled_status.issues_now.join(",<br>");
        }
        if (data.obstacle) {
	        document.getElementById("obstacleInFront").textContent = data.obstacle.obstacleInFront;
	        document.getElementById("sensorValueFront").textContent = data.obstacle.sensorValueFront;
	        document.getElementById("obstacleInBack").textContent = data.obstacle.obstacleInBack;
	        document.getElementById("sensorValueBack").textContent = data.obstacle.sensorValueBack;
        }

    } catch (e) {
        console.error("JSON error", e);
    }
};

// цвет батареи
function updateBattery(id, value, units_measurement="") {
    const el = document.getElementById(id);
    el.textContent = value.toFixed(2) + " " + units_measurement;

    if (value > 4) el.style.color = "#4CAF50";
    else if (value > 3) el.style.color = "#FFC107";
    else el.style.color = "#F44336";
}

// температура
function updateTemp(temp) {
    const el = document.getElementById("cpuTemp");
    el.textContent = temp.toFixed(1) + " °C";

    if (temp < 60) el.style.color = "#4CAF50";
    else if (temp < 75) el.style.color = "#FFC107";
    else el.style.color = "#F44336";
}

function setText(id, value, unit) {
    document.getElementById(id).textContent = value.toFixed(1) + " " + unit;
}

// скорость
function updateSpeedDisplay() {
  document.getElementById('speedValue').textContent = currentSpeed;
}

document.getElementById('speedSlider').addEventListener('input', function(e) {
  currentSpeed = parseInt(e.target.value);
  updateSpeedDisplay();

  if (gas !== 0 || steer !== 0) {
    sendWithSpeed(gas, steer);
  }
});

// отправка
function sendWithSpeed(g, s) {
  if (g !== 0 || s !== 0) {
    const speedMultiplier = currentSpeed / 150;
    g = Math.round(g * speedMultiplier);
    s = Math.round(s * speedMultiplier);
  }

  gas = g;
  steer = s;
  ws.send(JSON.stringify({ gas, steer }));
}
let camAngle = 90;   // стартовое положение
const CAM_MIN = 25;
const CAM_MAX = 95;

function moveCamera(step) {
  camAngle += step;

  if (camAngle < CAM_MIN) camAngle = CAM_MIN;
  if (camAngle > CAM_MAX) camAngle = CAM_MAX;

  document.getElementById("camAngle").textContent = camAngle;

  ws.send(JSON.stringify({
    camera_angle: camAngle
  }));
}
// клавиатура
document.addEventListener("keydown", e => {
  if (e.repeat) return;
  if (e.key === "ArrowUp" || e.key === "+") {
    moveCamera(1);
  }
  if (e.key === "ArrowDown" || e.key === "-") {
    moveCamera(-1);
  }
});
// WSAD
document.addEventListener("keydown", e => {
  if (e.repeat) return;

  if (e.key === "w") sendWithSpeed(150, steer);
  if (e.key === "s") sendWithSpeed(-150, steer);
  if (e.key === "a") sendWithSpeed(gas, -150);
  if (e.key === "d") sendWithSpeed(gas, 150);
});

document.addEventListener("keyup", e => {
  if (["w","s"].includes(e.key)) gas = 0;
  if (["a","d"].includes(e.key)) steer = 0;
  sendWithSpeed(gas, steer);
});

let lightOn = false;

function toggleLight() {
  lightOn = !lightOn;

  document.getElementById("lightStatus").textContent = lightOn ? "ON" : "OFF";
  document.getElementById("lightStatus").style.color = lightOn ? "#4CAF50" : "#F44336";
  document.getElementById("lightBtn").textContent = lightOn ? "ВЫКЛ" : "ВКЛ";

  ws.send(JSON.stringify({
    light: lightOn ? 1 : 0
  }));
}

// init
updateSpeedDisplay();

