<script setup>
import { onMounted, onUnmounted, computed } from 'vue'
import { useRobotStore } from '@/stores/robot'
import { fmt, color5v, colorDrivePack } from '@/utils/format'

const robot = useRobotStore()

const wsBadge = computed(() => {
  switch (robot.wsState) {
    case 'online':
      return { color: 'positive', label: 'ONLINE' }
    case 'connecting':
      return { color: 'warning', label: '…' }
    case 'error':
      return { color: 'negative', label: 'ERROR' }
    default:
      return { color: 'grey', label: 'OFFLINE' }
  }
})

const jsonText = computed(() => {
  if (!robot.rawFeed.length) return '-- ожидание данных --'
  const last = robot.rawFeed[robot.rawFeed.length - 1]
  return JSON.stringify({ time: last.stamp, ...last.data }, null, 2)
})

function onKeyDown(e) {
  if (e.repeat) return
  if (e.key === 'w') robot.setMotion(150, robot.steer)
  if (e.key === 's') robot.setMotion(-150, robot.steer)
  if (e.key === 'a') robot.setMotion(robot.gas, -150)
  if (e.key === 'd') robot.setMotion(robot.gas, 150)
}

function onKeyUp(e) {
  if (['w', 's'].includes(e.key)) robot.gas = 0
  if (['a', 'd'].includes(e.key)) robot.steer = 0
  if (['w', 's', 'a', 'd'].includes(e.key)) robot.sendMotion()
}

onMounted(() => {
  robot.connect()
  window.addEventListener('keydown', onKeyDown)
  window.addEventListener('keyup', onKeyUp)
})

onUnmounted(() => {
  window.removeEventListener('keydown', onKeyDown)
  window.removeEventListener('keyup', onKeyUp)
  if (robot.ws) robot.ws.close()
})
</script>

