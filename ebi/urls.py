from django.conf.urls.defaults import *
from django.conf import settings

from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Example:
    # (r'^shohaiti/', include('shohaiti.haiti.urls')),

    (r'^admin/', include(admin.site.urls)),
)

urlpatterns += patterns('ebi.metagame.views',
    (r'^$', 'index'),
	
	(r'^players/$', 'player_list'),
	(r'^players/(?P<id>\d+)/$', 'player_detail'),
	
	(r'^game/(?P<slug>\S+?)/$', 'game_detail'),
	(r'^maker/(?P<slug>\S+?)/$', 'maker_detail'),
	(r'^festival/(?P<slug>\S+?)/$', 'festival_detail'),
)


# Created flat pages for this
# urlpatterns += patterns('django.views.generic.simple',
  # (r'^about/$', 'direct_to_template', {'template': 'metagame/about.html'}),
  # (r'^contact/$', 'direct_to_template', {'template': 'metagame/contact.html'}),
# )


urlpatterns += patterns('',
    (r'^login/$', 'django.contrib.auth.views.login')
)

# TODO configure static file serving for deployment server
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/Users/alper/Documents/projects/play/site/media'})
    )