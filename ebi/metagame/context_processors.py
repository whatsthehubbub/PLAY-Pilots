from django.core.cache import cache
from django.contrib.sites.models import Site
from django.contrib.auth.models import User

from services import feed_first_entry

from actstream.models import Action

def base(request):    
    # This already is cached by Django.
    site = Site.objects.get_current()
    
    # Cache all this stuff aggressively
    CACHE_DURATION = 60*60

    blogentry = cache.get('blogentry')
    if not blogentry:
        blogentry = feed_first_entry('http://ebi.posterous.com/rss.xml')
        cache.set('blogentry', blogentry, CACHE_DURATION)

    recent_users = User.objects.all().order_by('-last_login')

    actions = Action.objects.all().order_by('-timestamp')

    return {
        'SITE_DOMAIN': 'http://' + site.domain,
        'blogentry': blogentry,
        'users': recent_users[:3],
        'actions': actions
    }