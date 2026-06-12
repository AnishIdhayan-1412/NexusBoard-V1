from communities.models import Community


def site_context(request):
    return {
        'site_name': 'NexusBoard',
        'site_tagline': 'Where Ideas Connect',
        'total_communities': Community.objects.count(),
    }
