from celery import shared_task
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import ScrapingSource, ScrapeJobLog
from properties.models import Property
from partners.models import Partner, Contract
from django.db.models import Count, Q
import requests
from bs4 import BeautifulSoup
import logging
import re
from django.utils.text import slugify
from hashlib import md5

logger = logging.getLogger(__name__)
User = get_user_model()

@shared_task
def scrape_source(source_id):
    """Tâche de scraping pour une source donnée"""
    try:
        source = ScrapingSource.objects.get(id=source_id, active=True)
    except ScrapingSource.DoesNotExist:
        logger.error(f"Source {source_id} not found or inactive")
        return
    
    # Créer un log de job
    job_log = ScrapeJobLog.objects.create(
        source=source,
        status='running'
    )
    
    try:
        # Sélectionner la fonction de scraping selon la source
        if 'jumia' in source.base_url.lower():
            items = scrape_jumia_house(source)
        elif 'boncoin' in source.base_url.lower():
            items = scrape_boncoin(source)
        elif 'expat' in source.base_url.lower():
            items = scrape_expat(source)
        elif 'booking' in source.base_url.lower():
            items = scrape_booking(source)
        else:
            items = []
        
        # Traitement des items
        items_created = 0
        items_updated = 0
        
        for item_data in items:
            property_obj, created = process_scraped_item(item_data, source)
            if created:
                items_created += 1
            else:
                items_updated += 1
        
        # Mettre à jour le log
        job_log.status = 'success'
        job_log.items_extracted = len(items)
        job_log.items_created = items_created
        job_log.items_updated = items_updated
        job_log.finished_at = timezone.now()
        job_log.save()
        
        # Mettre à jour la source
        source.last_scraped = timezone.now()
        source.save()
        
        logger.info(f"Scraping completed for {source.name}: {len(items)} items processed")
        
    except Exception as e:
        job_log.status = 'failed'
        job_log.errors = str(e)
        job_log.finished_at = timezone.now()
        job_log.save()
        logger.error(f"Scraping failed for {source.name}: {str(e)}")

def scrape_jumia_house(source):
    """Scraper spécifique pour Jumia House"""
    items = []
    try:
        response = requests.get(source.base_url, timeout=30)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Utiliser scraper_config si disponible
        config = source.scraper_config or {
            'card_selector': 'div.property-card',
            'title_selector': 'h3',
            'price_selector': 'span.price',
            'location_selector': 'span.location',
            'description_selector': 'p.description',
            'url_selector': 'a'
        }
        
        property_cards = soup.select(config['card_selector'])
        
        for card in property_cards:
            item = {
                'title': card.select_one(config['title_selector']).text.strip() if card.select_one(config['title_selector']) else '',
                'price': extract_price(card.select_one(config['price_selector'])),
                'location': card.select_one(config['location_selector']).text.strip() if card.select_one(config['location_selector']) else '',
                'description': card.select_one(config['description_selector']).text.strip() if card.select_one(config['description_selector']) else '',
                'source_url': (source.base_url.rstrip('/') + card.select_one(config['url_selector'])['href']) if card.select_one(config['url_selector']) else '',
            }
            items.append(item)
            
    except Exception as e:
        logger.error(f"Error scraping Jumia House: {str(e)}")
    
    return items

def scrape_boncoin(source):
    """Scraper spécifique pour Boncoin.cm"""
    items = []
    try:
        response = requests.get(source.base_url, timeout=30)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Utiliser scraper_config si disponible
        config = source.scraper_config or {
            'card_selector': 'div.listing-item',
            'title_selector': 'h2.title',
            'price_selector': 'span.price',
            'location_selector': 'span.location',
            'description_selector': 'p.description',
            'url_selector': 'a.listing-link'
        }
        
        listing_cards = soup.select(config['card_selector'])
        
        for card in listing_cards:
            item = {
                'title': card.select_one(config['title_selector']).text.strip() if card.select_one(config['title_selector']) else '',
                'price': extract_price(card.select_one(config['price_selector'])),
                'location': card.select_one(config['location_selector']).text.strip() if card.select_one(config['location_selector']) else '',
                'description': card.select_one(config['description_selector']).text.strip() if card.select_one(config['description_selector']) else '',
                'source_url': (source.base_url.rstrip('/') + card.select_one(config['url_selector'])['href']) if card.select_one(config['url_selector']) else '',
                'property_type': extract_property_type(card, config)
            }
            items.append(item)
            
    except Exception as e:
        logger.error(f"Error scraping Boncoin: {str(e)}")
    
    return items

