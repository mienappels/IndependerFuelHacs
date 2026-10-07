import logging
import async_timeout
from urllib.parse import quote
from datetime import timedelta

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import CONF_POSTAL_CODE

_LOGGER = logging.getLogger(__name__)

DOMAIN = "independer_fuel"

CONF_FUEL_TYPE = "fuel_type"
CONF_RANGE = "range"
CONF_LIMIT = "limit"

# Bijgewerkte mapping op basis van de exacte Independer waarden
FUEL_TYPES = {
    "euro98": 1,
    "euro95": 2,
    "diesel": 6,
    "lpg": 7,
    "aardgas": 14,
    "biodiesel": 17,
    "premium_benzine": 13,
    "premium_diesel": 12
}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_POSTAL_CODE): cv.string,
    vol.Optional(CONF_FUEL_TYPE, default="euro95"): vol.In(FUEL_TYPES.keys()),
    vol.Optional(CONF_RANGE, default=5): cv.positive_int,
    vol.Optional(CONF_LIMIT, default=1): vol.All(vol.Coerce(int), vol.Range(min=1, max=5)),
})

SCAN_INTERVAL = timedelta(hours=4)

async def async_setup_platform(hass, config, asyncAddEntities, discoveryInfo=None):
    postalCode = config[CONF_POSTAL_CODE]
    fuelType = config[CONF_FUEL_TYPE]
    searchRange = config[CONF_RANGE]
    resultLimit = config[CONF_LIMIT]

    httpClient = async_get_clientsession(hass)

    dataCoordinator = IndependerDataCoordinator(
        hass, httpClient, postalCode, fuelType, searchRange
    )

    await dataCoordinator.async_config_entry_first_refresh()

    entities = []
    for rank in range(resultLimit):
        entities.append(IndependerFuelSensor(dataCoordinator, postalCode, fuelType, rank))

    asyncAddEntities(entities)


class IndependerDataCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, session, postalCode, fuelType, searchRange):
        self.session = session
        self.postalCode = postalCode
        self.fuelType = fuelType
        self.searchRange = searchRange
        self.fuelId = FUEL_TYPES[self.fuelType]

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )

    async def _async_update_data(self):
        encodedPostalCode = quote(self.postalCode)
        apiUrl = f"https://www.independer.nl/api/autoverzekering/gasstation/getgasstations?addressInformation={encodedPostalCode}&fuelType={self.fuelId}&range={self.searchRange}&sorting=1"
        
        try:
            async with async_timeout.timeout(15):
                response = await self.session.get(
                    apiUrl, 
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36", 
                        "Accept": "application/json"
                    }
                )
                response.raise_for_status()
                
                jsonData = await response.json()
                
                return jsonData.get("gasStations", [])

        except Exception as errorMessage:
            raise UpdateFailed(f"Fout bij ophalen van Independer API: {errorMessage}")


class IndependerFuelSensor(SensorEntity):
    def __init__(self, coordinator, postalCode, fuelType, rank):
        self.coordinator = coordinator
        self.postalCode = postalCode
        self.fuelType = fuelType
        self.rank = rank
        
        displayRank = self.rank + 1
        
        self._attr_name = f"Brandstof {fuelType.replace('_', ' ').title()} ({postalCode}) #{displayRank}"
        self._attr_unique_id = f"independer_{postalCode}_{fuelType}_{displayRank}"
        self._attr_icon = "mdi:gas-station"
        self._attr_native_unit_of_measurement = "€/L" 

    @property
    def state(self):
        gasStations = self.coordinator.data
        if gasStations and len(gasStations) > self.rank:
            return gasStations[self.rank].get("fuel", {}).get("fuelPrice")
        return None

    @property
    def extra_state_attributes(self):
        gasStations = self.coordinator.data
        if gasStations and len(gasStations) > self.rank:
            stationData = gasStations[self.rank]
            return {
                "Tankstation": stationData.get("name"),
                "Afstand (km)": stationData.get("distance"),
                "Laatst Geüpdatet": stationData.get("fuel", {}).get("lastUpdated"),
                "Adres": f"{stationData.get('location', {}).get('address', {}).get('streetName', '')} {stationData.get('location', {}).get('address', {}).get('houseNumber', '')}, {stationData.get('location', {}).get('address', {}).get('city', '')}",
                "Rang": self.rank + 1
            }
        return {"Fout": "Niet genoeg tankstations gevonden binnen deze straal."}

    async def async_update(self):
        await self.coordinator.async_request_refresh()