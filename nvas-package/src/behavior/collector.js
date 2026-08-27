// src/behavior/collector.js

const mouse = require('./mouse');
const keyboard = require('./keyboard');
const scroll = require('./scroll');
const interaction = require('./interaction');

class BehaviorCollector {
  constructor() {
    this.sessionStartTime = null;
  }

  startAll() {
    this.sessionStartTime = Date.now();
    mouse.start();
    keyboard.start();
    scroll.start();
    interaction.start();
  }

  stopAll() {
    mouse.stop();
    keyboard.stop();
    scroll.stop();
    interaction.stop();
  }

  collectAllData() {
    return {
      sessionStartTime: this.sessionStartTime,
      sessionEndTime: Date.now(),
      mouse: mouse.getData(),
      keyboard: keyboard.getData(),
      scroll: scroll.getData(),
      interaction: interaction.getData()
    };
  }

  resetAll() {
    this.sessionStartTime = Date.now();
    mouse.reset();
    keyboard.reset();
    scroll.reset();
    interaction.reset();
  }
}

module.exports = new BehaviorCollector();
