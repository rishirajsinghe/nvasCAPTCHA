// src/features/aggregator.js

const behaviorCollector = require('../behavior/collector');
const browserEnvironment = require('../environment/browser');

// --- Helper Math Functions ---

function safeAvg(arr) {
  if (!arr || arr.length === 0) return 0;
  return arr.reduce((a, b) => a + b, 0) / arr.length;
}

function safeVariance(arr) {
  if (!arr || arr.length < 2) return 0;
  const mean = safeAvg(arr);
  return arr.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / arr.length;
}

function safeStdDev(arr) {
  return Math.sqrt(safeVariance(arr));
}

function calculateIntervals(timestamps) {
  const intervals = [];
  for (let i = 1; i < timestamps.length; i++) {
    intervals.push(timestamps[i] - timestamps[i - 1]);
  }
  return intervals;
}

// --- Feature Extractors ---

function extractMouseFeatures(mouseData) {
  const movements = mouseData.movements || [];
  const clicks = mouseData.clickTimestamps || [];

  let totalDistance = 0;
  const speeds = [];
  const accelerations = [];
  const angleChanges = [];
  let jitterCount = 0;

  const xCoords = [];
  const yCoords = [];

  for (let i = 0; i < movements.length; i++) {
    xCoords.push(movements[i].x);
    yCoords.push(movements[i].y);

    if (i > 0) {
      const p1 = movements[i - 1];
      const p2 = movements[i];
      const dt = p2.timestamp - p1.timestamp;
      const dx = p2.x - p1.x;
      const dy = p2.y - p1.y;

      const dist = Math.sqrt(dx * dx + dy * dy);
      totalDistance += dist;

      // Speed (pixels per ms)
      const speed = dt > 0 ? dist / dt : 0;
      speeds.push(speed);

      // Acceleration
      if (i > 1) {
        const prevSpeed = speeds[speeds.length - 2];
        const accel = dt > 0 ? (speed - prevSpeed) / dt : 0;
        accelerations.push(accel);
        
        // Angle Change
        const p0 = movements[i - 2];
        const angle1 = Math.atan2(p1.y - p0.y, p1.x - p0.x);
        const angle2 = Math.atan2(p2.y - p1.y, p2.x - p1.x);
        let angleChange = Math.abs(angle2 - angle1);
        if (angleChange > Math.PI) angleChange = 2 * Math.PI - angleChange; // Shortest angle
        angleChanges.push(angleChange);

        // Jitter: abrupt direction change > 90 degrees (PI/2) in a very short time
        if (angleChange > Math.PI / 2 && dt < 100) {
          jitterCount += 1;
        }
      }
    }
  }

  const clickIntervals = calculateIntervals(clicks);

  return {
    avgMouseSpeed: safeAvg(speeds),
    avgMouseAcceleration: safeAvg(accelerations),
    avgMouseAngleChange: safeAvg(angleChanges),
    clickCount: clicks.length,
    avgClickInterval: safeAvg(clickIntervals),
    mouseDistance: totalDistance,
    mouseJitter: jitterCount,
    xMovementVariance: safeVariance(xCoords),
    yMovementVariance: safeVariance(yCoords)
  };
}

function extractKeyboardFeatures(kbData, pageTimeMs) {
  const pageTimeMinutes = pageTimeMs > 0 ? pageTimeMs / 60000 : 0;
  
  // Keystrokes per minute
  const typingRate = pageTimeMinutes > 0 ? (kbData.keyPressCount / pageTimeMinutes) : 0;

  return {
    keyPressCount: kbData.keyPressCount,
    avgKeyHoldDuration: safeAvg(kbData.keyHoldDurations),
    avgKeystrokeInterval: safeAvg(kbData.keyPressIntervals),
    typingRate: typingRate,
    backspaceCount: kbData.backspaceCount,
    repeatedKeyCount: kbData.repeatedKeyCount,
    keyHoldStdDev: safeStdDev(kbData.keyHoldDurations)
  };
}

function extractScrollFeatures(scrollData) {
  const events = scrollData.scrollEvents || [];
  let totalScrollDistance = 0;
  const speeds = [];
  let directionChanges = 0;
  let lastDirection = 0; // 1 for down, -1 for up, 0 for none

  for (let i = 1; i < events.length; i++) {
    const e1 = events[i - 1];
    const e2 = events[i];
    
    const dy = e2.position - e1.position;
    const dt = e2.timestamp - e1.timestamp;
    const absDy = Math.abs(dy);
    
    totalScrollDistance += absDy;
    
    if (dt > 0) {
      speeds.push(absDy / dt);
    }

    const currentDirection = dy > 0 ? 1 : (dy < 0 ? -1 : 0);
    if (currentDirection !== 0 && lastDirection !== 0 && currentDirection !== lastDirection) {
      directionChanges += 1;
    }
    if (currentDirection !== 0) {
      lastDirection = currentDirection;
    }
  }

  return {
    scrollEventCount: events.length,
    totalScrollDistance: totalScrollDistance,
    avgScrollSpeed: safeAvg(speeds),
    scrollDirectionChanges: directionChanges
  };
}

function extractInteractionFeatures(interactionData, pageTimeMs) {
  const timestamps = interactionData.interactionTimestamps || [];
  const intervals = calculateIntervals(timestamps);

  return {
    pageTime: pageTimeMs,
    fieldInteractionCount: interactionData.interactions ? interactionData.interactions.length : 0,
    avgFieldInteractionInterval: safeAvg(intervals)
  };
}

class FeatureAggregator {
  aggregate() {
    const rawData = behaviorCollector.collectAllData();
    const envData = browserEnvironment.collect();

    // Ensure session end time is at least equal to start time
    let pageTime = 0;
    if (rawData.sessionStartTime && rawData.sessionEndTime) {
      pageTime = Math.max(0, rawData.sessionEndTime - rawData.sessionStartTime);
    }

    const mouseFeatures = extractMouseFeatures(rawData.mouse);
    const keyboardFeatures = extractKeyboardFeatures(rawData.keyboard, pageTime);
    const scrollFeatures = extractScrollFeatures(rawData.scroll);
    const interactionFeatures = extractInteractionFeatures(rawData.interaction, pageTime);

    // Flattening into the requested final ML numerical feature vector
    const behavioralFeatures = {
      ...mouseFeatures,
      ...keyboardFeatures,
      ...scrollFeatures,
      ...interactionFeatures
    };

    // Sanitize any potential NaNs or Infinities just in case
    for (const key in behavioralFeatures) {
      if (typeof behavioralFeatures[key] === 'number') {
         if (isNaN(behavioralFeatures[key]) || !isFinite(behavioralFeatures[key])) {
            behavioralFeatures[key] = 0;
         }
      }
    }

    return {
      environment: envData,
      behavior: behavioralFeatures,
      timestamp: Date.now()
    };
  }
}

module.exports = new FeatureAggregator();
