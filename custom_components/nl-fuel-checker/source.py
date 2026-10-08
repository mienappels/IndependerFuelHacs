class FuelSource:
    def __init__(self, session, postalCode, fuelType, searchRange):
        self.session = session
        self.postalCode = postalCode
        self.fuelType = fuelType
        self.searchRange = searchRange

    async def fetchPrices(self):
        """
        Moet worden overschreven door de subklasse.
        Verwacht een lijst met dictionaries: 
        [{'name': '', 'brand': '', 'address': '', 'city': '', 'price': 0.0, 'distanceKm': 0.0 of 'N/A', 'lastUpdated': '', 'latitude': 0.0, 'longitude': 0.0}]
        """
        raise NotImplementedError("fetchPrices moet worden geïmplementeerd door de subklasse")