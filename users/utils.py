def get_client_ip(request):
  x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
  if x_forwarded_for:
    ip = x_forwarded_for.split(',')[0]  # Take the first IP
  else:
    ip = request.META.get('REMOTE_ADDR')
  return ip




import geoip2.database

GEOIP_DB_PATH = "geoip/GeoLite2-City.mmdb"  # Path to your GeoLite2 database

def annotate_login_history_with_location(history_queryset):
    """
    Annotates a queryset of LoginHistory objects with city, state, and country
    based on their IP addresses.
    """
    reader = geoip2.database.Reader(GEOIP_DB_PATH)

    for entry in history_queryset:
        try:
            response = reader.city(entry.ip_address)
            entry.city = response.city.name or "Unknown"
            entry.state = response.subdivisions.most_specific.name or "Unknown"
            entry.country = response.country.name or "Unknown"
        except:
            entry.city = entry.state = entry.country = "Unknown"

    reader.close()
    return history_queryset
