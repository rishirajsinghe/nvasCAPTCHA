# NVAS CAPTCHA

A modular behavior collection and ML-based adaptive bot detection package.

## Usage

```javascript
import NvasCaptcha from 'nvas-captcha';

// Initialize the package
NvasCaptcha.init();

// When verifying a user action (e.g. login)
const result = await NvasCaptcha.verify();
```

## Architecture

This package is designed modularly to capture environmental and behavioural data independently for privacy-first bot detection.
