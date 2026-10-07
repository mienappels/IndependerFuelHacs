# Independer Brandstofprijzen voor Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/mienappels/IndependerFuelHacs)

Home assistant custom component to fetch fuel prices from Independer.nl. This component is not affiliated with Independer.nl.

If independer.nl changes their website, this component may stop working. Please report any issues on the [Github page](https://github.com/mienappels/IndependerFuelHacs/issues).

## Installation

### HACS

1. Install [HACS](https://hacs.xyz/) if you haven't already.
2. Click the 3 dots in the top right corner of HACS.
3. select "Custom repositories".
4. Enter the following URL: (`https://github.com/mienappels/IndependerFuelHacs`)
5. select "Integration" as category.
6. Click "Add" to add the repository.
7. Search for "Independer Brandstofprijzen" in HACS and click "Install".
8. Continue with the configuration steps below.

### Configuration

```yaml
sensor:
  - platform: independer_fuel
    postal_code: "1234 AB"
    fuel_type: "euro95" # Options: euro98, euro95, diesel, lpg, aardgas, biodiesel, premium_benzine, premium_diesel
    range: 5 # Maximum distance in Km
    limit: 3 # Amount of fuel stations. Maximum is 5.
```

Scan interval is set to 4 hours. This is currently not configurable to avoid being blocked by Independer.nl. If you want to change the scan interval, open a pull request with your changes.

## Changelog
All notable changes to this project will be documented in the [CHANGELOG.md](./CHANGELOG.md) file.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## Legal notice
This component is not affiliated with Independer.nl. The developer of this component is not responsible for any issues that may arise from using this component. Use at your own risk.

For take down requests, please contact the developer directly via [discord](https://discordapp.com/users/304970705794105345).
