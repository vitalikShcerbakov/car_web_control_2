import { defineStore } from 'pinia'

function wsUrl() {
  const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  return `${proto}//${window.location.host}/ws`
}

export const useRobotStore = defineStore('robot', {
  state: () => ({
    wsState: 'offline',
    ws: null,
    battery: { drive: null, raspberry: null },
    encoders: null,
    telemetry: null,
    rawFeed: [],
    gas: 0,
    steer: 0,
    maxSpeed: 150,
    lightOn: false,
    sensorPowerOn: true,
    /** Логика на Arduino: 1 — защита по ИК/УЗ, 0 — выкл */
    safetyOn: true,
  }),

  getters: {
    ir() {
      return this.telemetry?.IRSensor ?? null
    },
    distanceCm() {
      const d = this.telemetry?.ultrasonicSensor?.distance
      return d == null ? null : Number(d)
    },
  },

  actions: {
    connect() {
      if (this.ws) {
        try {
          this.ws.close()
        } catch (_) {
          /* ignore */
        }
        this.ws = null
      }
      this.wsState = 'connecting'
      const socket = new WebSocket(wsUrl())
      this.ws = socket

      socket.onopen = () => {
        this.wsState = 'online'
      }
      socket.onclose = () => {
        this.wsState = 'offline'
        this.ws = null
      }
      socket.onerror = () => {
        this.wsState = 'error'
      }
      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          this.applyMessage(data)
        } catch (e) {
          console.error('WS JSON parse error', e)
        }
      }
    },

    applyMessage(data) {
      if (data.battery) {
        this.battery = {
          drive: data.battery.drive ?? null,
          raspberry: data.battery.raspberry ?? null,
        }
      }
      if (data.encoders) this.encoders = data.encoders
      if (data.telemetry) this.telemetry = data.telemetry

      const stamp = new Date().toLocaleTimeString()
      this.rawFeed.push({ stamp, data })
      if (this.rawFeed.length > 120) this.rawFeed.splice(0, this.rawFeed.length - 120)
    },

    sendJson(payload) {
      if (!this.ws || this.ws.readyState !== WebSocket.OPEN) return
      this.ws.send(JSON.stringify(payload))
    },

    sendMotion() {
      let g = this.gas
      let s = this.steer
      if (g !== 0 || s !== 0) {
        const m = this.maxSpeed / 150
        g = Math.round(g * m)
        s = Math.round(s * m)
      }
      this.sendJson({ gas: g, steer: s })
    },

    setMaxSpeed(v) {
      this.maxSpeed = v
      if (this.gas !== 0 || this.steer !== 0) this.sendMotion()
    },

    setMotion(g, s) {
      this.gas = g
      this.steer = s
      this.sendMotion()
    },

    stopMotion() {
      this.gas = 0
      this.steer = 0
      this.sendMotion()
    },

    toggleDriveBattery() {
      this.lightOn = !this.lightOn
      this.sendJson({ light: this.lightOn ? 1 : 0 })
    },

    toggleSensorRail() {
      this.sensorPowerOn = !this.sensorPowerOn
      this.sendJson({ telemetry: this.sensorPowerOn ? 1 : 0 })
    },

    toggleSafety() {
      this.safetyOn = !this.safetyOn
      this.sendJson({ safety: this.safetyOn ? 1 : 0 })
    },
  },
})
