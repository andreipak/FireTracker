from django.db import models
from geopy import geocoders 

class State(models.Model):
    name = models.CharField(max_length=50)
    name_slug = models.SlugField()
    short_name = models.CharField(max_length=8)
    def __unicode__(self):
        return self.name

class City(models.Model):
    name = models.CharField(max_length=150)
    name_slug = models.SlugField()
    state = models.ForeignKey(State)
    def __unicode__(self):
        return self.name

class Department(models.Model):
    name = models.CharField(max_length=150)
    name_slug = models.SlugField()
    short_name = models.CharField(max_length=15)
    def __unicode__(self):
        return self.name

class Title(models.Model):
    title = models.CharField(max_length=50)
    title_short = models.CharField(max_length=10, blank=True, null=True)
    title_slug = models.SlugField()
    employer = models.ForeignKey(Department, blank=True, null=True)
    def __unicode__(self):
        return self.title

class Person(models.Model):
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    name_slug = models.SlugField()
    dob = models.DateField(blank=True, null=True)
    title = models.ForeignKey(Title, blank=True, null=True)
    experience = models.IntegerField(blank=True, null=True)
    def __unicode__(self):
        return "%s %s" % (self.first_name, self.last_name)
    def get_absolute_url(self):
        return "/firestarter/person/%s/%s" % (self.id, self.name_slug)

class Address(models.Model):
    street = models.CharField(max_length=150)
    street_slug = models.SlugField()
    city = models.ForeignKey(City)
    property_value = models.IntegerField(max_length=12, blank=True, null=True)
    owner = models.ManyToManyField(Person, blank=True, null=True)
    def __unicode__(self):
        return self.street
    def full_address(self):
        return u"%s, %s, %s" % (self.city.state, self.city, self.street)
    def get_lat(self):
        geocode = self.geocode_set.all()[0]
        return geocode.latitude
    def get_long(self):
        geocode = self.geocode_set.all()[0]
        return geocode.longitude
    
class Geocode(models.Model):
    address = models.ForeignKey(Address)
    computed_address = models.CharField(max_length=255, null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    geocode_error = models.BooleanField(default=False)
    def fill_geocode_data(self):
        if not self.address:
            self.geocode_error = True
            return 
        try:
            g = geocoders.Google()
            geo_address = self.address.full_address()
            self.computed_address, (self.latitude, self.longitude,) = g.geocode(geo_address)
            self.geocode_error = False
        except (UnboundLocalError, ValueError,geocoders.google.GQueryError):
            self.geocode_error = True
        return "%.5f, %.5f" % (self.latitude, self.longitude)
    
class Station(models.Model):
    name = models.CharField(max_length=150)
    name_slug = models.SlugField()
    department = models.ForeignKey(Department)
    address = models.ForeignKey(Address)
    def __unicode__(self):
        return self.name

class StoryLink(models.Model):
    link = models.CharField(max_length=250)
    headline = models.CharField(max_length=250, null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    def __unicode__(self):
        return self.headline

class Injury(models.Model):
    injury = models.CharField(max_length=150)
    injury_slug = models.SlugField()
    def __unicode__(self):
        return self.injury

class Victim(models.Model):
    person = models.ForeignKey(Person)
    injury = models.ForeignKey(Injury)
    def __unicode__(self):
        return "%s %s" % (self.person.last_name, self.injury.injury)

class Source(models.Model):
    source = models.ForeignKey(Person)
    def __unicode__(self):
        return self.source.name_slug

class Cause(models.Model):
    type = models.CharField(max_length=150)
    type_slug = models.SlugField()
    def __unicode__(self):
        return self.type

class Fire(models.Model):
    location = models.ForeignKey(Address)
    geocode = models.ForeignKey(Geocode, null=True, blank=True)
    cause = models.ForeignKey(Cause, blank=True, null=True)
    date = models.DateTimeField(blank=True, null=True)
    monetary_damage = models.IntegerField(blank=True, null=True)
    respondings = models.ManyToManyField(Station, blank=True, null=True)
    response_time = models.DateTimeField(blank=True, null=True)
    extinguish_time = models.DateTimeField(blank=True, null=True)
    story_links = models.ManyToManyField(StoryLink, blank=True, null=True)
    victims = models.ManyToManyField(Victim, blank=True, null=True)
    source = models.ForeignKey(Person, blank=True, null=True)
    def __unicode__(self):
        return "%s on %s" % (self.location, self.date)
    def time_took(self):
        return self.response_time - self.date
    def extinguish_time_took(self):
        return self.extinguish_time - self.response_time
    def get_absolute_url(self):
        return "/firestarter/fire/%s/%s" % (self.id, self.location.street_slug)
    def save(self, *args, **kwargs):
        if not self.geocode:
            g = Geocode(address=self.location)
            g.fill_geocode_data()
            g.save()
            self.geocode = g 
        super(Fire, self).save(*args, **kwargs)