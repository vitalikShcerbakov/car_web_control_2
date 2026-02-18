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

        if (data.battery) {
            updateBattery("bat1", data.battery.bat1);
            updateBattery("bat2", data.battery.bat2);
            updateBattery("ups", data.battery.ups);
        }

        if (data.raspi_temp !== undefined) {
            updateTemp(data.raspi_temp);
        }

        if (data.system_info) {
            setText("cpuLoad", data.system_info.cpu_percent, "%");
            setText("ramLoad", data.system_info.memory_percent, "%");
            setText("diskLoad", data.system_info.disk_percent, "%");
        }

    } catch (e) {
        console.error("JSON error", e);
    }
};

// цвет батареи
function updateBattery(id, value) {
    const el = document.getElementById(id);
    el.textContent = value.toFixed(2) + " V";

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

// init
updateSpeedDisplay();

