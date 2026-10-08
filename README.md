# NL Fuel Checker for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/mienappels/NL-fuel-checker)

Home Assistant custom integration to fetch fuel prices from multiple Dutch sources, including Independer and PompWijzer. This component is not affiliated with either service provider.

If the upstream fuel providers change their APIs or website behavior, this integration may stop working. Please report issues on the [GitHub page](https://github.com/mienappels/NL-fuel-checker/issues).

## Installation

### HACS

1. Install [HACS](https://hacs.xyz/) if you haven't already.
2. Click the 3 dots in the top right corner of HACS.
3. Select "Custom repositories".
4. Enter the following URL: (`https://github.com/mienappels/NL-fuel-checker`)
5. Select "Integration" as the category.
6. Click "Add" to add the repository.
7. Search for "NL Fuel Checker" in HACS and click "Install".
8. Continue with the configuration steps below.

### Configuration

```yaml
sensor:
  - platform: nl_fuel_checker
    postal_code: "1234 AB"
    fuel_type: "euro95" # Options for Independer: euro98, euro95, diesel, lpg, aardgas, biodiesel, premium_benzine, premium_diesel
    range: 5 # Maximum distance in km
    limit: 3 # Amount of fuel stations. Maximum is 5.
    source: "independer" # Optional: "independer" (default) or "pompwijzer"; PompWijzer currently supports only euro95, euro98 and diesel
```

The integration fetches prices from one or more configured Dutch fuel price providers. The scan interval is set to 4 hours to avoid rate limiting. If you want to change the scan interval, open a pull request with your changes.

## Changelog
All notable changes to this project will be documented in the [CHANGELOG.md](./CHANGELOG.md) file.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## Legal notice
This custom integration is not affiliated with, endorsed by, or sponsored by Independer, PompWijzer, or any other fuel price provider. It is an independent Home Assistant integration built to read publicly available pricing data from supported sources.

The developer is not responsible for any issues, data inaccuracies, downtime, rate limiting, or legal concerns arising from the use of third-party provider data. Use this integration at your own risk.

For takedown requests or inquiries, please contact the developer directly via [Discord](https://discordapp.com/users/304970705794105345).