<template>
  <q-layout view="hHh lpR fFf" class="app-bg text-white">
    <q-header elevated class="bg-grey-10">
      <q-toolbar>
        <q-toolbar-title class="text-weight-medium">Car Control</q-toolbar-title>
        <q-space />
        <q-badge outline :color="wsBadge.color" :label="wsBadge.label" class="text-caption q-px-sm q-py-xs" />
        <q-btn flat dense round icon="refresh" class="q-ml-sm" @click="robot.connect()" />
      </q-toolbar>
    </q-header>

    <q-page-container>
      <q-page padding class="app-page">
        <div class="dashboard-grid">
          <!-- Левая колонка -->
          <div class="column q-gutter-md">
            <q-card flat bordered class="bg-grey-10">
              <q-card-section>
                <div class="text-subtitle1 text-weight-medium q-mb-sm">Скорость</div>
                <q-slider
                  :model-value="robot.maxSpeed"
                  @update:model-value="robot.setMaxSpeed"
                  :min="0"
                  :max="255"
                  :step="5"
                  color="primary"
                  label
                />
                <div class="text-h4 text-center text-primary q-mt-sm">{{ robot.maxSpeed }}</div>
              </q-card-section>
            </q-card>

            <q-card flat bordered class="bg-grey-10">
              <q-card-section>
                <div class="text-subtitle1 text-weight-medium q-mb-sm">Питание</div>
                <div class="text-caption text-grey-5 q-mb-xs">АКБ двигателей</div>
                <q-btn
                  :color="robot.lightOn ? 'negative' : 'primary'"
                  :label="robot.lightOn ? 'ВЫКЛ' : 'ВКЛ'"
                  class="full-width q-mb-md"
                  @click="robot.toggleDriveBattery()"
                />
                <div class="text-caption text-grey-5 q-mb-xs">Датчики / энкодеры</div>
                <q-btn
                  :color="robot.sensorPowerOn ? 'negative' : 'primary'"
                  :label="robot.sensorPowerOn ? 'ВЫКЛ' : 'ВКЛ'"
                  class="full-width"
                  @click="robot.toggleSensorRail()"
                />
              </q-card-section>
            </q-card>

            <q-card flat bordered class="bg-grey-10 json-card">
              <q-card-section>
                <div class="text-subtitle1 text-weight-medium q-mb-sm">JSON</div>
                <q-scroll-area style="height: 220px">
                  <pre class="json-pre">{{ jsonText }}</pre>
                </q-scroll-area>
              </q-card-section>
            </q-card>
          </div>

          <!-- Центр -->
          <div class="column q-gutter-md">
            <q-card flat bordered class="bg-grey-10 flex flex-center camera-card">
              <q-card-section class="full-width">
                <div class="text-h6 text-center q-mb-md">Камера</div>
                <q-banner rounded class="bg-grey-9 text-grey-4 text-center">
                  Поток и управление камерой — заготовка (позже).
                </q-banner>
              </q-card-section>
            </q-card>

            <q-card flat bordered class="bg-grey-10">
              <q-card-section>
                <div class="text-subtitle1 text-weight-medium q-mb-md text-center">Управление</div>
                <div class="controls-grid">
                  <div />
                  <q-btn color="primary" icon="keyboard_arrow_up" @click="robot.setMotion(150, 0)" />
                  <div />
                  <q-btn color="primary" icon="keyboard_arrow_left" @click="robot.setMotion(0, -150)" />
                  <q-btn color="warning" icon="stop" @click="robot.stopMotion()" />
                  <q-btn color="primary" icon="keyboard_arrow_right" @click="robot.setMotion(0, 150)" />
                  <div />
                  <q-btn color="primary" icon="keyboard_arrow_down" @click="robot.setMotion(-150, 0)" />
                  <div />
                </div>
                <div class="text-caption text-grey-5 text-center q-mt-md">WASD с клавиатуры</div>
              </q-card-section>
            </q-card>
          </div>

          <!-- Правая колонка -->
          <div class="column q-gutter-md">
            <q-card flat bordered class="bg-grey-10">
              <q-card-section>
                <div class="text-subtitle1 text-weight-medium q-mb-sm">Raspberry (5 V)</div>
                <q-list dense bordered class="rounded-borders bg-grey-9">
                  <q-item>
                    <q-item-section>Напряжение</q-item-section>
                    <q-item-section side>
                      <span :class="'text-' + color5v(robot.battery.raspberry?.bus_V)">
                        {{ fmt(robot.battery.raspberry?.bus_V, 2, 'V') }}
                      </span>
                    </q-item-section>
                  </q-item>
                  <q-item>
                    <q-item-section>Ток</q-item-section>
                    <q-item-section side>{{ fmt(robot.battery.raspberry?.current_mA, 1, 'mA') }}</q-item-section>
                  </q-item>
                  <q-item>
                    <q-item-section>Мощность</q-item-section>
                    <q-item-section side>{{ fmt(robot.battery.raspberry?.power_mW, 1, 'mW') }}</q-item-section>
                  </q-item>
                </q-list>
              </q-card-section>
            </q-card>

            <q-card flat bordered class="bg-grey-10">
              <q-card-section>
                <div class="text-subtitle1 text-weight-medium q-mb-sm">Привод (акб)</div>
                <q-list dense bordered class="rounded-borders bg-grey-9">
                  <q-item>
                    <q-item-section>Напряжение</q-item-section>
                    <q-item-section side>
                      <span :class="'text-' + colorDrivePack(robot.battery.drive?.bus_V)">
                        {{ fmt(robot.battery.drive?.bus_V, 2, 'V') }}
                      </span>
                    </q-item-section>
                  </q-item>
                  <q-item>
                    <q-item-section>Ток</q-item-section>
                    <q-item-section side>{{ fmt(robot.battery.drive?.current_mA, 1, 'mA') }}</q-item-section>
                  </q-item>
                  <q-item>
                    <q-item-section>Мощность</q-item-section>
                    <q-item-section side>{{ fmt(robot.battery.drive?.power_mW, 1, 'mW') }}</q-item-section>
                  </q-item>
                </q-list>
              </q-card-section>
            </q-card>

            <q-card flat bordered class="bg-grey-10">
              <q-card-section>
                <div class="text-subtitle1 text-weight-medium q-mb-sm">Датчики</div>
                <q-list dense bordered class="rounded-borders bg-grey-9">
                  <q-item>
                    <q-item-section>Ультразвук</q-item-section>
                    <q-item-section side>{{ fmt(robot.distanceCm, 1, 'см') }}</q-item-section>
                  </q-item>
                  <q-item v-for="n in ['ir1', 'ir2', 'ir3', 'ir4']" :key="n">
                    <q-item-section>{{ n }}</q-item-section>
                    <q-item-section side>
                      <q-badge :color="robot.ir?.[n] ? 'warning' : 'positive'" :label="robot.ir?.[n] ? 'ОБ' : 'OK'" />
                    </q-item-section>
                  </q-item>
                </q-list>
              </q-card-section>
            </q-card>

            <q-card flat bordered class="bg-grey-10">
              <q-card-section>
                <div class="text-subtitle1 text-weight-medium q-mb-sm">Энкодеры</div>
                <div class="row q-col-gutter-xs text-caption">
                  <div class="col-3" v-for="k in ['enc1', 'enc2', 'enc3', 'enc4']" :key="k">
                    <div class="text-grey-5">{{ k }}</div>
                    <div class="text-body2">{{ robot.encoders?.[k] ?? '—' }}</div>
                  </div>
                </div>
              </q-card-section>
            </q-card>
          </div>
        </div>
      </q-page>
    </q-page-container>
  </q-layout>
</template>

<style lang="sass">
.app-bg
  background: #0f1115
  min-height: 100vh

.app-page
  max-width: 1400px
  margin: 0 auto

.dashboard-grid
  display: grid
  grid-template-columns: minmax(240px, 280px) minmax(0, 1fr) minmax(240px, 320px)
  gap: 16px
  align-items: start

@media (max-width: 1024px)
  .dashboard-grid
    grid-template-columns: 1fr

.controls-grid
  display: grid
  grid-template-columns: repeat(3, 72px)
  gap: 8px
  justify-content: center

.camera-card
  min-height: 200px

.json-pre
  margin: 0
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace
  font-size: 11px
  white-space: pre-wrap
  word-break: break-word
  color: #cdd3dc
</style>
