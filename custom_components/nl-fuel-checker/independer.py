import async_timeout
from urllib.parse import quote
from .source import FuelSource

class IndependerSource(FuelSource):
    def __init__(self, session, postalCode, fuelType, searchRange):
        super().__init__(session, postalCode, fuelType, searchRange)
        
        # Specifieke Independer mapping
        self.fuelMapping = {
            "euro98": 1, "euro95": 2, "diesel": 6, "lpg": 7, 
            "aardgas": 14, "biodiesel": 17, "premium_benzine": 13, "premium_diesel": 12
        }
        self.fuelId = self.fuelMapping.get(self.fuelType, 2)

    async def fetchPrices(self):
        encodedPostalCode = quote(self.postalCode)
        apiUrl = f"https://www.independer.nl/api/autoverzekering/gasstation/getgasstations?addressInformation={encodedPostalCode}&fuelType={self.fuelId}&range={self.searchRange}&sorting=1"
        
        async with async_timeout.timeout(15):
            response = await self.session.get(
                apiUrl, 
                headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
            )
            response.raise_for_status()
            jsonData = await response.json()
            
            gasStations = jsonData.get("gasStations", [])
            validStations = []
            
            for station in gasStations:
                validStations.append({
                    "name": station.get("name"),
                    "brand": "Onbekend", 
                    "address": f"{station.get('location', {}).get('address', {}).get('streetName', '')} {station.get('location', {}).get('address', {}).get('houseNumber', '')}",
                    "city": station.get('location', {}).get('address', {}).get('city', ''),
                    "price": station.get("fuel", {}).get("fuelPrice"),
                    "distanceKm": "N/A", # Geforceerd naar N/A zoals gevraagd
                    "lastUpdated": station.get("fuel", {}).get("lastUpdated"),
                    "latitude": station.get("location", {}).get("coordinates", {}).get("latitude"),
                    "longitude": station.get("location", {}).get("coordinates", {}).get("longitude")
                })
            
            return validStations