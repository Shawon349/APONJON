from django.db import models
from .utils import haversine_distance

class Location(models.Model):
    """
    Location model as specified in the Class Diagram.
    Stores precise geolocation (lat/long) as well as administrative zones (thana, area, city).
    """
    locationID = models.AutoField(primary_key=True)
    address = models.CharField(max_length=255, help_text="Street address or landmark")
    area = models.CharField(max_length=120, help_text="Local area or neighborhood e.g. Dhanmondi 27")
    city = models.CharField(max_length=80, default="Dhaka")
    thana = models.CharField(max_length=80, help_text="Police Station jurisdiction area e.g. Dhanmondi")
    postalCode = models.CharField(max_length=20, blank=True, null=True)
    latitude = models.FloatField(default=23.7500, help_text="Geographical latitude")
    longitude = models.FloatField(default=90.3800, help_text="Geographical longitude")

    class Meta:
        verbose_name = "Location"
        verbose_name_plural = "Locations"

    def __str__(self):
        return f"{self.area}, {self.thana}, {self.city}"

    @classmethod
    def createLocation(cls, address, area, thana, city="Dhaka", postalCode="", latitude=23.7500, longitude=90.3800):
        """Class method matching Class Diagram createLocation()"""
        return cls.objects.create(
            address=address,
            area=area,
            thana=thana,
            city=city,
            postalCode=postalCode,
            latitude=latitude,
            longitude=longitude
        )

    def viewLocation(self):
        """Returns formatted location summary"""
        return {
            "locationID": self.locationID,
            "address": self.address,
            "area": self.area,
            "thana": self.thana,
            "city": self.city,
            "coordinates": (self.latitude, self.longitude)
        }

    def updateLocation(self, **kwargs):
        """Updates location fields dynamically"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.save()
        return self

    def findNearbyUsers(self, radius_km=10.0):
        """
        Finds registered users (Reporters and Police Officers) within the radius_km 
        or located in the same Thana/Area.
        """
        from accounts.models import User, Reporter, PoliceOfficer

        nearby_users = set()

        # 1. Check all users whose reporter/officer profile location is within radius
        for reporter in Reporter.objects.select_related('user', 'location').all():
            if reporter.location:
                # Same thana match or distance match
                if reporter.location.thana.strip().lower() == self.thana.strip().lower():
                    nearby_users.add(reporter.user)
                else:
                    dist = haversine_distance(self.latitude, self.longitude, reporter.location.latitude, reporter.location.longitude)
                    if dist <= radius_km:
                        nearby_users.add(reporter.user)

        for officer in PoliceOfficer.objects.select_related('user', 'location').all():
            if officer.location:
                if officer.location.thana.strip().lower() == self.thana.strip().lower() or officer.jurisdiction.strip().lower() == self.thana.strip().lower():
                    nearby_users.add(officer.user)
                else:
                    dist = haversine_distance(self.latitude, self.longitude, officer.location.latitude, officer.location.longitude)
                    if dist <= radius_km:
                        nearby_users.add(officer.user)

        return list(nearby_users)
