from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from accounts.models import User, PoliceOfficer, Reporter
from locations.models import Location
from cases.models import MissingPersonCase, PriorityTracker
from verification.models import VerificationCheck
from sightings.models import SightingTip
from notifications.models import Notification

class Command(BaseCommand):
    help = "Seeds database with comprehensive demo data for আপনজন (Aponjon) platform"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Setting up আপনজন (Aponjon) demo database..."))

        # 1. Create Locations
        loc_dhanmondi, _ = Location.objects.get_or_create(
            area="Dhanmondi 27",
            thana="Dhanmondi",
            city="Dhaka",
            defaults={
                "address": "House 12, Road 27, Dhanmondi",
                "postalCode": "1209",
                "latitude": 23.7530,
                "longitude": 90.3750
            }
        )

        loc_mirpur, _ = Location.objects.get_or_create(
            area="Mirpur 10 Circle",
            thana="Mirpur",
            city="Dhaka",
            defaults={
                "address": "Section 10, Block C, Mirpur",
                "postalCode": "1216",
                "latitude": 23.8070,
                "longitude": 90.3680
            }
        )

        loc_uttara, _ = Location.objects.get_or_create(
            area="Uttara Sector 3",
            thana="Uttara",
            city="Dhaka",
            defaults={
                "address": "Road 7, Sector 3, Uttara",
                "postalCode": "1230",
                "latitude": 23.8690,
                "longitude": 90.3990
            }
        )

        # 2. Create Users
        # Default Super Admin: Shawon / 47K3RWJ6
        admin_user, created = User.objects.get_or_create(
            username="Shawon",
            defaults={
                "first_name": "Sumsodduha",
                "last_name": "Shawon",
                "email": "shawon@aponjon.org",
                "phone": "+880 1700-000000",
                "role": "ADMIN",
                "is_staff": True,
                "is_superuser": True
            }
        )
        admin_user.set_password("47K3RWJ6")
        admin_user.role = "ADMIN"
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()

        # Police Officer 1 (Dhanmondi)
        officer_user, created = User.objects.get_or_create(
            username="officer_rahman",
            defaults={
                "first_name": "Tanvir",
                "last_name": "Rahman",
                "email": "tanvir.rahman@police.gov.bd",
                "phone": "+880 1711-223344",
                "role": "POLICE",
                "is_staff": True
            }
        )
        if created:
            officer_user.set_password("police123")
            officer_user.save()

        officer_profile, _ = PoliceOfficer.objects.get_or_create(
            user=officer_user,
            defaults={
                "badgeNumber": "BP-849102",
                "stationName": "Dhanmondi Model Thana",
                "jurisdiction": "Dhanmondi, Kalabagan, Sobhanbagh",
                "location": loc_dhanmondi,
                "isVerified": True
            }
        )

        # Police Officer 2 (Mirpur)
        officer2_user, created = User.objects.get_or_create(
            username="officer_hossain",
            defaults={
                "first_name": "Arif",
                "last_name": "Hossain",
                "email": "arif.hossain@police.gov.bd",
                "phone": "+880 1819-334455",
                "role": "POLICE",
                "is_staff": True
            }
        )
        if created:
            officer2_user.set_password("police123")
            officer2_user.save()

        officer2_profile, _ = PoliceOfficer.objects.get_or_create(
            user=officer2_user,
            defaults={
                "badgeNumber": "BP-992145",
                "stationName": "Mirpur Model Thana",
                "jurisdiction": "Mirpur, Pallabi, Kazipara",
                "location": loc_mirpur,
                "isVerified": True
            }
        )

        # Reporter 1 (Demo Family Reporter)
        shawon_user, created = User.objects.get_or_create(
            username="shawon_reporter",
            defaults={
                "first_name": "পরিবার",
                "last_name": "রিপোর্টার",
                "email": "reporter@example.com",
                "phone": "+880 1680-123456",
                "role": "REPORTER"
            }
        )
        if created:
            shawon_user.set_password("reporter123")
            shawon_user.save()

        shawon_reporter, _ = Reporter.objects.get_or_create(
            user=shawon_user,
            defaults={
                "location": loc_dhanmondi,
                "reporterType": "Family Member",
                "relation": "পরিবারের সদস্য",
                "nidNumber": "19982692019482",
                "isVerified": True
            }
        )

        # Reporter 2 (Demo Family Reporter 2)
        sufal_user, created = User.objects.get_or_create(
            username="sufal_reporter",
            defaults={
                "first_name": "পরিবার",
                "last_name": "রিপোর্টার ২",
                "email": "reporter2@example.com",
                "phone": "+880 1799-654321",
                "role": "REPORTER"
            }
        )
        if created:
            sufal_user.set_password("reporter123")
            sufal_user.save()

        sufal_reporter, _ = Reporter.objects.get_or_create(
            user=sufal_user,
            defaults={
                "location": loc_mirpur,
                "reporterType": "Family Member",
                "relation": "সন্তান",
                "nidNumber": "20015592817294",
                "isVerified": True
            }
        )

        # Citizen / Volunteer (Demo Citizen)
        junayed_user, created = User.objects.get_or_create(
            username="junayed_citizen",
            defaults={
                "first_name": "সচেতন",
                "last_name": "নাগরিক",
                "email": "citizen@example.com",
                "phone": "+880 1552-112233",
                "role": "CITIZEN"
            }
        )
        if created:
            junayed_user.set_password("citizen123")
            junayed_user.save()

        # 3. Create Missing Person Cases
        # Case 1: Child missing in Dhanmondi (CRITICAL - 7yo Bangladeshi boy)
        now = timezone.now()
        case1, created1 = MissingPersonCase.objects.get_or_create(
            fullName="Rayan Ahmed",
            reporter=shawon_reporter,
            defaults={
                "age": 7,
                "gender": "Male",
                "photoURL": "/static/images/cases/rayan_ahmed.jpg",
                "lastSeenTime": now - timedelta(hours=6),
                "caseStatus": "SEARCHING",
                "clothingDetails": "কালো টি-শার্ট (বুকে 'WHERE ARE WE?' লেখা), হাফ প্যান্ট।",
                "medicalConditions": "Non-verbal autistic child, responds to the name 'Rayan', sensitive to sirens.",
                "identifyingMarks": "Small mole under right eye.",
                "height": "3 ft 8 in",
                "location": loc_dhanmondi,
                "isArchived": False
            }
        )
        if not created1:
            case1.photoURL = "/static/images/cases/rayan_ahmed.jpg"
            case1.clothingDetails = "কালো টি-শার্ট (বুকে 'WHERE ARE WE?' লেখা), হাফ প্যান্ট।"
            case1.save()

        tracker1, _ = PriorityTracker.objects.get_or_create(case=case1)
        tracker1.urgencyLevel = 'CRITICAL'
        tracker1.save()

        verif1, _ = VerificationCheck.objects.get_or_create(
            case=case1,
            defaults={
                "officer": officer_profile,
                "gdNumber": "GD-2026-DHAN-4019",
                "verifyStatus": "APPROVED",
                "policeRemarks": "Identity confirmed by family with birth certificate and CC camera footage near Rabindra Sarobar.",
                "verifiedAt": now - timedelta(hours=5)
            }
        )

        # Case 2: Elderly Alzheimer's Patient in Mirpur (CRITICAL - 74yo Bangladeshi grandfather)
        case2, created2 = MissingPersonCase.objects.get_or_create(
            fullName="Haji Abdul Karim",
            reporter=sufal_reporter,
            defaults={
                "age": 74,
                "gender": "Male",
                "photoURL": "/static/images/cases/haji_abdul_karim.jpg",
                "lastSeenTime": now - timedelta(hours=15),
                "caseStatus": "SIGHTED",
                "clothingDetails": "বাদামী রঙের লম্বা পাঞ্জাবি, মাথায় সাদা টুপি, মুখে শুভ্র দীর্ঘ দাড়ি ও হাতে বাঁশের লাঠি।",
                "medicalConditions": "Diagnosed with Alzheimer's disease and acute memory loss. In urgent need of daily cardiac medications.",
                "identifyingMarks": "White beard, gold frame spectacles.",
                "height": "5 ft 6 in",
                "location": loc_mirpur,
                "isArchived": False
            }
        )
        if not created2:
            case2.photoURL = "/static/images/cases/haji_abdul_karim.jpg"
            case2.clothingDetails = "বাদামী রঙের লম্বা পাঞ্জাবি, মাথায় সাদা টুপি, মুখে শুভ্র দীর্ঘ দাড়ি ও হাতে বাঁশের লাঠি।"
            case2.save()
        tracker2, _ = PriorityTracker.objects.get_or_create(case=case2)
        tracker2.urgencyLevel = 'CRITICAL'
        tracker2.save()

        verif2, _ = VerificationCheck.objects.get_or_create(
            case=case2,
            defaults={
                "officer": officer2_profile,
                "gdNumber": "GD-2026-MIRP-8821",
                "verifyStatus": "APPROVED",
                "policeRemarks": "NID verified. Last seen walking towards Mirpur 2 intersection at 7 AM.",
                "verifiedAt": now - timedelta(hours=14)
            }
        )

        # Sighting Tip for Case 2
        tip1, _ = SightingTip.objects.get_or_create(
            case=case2,
            sightingDescription="Saw an elderly uncle in white Punjabi sitting on a wooden bench beside Mama Tea Stall near Mirpur 2 stadium gate. Looked confused about his address.",
            defaults={
                "tipster_name": "Junayed Shahriar",
                "tipster_phone": "+880 1552-112233",
                "sightingTime": now - timedelta(hours=2),
                "location": loc_mirpur,
                "status": "CREDIBLE"
            }
        )

        # Case 3: Reunited Case (Demonstrating Auto-Archive & Privacy Protection)
        case3, created3 = MissingPersonCase.objects.get_or_create(
            fullName="Nusrat Jahan",
            reporter=shawon_reporter,
            defaults={
                "age": 16,
                "gender": "Female",
                "photoURL": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=500&auto=format&fit=crop&q=80",
                "lastSeenTime": now - timedelta(days=2),
                "caseStatus": "REUNITED",
                "clothingDetails": "Black abaya and grey scarf.",
                "medicalConditions": "Asthma.",
                "location": loc_uttara,
                "isArchived": True # Auto-archived to protect privacy!
            }
        )
        tracker3, _ = PriorityTracker.objects.get_or_create(case=case3)
        tracker3.urgencyLevel = 'STANDARD'
        tracker3.save()

        verif3, _ = VerificationCheck.objects.get_or_create(
            case=case3,
            defaults={
                "officer": officer_profile,
                "gdNumber": "GD-2026-UTTA-1044",
                "verifyStatus": "APPROVED",
                "policeRemarks": "Safely traced in Tongi and handed over to family in good health.",
                "verifiedAt": now - timedelta(days=1)
            }
        )

        # 4. Create Notifications
        Notification.objects.get_or_create(
            recipient=junayed_user,
            case=case1,
            title="CRITICAL ALERT: Missing 7yo Child in Dhanmondi",
            defaults={
                "message": "Verified Alert (GD-2026-DHAN-4019): Rayan Ahmed, 7yo boy missing near Dhanmondi Lake. Please keep an eye out and report any sighting.",
                "notificationType": "URGENT_ALERT",
                "priorityLevel": "CRITICAL",
                "isRead": False
            }
        )

        Notification.objects.get_or_create(
            recipient=sufal_user,
            case=case2,
            title="Credible Sighting Tip Received!",
            defaults={
                "message": "A community member reported spotting Haji Abdul Karim near Mirpur 2 stadium gate. Investigating officers are en route.",
                "notificationType": "SIGHTING_TIP",
                "priorityLevel": "CRITICAL",
                "isRead": False
            }
        )

        self.stdout.write(self.style.SUCCESS("✓ Demo data successfully generated for আপনজন (Aponjon)!"))
        self.stdout.write(self.style.SUCCESS("  - Admin: admin / admin123"))
        self.stdout.write(self.style.SUCCESS("  - Police: officer_rahman / police123 (Dhanmondi Thana)"))
        self.stdout.write(self.style.SUCCESS("  - Police: officer_hossain / police123 (Mirpur Thana)"))
        self.stdout.write(self.style.SUCCESS("  - Reporter: shawon_reporter / reporter123"))
        self.stdout.write(self.style.SUCCESS("  - Reporter: sufal_reporter / reporter123"))
        self.stdout.write(self.style.SUCCESS("  - Citizen: junayed_citizen / citizen123"))