def scrape_expat(source):
    """Scraper spécifique pour Expat.com"""
    items = []
    try:
        response = requests.get(source.base_url, timeout=30)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        config = source.scraper_config or {
            'card_selector': 'article.listing',
            'title_selector': 'h2',
            'price_selector': 'span.price',
            'location_selector': 'span.city',
            'description_selector': 'p.summary',
            'url_selector': 'a.listing-link'
        }
        
        listings = soup.select(config['card_selector'])
        
        for listing in listings:
            item = {
                'title': listing.select_one(config['title_selector']).text.strip() if listing.select_one(config['title_selector']) else '',
                'price': extract_price(listing.select_one(config['price_selector'])),
                'location': listing.select_one(config['location_selector']).text.strip() if listing.select_one(config['location_selector']) else '',
                'description': listing.select_one(config['description_selector']).text.strip() if listing.select_one(config['description_selector']) else '',
                'source_url': (source.base_url.rstrip('/') + listing.select_one(config['url_selector'])['href']) if listing.select_one(config['url_selector']) else '',
                'property_type': extract_property_type(listing, config)
            }
            items.append(item)
            
    except Exception as e:
        logger.error(f"Error scraping Expat.com: {str(e)}")
    
    return items

def scrape_booking(source):
    """Scraper spécifique pour Booking.com"""
    items = []
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(source.base_url, timeout=30, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        config = source.scraper_config or {
            'card_selector': 'div.sr_property_block',
            'title_selector': 'span.sr-hotel__name',
            'price_selector': 'div.bui-price-display__value',
            'location_selector': 'span.sr_card_address_line',
            'description_selector': 'div.hotel_desc',
            'url_selector': 'a.hotel_name_link'
        }
        
        hotels = soup.select(config['card_selector'])
        
        for hotel in hotels:
            item = {
                'title': hotel.select_one(config['title_selector']).text.strip() if hotel.select_one(config['title_selector']) else '',
                'price': extract_price(hotel.select_one(config['price_selector'])),
                'location': hotel.select_one(config['location_selector']).text.strip() if hotel.select_one(config['location_selector']) else '',
                'description': hotel.select_one(config['description_selector']).text.strip() if hotel.select_one(config['description_selector']) else '',
                'source_url': (source.base_url.rstrip('/') + hotel.select_one(config['url_selector'])['href']) if hotel.select_one(config['url_selector']) else '',
                'property_type': 'hotel'
            }
            items.append(item)
            
    except Exception as e:
        logger.error(f"Error scraping Booking.com: {str(e)}")
    
    return items

def extract_price(price_element):
    """Extrait et normalise le prix"""
    if not price_element:
        return None
    
    price_text = price_element.text.strip()
    price_match = re.search(r'[\d,]+', price_text.replace(' ', ''))
    if price_match:
        return float(price_match.group().replace(',', ''))
    return None

def extract_property_type(card, config):
    """Extrait le type de propriété"""
    type_selector = config.get('type_selector', 'span.property-type')
    type_text = card.select_one(type_selector).text.strip().lower() if card.select_one(type_selector) else ''
    
    type_mapping = {
        'house': 'house',
        'apartment': 'apartment',
        'land': 'land',
        'hotel': 'hotel',
        'maison': 'house',
        'appartement': 'apartment',
        'terrain': 'land',
        'hôtel': 'hotel'
    }
    
    for key, value in type_mapping.items():
        if key in type_text:
            return value
    return 'unknown'

def process_scraped_item(item_data, source):
    """Traite un item scrappé et crée/met à jour la propriété"""
    system_user, _ = User.objects.get_or_create(
        email='system@astremina.com',
        defaults={
            'username': 'system',
            'first_name': 'System',
            'last_name': 'Scraper',
            'is_active': False
        }
    )
    
    # Normaliser le titre pour le dédoublonnage
    normalized_title = slugify(item_data.get('title', ''))
    price = item_data.get('price', 0)
    location = item_data.get('location', '')
    
    # Générer un checksum pour le dédoublonnage
    checksum = md5(f"{normalized_title}{price}{location}".encode()).hexdigest()
    
    # Vérifier si la propriété existe déjà
    existing_property = Property.objects.filter(
        source=source,
        source_url=item_data.get('source_url', '')
    ).first() or Property.objects.filter(
        source=source,
        checksum=checksum
    ).first()
    
    property_data = {
        'title': item_data.get('title', ''),
        'description': item_data.get('description', ''),
        'property_type': item_data.get('property_type', 'unknown'),
        'price': price or 0,
        'currency': 'XAF',
        'city': extract_city(item_data.get('location', '')),
        'address': location,
        'source': source,
        'source_url': item_data.get('source_url', ''),
        'owner': system_user,
        'status': 'published',
        'checksum': checksum
    }
    
    if existing_property:
        # Mettre à jour
        for key, value in property_data.items():
            setattr(existing_property, key, value)
        existing_property.save()
        return existing_property, False
    else:
        # Créer nouveau
        property_obj = Property.objects.create(**property_data)
        return property_obj, True

def extract_city(location_text):
    """Extrait la ville à partir du texte de localisation"""
    if not location_text:
        return ''
    
    cities = ['Douala', 'Yaoundé', 'Bamenda', 'Bafoussam', 'Garoua', 'Maroua', 'Ngaoundéré']
    
    for city in cities:
        if city.lower() in location_text.lower():
            return city
    
    return location_text.split(',')[0].strip()

@shared_task
def check_contract_expirations():
    """Vérifie les contrats expirés et désactive les propriétés"""
    from partners.models import Contract
    from django.utils import timezone
    
    today = timezone.now().date()
    expired_contracts = Contract.objects.filter(
        end_date__lt=today,
        status='active'
    )
    
    for contract in expired_contracts:
        contract.status = 'expired'
        contract.save()
        
        Property.objects.filter(
            owner=contract.partner.user,
            status='published'
        ).update(status='disabled')
        
        logger.info(f"Contract expired for partner {contract.partner.company_name}")

@shared_task
def geocode_property(property_id):
    """Géocode une propriété"""
    try:
        from geopy.geocoders import Nominatim
        
        property_obj = Property.objects.get(id=property_id)
        if property_obj.latitude and property_obj.longitude:
            return
        
        geolocator = Nominatim(user_agent="astremina")
        location = geolocator.geocode(f"{property_obj.address}, {property_obj.city}, Cameroon")
        
        if location:
            property_obj.latitude = location.latitude
            property_obj.longitude = location.longitude
            property_obj.save()
            logger.info(f"Geocoded property {property_obj.title}")
        
    except Exception as e:
        logger.error(f"Geocoding failed for property {property_id}: {str(e)}")

@shared_task
def stats_aggregate_daily():
    """Agrège les statistiques quotidiennes pour le dashboard"""
    from django.utils import timezone
    from dashboard.models import DailyStats  # Assumes a DailyStats model in dashboard/models.py
    
    try:
        today = timezone.now().date()
        thirty_days_ago = today - timezone.timedelta(days=30)
        
        # Statistiques utilisateurs
        total_users = User.objects.count()
        active_users_30d = User.objects.filter(last_login__gte=thirty_days_ago).count()
        new_users_30d = User.objects.filter(date_joined__gte=thirty_days_ago).count()
        
        # Statistiques propriétés
        total_properties = Property.objects.count()
        published_properties = Property.objects.filter(status='published').count()
        new_properties_24h = Property.objects.filter(created_at__gte=today).count()
        
        # Statistiques partenaires
        total_partners = Partner.objects.count()
        active_contracts = Contract.objects.filter(status='active').count()
        
        # Enregistrer les stats
        DailyStats.objects.create(
            date=today,
            total_users=total_users,
            active_users_30d=active_users_30d,
            new_users_30d=new_users_30d,
            total_properties=total_properties,
            published_properties=published_properties,
            new_properties_24h=new_properties_24h,
            total_partners=total_partners,
            active_contracts=active_contracts
        )
        
        logger.info(f"Daily stats aggregated for {today}")
        
    except Exception as e:
        logger.error(f"Error aggregating daily stats: {str(e)}")