import asyncio
import async_timeout
from urllib.parse import quote
from .source import FuelSource

class PompwijzerSource(FuelSource):
    def __init__(self, session, postalCode, fuelType, searchRange):
        super().__init__(session, postalCode, fuelType, searchRange)
        self.lat = None
        self.lon = None
        
        self.supportedFuels = ["euro95", "euro98", "diesel"]
        if self.fuelType not in self.supportedFuels:
            raise ValueError(f"Bron 'pompwijzer' ondersteunt uitsluitend {self.supportedFuels}. Ongeldige keuze: '{self.fuelType}'.")

    async def fetchCoordinates(self):
        encodedAddress = quote(self.postalCode)
        encodedAddress = encodedAddress.replace("%20", "") 
        encodedAddress = encodedAddress.replace(" ", "")
        url = f"https://nominatim.openstreetmap.org/search?q={encodedAddress}&format=json&limit=1"
        headers = {"User-Agent": "NlFuelChecker/1.0"}
        
        async with async_timeout.timeout(10):
            response = await self.session.get(url, headers=headers)
            response.raise_for_status()
            data = await response.json()
            
            if data:
                self.lat = float(data[0]["lat"])
                self.lon = float(data[0]["lon"])
            else:
                raise Exception(f"Kan geen coördinaten vinden voor: {self.postalCode}")

    async def fetchPrices(self):
        if not self.lat or not self.lon:
            await self.fetchCoordinates()

        urlDistances = f"https://api.pompwijzer.nl/api/location-distances?location={self.lon}%2C{self.lat}&radius_km={self.searchRange}"
        urlPrices = f"https://api.pompwijzer.nl/api/stations?fuel_type={self.fuelType}&has_price=true"
        
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json"
        }

        async with async_timeout.timeout(15):
            distanceTask = self.session.get(urlDistances, headers=headers)
            priceTask = self.session.get(urlPrices, headers=headers)
            
            responseDistances, responsePrices = await asyncio.gather(distanceTask, priceTask)
            
            responseDistances.raise_for_status()
            responsePrices.raise_for_status()
            
            jsonDistances = await responseDistances.json()
            jsonPrices = await responsePrices.json()

        stationsInRadius = {
            station["station_id"]: station 
            for station in jsonDistances.get("stations", [])
        }
        
        validStations = []
        
        for station in jsonPrices:
            stationId = station.get("id")
            if stationId in stationsInRadius:
                distanceInfo = stationsInRadius[stationId]
                priceInfo = station.get("price", {})
                actualPrice = priceInfo.get("price")
                
                if actualPrice is not None:
                    drivingDistanceKm = distanceInfo.get("driving_distance", 0) / 1000
                    
                    validStations.append({
                        "name": station.get("name"),
                        "brand": station.get("brand"),
                        "address": station.get("address"),
                        "city": station.get("city"),
                        "price": actualPrice,
                        "distanceKm": round(drivingDistanceKm, 2),
                        "lastUpdated": priceInfo.get("timestamp"),
                        "latitude": station.get("lat"),
                        "longitude": station.get("lon")
                    })
        
        validStations.sort(key=lambda s: s["price"])
        return validStations