class GeoService:
    def __init__(self, postcode_region_map: dict):
        self.postcode_region_map = postcode_region_map

    def get_region_by_postcode(self, postcode: str) -> str:
        return self.postcode_region_map.get(postcode[:3], "Unknown")