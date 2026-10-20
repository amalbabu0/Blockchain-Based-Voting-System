from django.core.management.base import BaseCommand
from voteA.models import Student, Staff, admin_log


class Command(BaseCommand):
    help = "Seed demo admin, staff, and student accounts for local testing."

    def handle(self, *args, **options):
        admin, _ = admin_log.objects.get_or_create(
            email='admin@demo.com',
            defaults={'password': 'admin123'},
        )

        hod, _ = Staff.objects.get_or_create(
            email='hod@demo.com',
            defaults={
                'name': 'Demo HOD',
                'id_no': 1001,
                'mob': 9000000001,
                'department': 'CSE',
                'designation': 'HOD',
                'password': 'hod12345',
                'status': 'ACCEPTED',
            },
        )

        staff, _ = Staff.objects.get_or_create(
            email='staff@demo.com',
            defaults={
                'name': 'Demo Staff',
                'id_no': 1002,
                'mob': 9000000002,
                'department': 'CSE',
                'designation': 'STAFF',
                'password': 'staff123',
                'status': 'ACCEPTED',
            },
        )

        voter, _ = Student.objects.get_or_create(
            email='student1@demo.com',
            defaults={
                'name': 'Demo Voter',
                'ad_no': 2001,
                'mob': 9000000003,
                'department': 'CSE',
                'sex': 'F',
                'password': 'stud1234',
                'status': 'ACCEPTED',
                'type': 'STUDENT',
            },
        )

        candidate, _ = Student.objects.get_or_create(
            email='student2@demo.com',
            defaults={
                'name': 'Demo Candidate',
                'ad_no': 2002,
                'mob': 9000000004,
                'department': 'CSE',
                'sex': 'M',
                'password': 'stud5678',
                'status': 'ACCEPTED',
                'type': 'CANDIDATE',
            },
        )

        self.stdout.write(self.style.SUCCESS('Demo accounts ready:'))
        self.stdout.write(f'  admin:     {admin.email} / admin123')
        self.stdout.write(f'  HOD staff: {hod.email} / hod12345')
        self.stdout.write(f'  staff:     {staff.email} / staff123')
        self.stdout.write(f'  voter:     {voter.email} / stud1234')
        self.stdout.write(f'  candidate: {candidate.email} / stud5678')
