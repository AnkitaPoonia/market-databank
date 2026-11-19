import datetime
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from databank.models import Category, MarketData, ActivityLog

class Command(BaseCommand):
    help = 'Populates the database with sample categories and illustrative market datasets for testing and demonstration.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Specify an existing username to be assigned as the creator of the sample datasets.'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Initializing sample market databank data..."))

        # 1. Populate Standard Categories
        categories_data = [
            {
                'name': 'Automobile',
                'description': 'Commercial vehicles, passenger electric mobility, automotive OEM components, and fleet logistics.'
            },
            {
                'name': 'Information Technology',
                'description': 'Enterprise cloud platforms, AI engineering, IT consultation, and SaaS solutions.'
            },
            {
                'name': 'Banking',
                'description': 'Retail banking institutions, digital payment infrastructure, credit, and commercial asset financing.'
            },
            {
                'name': 'Retail',
                'description': 'Omnichannel consumer retail, fast-moving consumer goods (FMCG), and nationwide physical stores.'
            },
            {
                'name': 'Food Technology',
                'description': 'Online hyperlocal food ordering, quick-commerce fulfillment, and restaurant cloud kitchens.'
            },
        ]

        category_objs = {}
        for cat_info in categories_data:
            cat, created = Category.objects.get_or_create(
                name=cat_info['name'],
                defaults={'description': cat_info['description']}
            )
            category_objs[cat.name] = cat
            status_str = "Created" if created else "Found existing"
            self.stdout.write(f"  - {status_str} Category: {cat.name}")

        # 2. Identify or verify target user
        username = options.get('username')
        user = None
        if username:
            user = User.objects.filter(username=username).first()
            if not user:
                self.stdout.write(self.style.ERROR(f"Error: Specified user '{username}' does not exist."))
                return
        else:
            # Fall back to first available user, or create demo researcher
            user = User.objects.first()
            if not user:
                # Create a sample researcher user with unusable password; admin can set password
                user = User.objects.create_user(
                    username='demo_analyst',
                    email='analyst@example.com'
                )
                user.set_unusable_password()
                user.save()
                self.stdout.write(self.style.WARNING("Created 'demo_analyst' account (unusable password by default for security)."))

        self.stdout.write(f"Assigning sample datasets to author: {user.username}")

        # 3. Create Illustrative Market Datasets
        sample_datasets = [
            {
                'title': 'Q3 Commercial EV Fleet Transition & Demand Analysis',
                'company_name': 'Tata Motors Limited',
                'category': category_objs['Automobile'],
                'industry': 'Commercial Vehicles & Clean Mobility',
                'product_service': 'Electric Medium & Heavy Duty Trucks',
                'market_price': Decimal('3250000.00'),
                'market_demand': MarketData.MarketDemand.HIGH,
                'market_size': Decimal('48500000000.00'),
                'market_growth_rate': Decimal('22.40'),
                'description': 'Illustrative research evaluating fleet electrification adoption rates across Tier 1 logistical corridors in India. Emphasizes total cost of ownership (TCO) parity, charging hub density, and government clean-freight incentives.',
                'data_source': 'Auto Industry Annual Review 2024 & Ministry of Heavy Industries Bulletin',
                'collection_date': datetime.date(2025, 9, 15),
                'visibility': MarketData.Visibility.PUBLIC,
            },
            {
                'title': 'Enterprise Generative AI & Cloud Modernization Services',
                'company_name': 'Infosys Limited',
                'category': category_objs['Information Technology'],
                'industry': 'Software & IT Consulting',
                'product_service': 'Infosys Topaz & Enterprise AI Transformation',
                'market_price': Decimal('150000.00'),
                'market_demand': MarketData.MarketDemand.HIGH,
                'market_size': Decimal('120000000000.00'),
                'market_growth_rate': Decimal('18.75'),
                'description': 'Comprehensive benchmark of enterprise generative AI services, custom large language model integrations, and cloud migration frameworks across Fortune 500 financial clients.',
                'data_source': 'Corporate Investor Presentation & SEC Form 20-F',
                'collection_date': datetime.date(2025, 10, 10),
                'visibility': MarketData.Visibility.PUBLIC,
            },
            {
                'title': 'Omnichannel Consumer Footfall & Digital Payment Integration',
                'company_name': 'Reliance Industries (Retail Division)',
                'category': category_objs['Retail'],
                'industry': 'Supermarkets & Hypermarket Retail',
                'product_service': 'JioMart & Smart Bazaar Hybrid Checkout',
                'market_price': Decimal('850.00'),
                'market_demand': MarketData.MarketDemand.MEDIUM,
                'market_size': Decimal('85000000000.00'),
                'market_growth_rate': Decimal('14.20'),
                'description': 'Evaluation of consumer basket sizes, quick fulfillment logistics, and retail floor efficiency across over 18,000 nationwide convenience and hypermarket footprints.',
                'data_source': 'Reliance Retail Annual Report FY24 & CRISIL Retail Sector Monitor',
                'collection_date': datetime.date(2025, 8, 20),
                'visibility': MarketData.Visibility.PUBLIC,
            },
            {
                'title': 'Hyperlocal Quick-Commerce Grocery & Meal Unit Economics',
                'company_name': 'Zomato Limited (Blinkit Division)',
                'category': category_objs['Food Technology'],
                'industry': 'Quick Commerce & On-Demand Delivery',
                'product_service': '10-Minute Dark Store Fulfillment',
                'market_price': Decimal('420.00'),
                'market_demand': MarketData.MarketDemand.HIGH,
                'market_size': Decimal('32000000000.00'),
                'market_growth_rate': Decimal('36.80'),
                'description': 'Assessment of dark store density, SKU velocity, order packaging times, and delivery rider economics across metropolitan high-density clusters.',
                'data_source': 'Quarterly Shareholder Letter & FoodTech Industry Disruption Index',
                'collection_date': datetime.date(2025, 11, 1),
                'visibility': MarketData.Visibility.PUBLIC,
            },
            {
                'title': 'Retail Digital Mortgages & MSME Credit Underwriting',
                'company_name': 'HDFC Bank Limited',
                'category': category_objs['Banking'],
                'industry': 'Commercial Banking & Consumer Finance',
                'product_service': 'Express Digital Home Loans & Working Capital Credit',
                'market_price': Decimal('8.65'),
                'market_demand': MarketData.MarketDemand.HIGH,
                'market_size': Decimal('950000000000.00'),
                'market_growth_rate': Decimal('16.10'),
                'description': 'Study of post-merger branch distribution, automated digital KYC approval pipelines, and credit loss provision cushions across tier-2 and tier-3 expansion hubs.',
                'data_source': 'RBI Annual Banking Statistics & HDFC Bank Q2 Investor Disclosure',
                'collection_date': datetime.date(2025, 10, 25),
                'visibility': MarketData.Visibility.PUBLIC,
            },
            {
                'title': 'Internal Strategic Pricing Study: High-Performance EV Platforms',
                'company_name': 'Tata Motors Limited',
                'category': category_objs['Automobile'],
                'industry': 'Automotive EV Technology',
                'product_service': 'Next-Gen Battery Architecture Prototype',
                'market_price': Decimal('1800000.00'),
                'market_demand': MarketData.MarketDemand.MEDIUM,
                'market_size': Decimal('15000000000.00'),
                'market_growth_rate': Decimal('28.50'),
                'description': 'CONFIDENTIAL / PRIVATE: Strategic assessment of cell chemistry cost trajectories (LFP vs NMC) and projected supply chain decoupling.',
                'data_source': 'Internal Engineering Evaluation & OEM Benchmark',
                'collection_date': datetime.date(2025, 11, 2),
                'visibility': MarketData.Visibility.PRIVATE,
            }
        ]

        created_count = 0
        for ds in sample_datasets:
            dataset, created = MarketData.objects.get_or_create(
                title=ds['title'],
                company_name=ds['company_name'],
                defaults={
                    'category': ds['category'],
                    'industry': ds['industry'],
                    'product_service': ds['product_service'],
                    'market_price': ds['market_price'],
                    'market_demand': ds['market_demand'],
                    'market_size': ds['market_size'],
                    'market_growth_rate': ds['market_growth_rate'],
                    'description': ds['description'],
                    'data_source': ds['data_source'],
                    'collection_date': ds['collection_date'],
                    'visibility': ds['visibility'],
                    'created_by': user,
                }
            )
            if created:
                created_count += 1
                ActivityLog.objects.create(
                    user=user,
                    action='Sample Data Imported',
                    dataset=dataset,
                    details=f"Imported illustrative sample dataset '{dataset.title}'"
                )
                self.stdout.write(f"  + Added Dataset: '{dataset.title}' ({dataset.company_name}) [{dataset.visibility}]")
            else:
                self.stdout.write(f"  * Already present: '{dataset.title}'")

        self.stdout.write(self.style.SUCCESS(f"\nSuccessfully loaded sample data! Total new datasets: {created_count}"))
        self.stdout.write(self.style.NOTICE("Note: All financial figures are illustrative academic sample values."))

