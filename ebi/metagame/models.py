from django.db import models
from django.contrib.auth.models import User

from django.db.models.signals import pre_save, post_save


class Photo(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    
    photo = models.ImageField(upload_to='game_photos', blank=True)
    

class Maker(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    name = models.CharField(max_length=255)
    slug = models.SlugField()
    
    description = models.TextField(blank=True)
    
    link = models.URLField(verify_exists=False, blank=True)
    updatesFeed = models.URLField(verify_exists=False, blank=True)
    
    # TODO maybe turn this into a foreign key again
    photos = models.ManyToManyField(Photo, blank=True)
    logo = models.ImageField(upload_to='maker_logos', blank=True)
    
    def __unicode__(self):
        return self.name
        
    def get_absolute_url(self):
        return '/makers/%s' % self.slug
        
    def first_game(self):
        if self.games.all():
            return self.games.all()[0]
        else:
            return None
    

class Festival(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    name = models.CharField(max_length=255)
    slug = models.SlugField()

    description = models.TextField(blank=True)
    
    link = models.URLField(verify_exists=False, blank=True)
    
    start = models.DateTimeField(blank=True, null=True)
    end = models.DateTimeField(blank=True, null=True)

    # maybe turn this into a foreign key again
    photos = models.ManyToManyField(Photo, blank=True)
    logo = models.ImageField(upload_to='festival_logos', blank=True)
    
    location = models.CharField(max_length=255, help_text="A geo-codable address", blank=True)

    def __unicode__(self):
        return self.name
        
    def get_absolute_url(self):
        return '/festivals/%s' % self.slug
        
    def first_game(self):
        if self.games.all():
            return self.games.all()[0]
        else:
            return None
    

class Game(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    name = models.CharField(max_length=255)
    slug = models.SlugField()
    
    description = models.TextField(blank=True)
    
    start = models.DateTimeField(blank=True, null=True)
    end = models.DateTimeField(blank=True, null=True)
    
    photos = models.ManyToManyField(Photo, blank=True)
    logo = models.ImageField(upload_to='game_logos', blank=True)
    
    maker = models.ForeignKey('Maker', related_name='games', blank=True, null=True)

    festival = models.ForeignKey('Festival', related_name='games', blank=True, null=True)
    
    interested = models.ManyToManyField('Player', blank=True)

    def __unicode__(self):
        return self.name
        
    def get_absolute_url(self):
        return '/games/%s/' % self.slug
        
    def get_first_photo(self):
        if self.photos.all():
            return self.photos.all()[0].photo.url
        else:
            return ''


# Creates player instances whenever you create a user
def user_post_save_callback(sender, instance, created, **kwargs):
    if created:
        try:
            Player.objects.get(user=instance)
        except Player.DoesNotExist:
            Player.objects.create(user=instance)
post_save.connect(user_post_save_callback, sender=User)


class Player(models.Model):
    # Player profile class
    user = models.ForeignKey(User, unique=True)
    
    twitter_name = models.CharField(max_length=255, blank=True)
    
    avatar = models.ImageField(upload_to="player_avatars", blank=True)
    
    created = models.DateTimeField(auto_now_add=True)
    
    rating = models.IntegerField(blank=True, null=True, default=100)
    
    # game_set.all()
    
    def get_challenger_duels(self):
        return self.challenger_duel.all().filter(open=True).order_by('-created')
        
    def get_responder_duels(self):
        return self.responder_duel.all().filter(open=True).order_by('-created')
    
    def __unicode__(self):
        return self.user.username
        
    def get_absolute_url(self):
        return '/players/%d/' % self.user.id