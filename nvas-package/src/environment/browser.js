
class BrowserEnvironment {
  collect() {
    return {
      userAgent: navigator.userAgent,
      screenResolution: {
        width: window.screen ? window.screen.width : 0,
        height: window.screen ? window.screen.height : 0
      },
      touchSupport: 'ontouchstart' in window || navigator.maxTouchPoints > 0,
      language: navigator.language,
      platform: navigator.platform,
      hardwareConcurrency: navigator.hardwareConcurrency || 1,
      doNotTrack: navigator.doNotTrack === '1' || navigator.doNotTrack === 'yes',
      timeZoneOffset: new Date().getTimezoneOffset()
    };
  }
}

module.exports = new BrowserEnvironment();
