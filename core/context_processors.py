from django.core.cache import cache
from communities.models import Community


def site_context(request):
    # Cache community count for 5 minutes — avoids a DB hit on every page load.
    total_communities = cache.get('ctx_total_communities')
    if total_communities is None:
        total_communities = Community.objects.count()
        cache.set('ctx_total_communities', total_communities, 300)
    return {
        'site_name': 'NexusBoard',
        'site_tagline': 'Where Ideas Connect',
        'total_communities': total_communities,
    }
