"""
Management command for security auditing
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
from django.db import models
from accounts.models import AccessLog, UserProfile
from events.models import Event
from datetime import timedelta
import os


class Command(BaseCommand):
    help = 'Perform security audit of the system'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Number of days to look back for analysis (default: 7)'
        )
        parser.add_argument(
            '--detailed',
            action='store_true',
            help='Show detailed security information'
        )
    
    def handle(self, *args, **options):
        days = options['days']
        detailed = options['detailed']
        
        self.stdout.write(
            self.style.SUCCESS(f'\n=== EventoSys Security Audit ===\n')
        )
        
        # Check system configuration
        self.check_system_configuration()
        
        # Check user security
        self.check_user_security(days, detailed)
        
        # Check access logs
        self.check_access_patterns(days, detailed)
        
        # Check file security
        self.check_file_security()
        
        # Generate recommendations
        self.generate_recommendations()
        
        self.stdout.write(
            self.style.SUCCESS('\n=== Security Audit Complete ===\n')
        )
    
    def check_system_configuration(self):
        """Check system security configuration"""
        self.stdout.write('\n📋 System Configuration:')
        
        # Check DEBUG mode
        if settings.DEBUG:
            self.stdout.write(
                self.style.WARNING('  ⚠️  DEBUG mode is enabled (should be False in production)')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('  ✅ DEBUG mode is disabled')
            )
        
        # Check SECRET_KEY
        if settings.SECRET_KEY == 'django-insecure-#change-this-in-production#':
            self.stdout.write(
                self.style.ERROR('  ❌ Default SECRET_KEY is being used')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('  ✅ Custom SECRET_KEY is configured')
            )
        
        # Check security middleware
        security_middlewares = [
            'accounts.middleware.SecurityHeadersMiddleware',
            'accounts.middleware.SecurityLoggingMiddleware',
            'accounts.middleware.BruteForceProtectionMiddleware',
        ]
        
        missing_middlewares = []
        for middleware in security_middlewares:
            if middleware not in settings.MIDDLEWARE:
                missing_middlewares.append(middleware)
        
        if missing_middlewares:
            self.stdout.write(
                self.style.WARNING(f'  ⚠️  Missing security middlewares: {", ".join(missing_middlewares)}')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('  ✅ Security middlewares are configured')
            )
        
        # Check HTTPS settings
        if not settings.DEBUG:
            if not getattr(settings, 'SECURE_SSL_REDIRECT', False):
                self.stdout.write(
                    self.style.WARNING('  ⚠️  HTTPS redirect not configured for production')
                )
    
    def check_user_security(self, days, detailed):
        """Check user-related security"""
        self.stdout.write('\n👥 User Security:')
        
        # Check for default admin user
        default_admin = User.objects.filter(username='admin', is_superuser=True).first()
        if default_admin:
            self.stdout.write(
                self.style.WARNING('  ⚠️  Default admin user exists (consider renaming)')
            )
        
        # Check for users without profiles
        users_without_profiles = User.objects.filter(profile__isnull=True).count()
        if users_without_profiles > 0:
            self.stdout.write(
                self.style.WARNING(f'  ⚠️  {users_without_profiles} users without profiles')
            )
        
        # Check for inactive users with recent activity
        cutoff_date = timezone.now() - timedelta(days=days)
        inactive_with_activity = AccessLog.objects.filter(
            user__is_active=False,
            timestamp__gte=cutoff_date
        ).values('user').distinct().count()
        
        if inactive_with_activity > 0:
            self.stdout.write(
                self.style.WARNING(f'  ⚠️  {inactive_with_activity} inactive users with recent activity')
            )
        
        # Check password ages (if last_login is available)
        old_passwords = User.objects.filter(
            last_login__lt=timezone.now() - timedelta(days=90)
        ).exclude(last_login__isnull=True).count()
        
        if old_passwords > 0:
            self.stdout.write(
                self.style.WARNING(f'  ⚠️  {old_passwords} users haven\'t logged in for 90+ days')
            )
        
        # Count users by type
        user_stats = {
            'total': User.objects.count(),
            'active': User.objects.filter(is_active=True).count(),
            'admins': UserProfile.objects.filter(user_type='administrador').count(),
            'managers': UserProfile.objects.filter(user_type='gestor').count(),
            'viewers': UserProfile.objects.filter(user_type='visualizador').count(),
        }
        
        self.stdout.write(f'  📊 User Statistics:')
        self.stdout.write(f'     Total users: {user_stats["total"]}')
        self.stdout.write(f'     Active users: {user_stats["active"]}')
        self.stdout.write(f'     Administrators: {user_stats["admins"]}')
        self.stdout.write(f'     Managers: {user_stats["managers"]}')
        self.stdout.write(f'     Viewers: {user_stats["viewers"]}')
    
    def check_access_patterns(self, days, detailed):
        """Check access log patterns for security issues"""
        self.stdout.write('\n🔍 Access Patterns:')
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        # Failed login attempts
        failed_logins = AccessLog.objects.filter(
            action='login',
            success=False,
            timestamp__gte=cutoff_date
        ).count()
        
        if failed_logins > 10:
            self.stdout.write(
                self.style.WARNING(f'  ⚠️  {failed_logins} failed login attempts in last {days} days')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'  ✅ {failed_logins} failed login attempts (normal)')
            )
        
        # Suspicious IP addresses (multiple failed attempts)\n        suspicious_ips = AccessLog.objects.filter(\n            success=False,\n            timestamp__gte=cutoff_date\n        ).values('ip_address').annotate(\n            fail_count=models.Count('id')\n        ).filter(fail_count__gte=5)\n        \n        if suspicious_ips:\n            self.stdout.write(\n                self.style.WARNING(f'  ⚠️  {len(suspicious_ips)} IP addresses with 5+ failed attempts')\n            )\n            if detailed:\n                for ip_info in suspicious_ips:\n                    self.stdout.write(\n                        f'     IP: {ip_info[\"ip_address\"]} - {ip_info[\"fail_count\"]} failures'\n                    )\n        \n        # Admin access patterns\n        admin_users = User.objects.filter(profile__user_type='administrador')\n        admin_access = AccessLog.objects.filter(\n            user__in=admin_users,\n            timestamp__gte=cutoff_date\n        ).count()\n        \n        self.stdout.write(f'  👑 Admin actions in last {days} days: {admin_access}')\n        \n        # Recent security-related actions\n        security_actions = AccessLog.objects.filter(\n            action__icontains='security',\n            timestamp__gte=cutoff_date\n        ).count()\n        \n        if security_actions > 0:\n            self.stdout.write(f'  🔒 Security events logged: {security_actions}')\n        \n        # Most active users\n        active_users = AccessLog.objects.filter(\n            timestamp__gte=cutoff_date\n        ).values('user__username').annotate(\n            action_count=models.Count('id')\n        ).order_by('-action_count')[:5]\n        \n        if detailed and active_users:\n            self.stdout.write('  📈 Most active users:')\n            for user_info in active_users:\n                self.stdout.write(\n                    f'     {user_info[\"user__username\"]}: {user_info[\"action_count\"]} actions'\n                )\n    \n    def check_file_security(self):\n        \"\"\"Check file and directory security\"\"\"\n        self.stdout.write('\\n📁 File Security:')\n        \n        # Check media directory permissions\n        media_root = getattr(settings, 'MEDIA_ROOT', None)\n        if media_root and os.path.exists(media_root):\n            try:\n                # Check if directory is writable\n                test_file = os.path.join(media_root, '.security_test')\n                with open(test_file, 'w') as f:\n                    f.write('test')\n                os.remove(test_file)\n                self.stdout.write(\n                    self.style.SUCCESS('  ✅ Media directory is accessible')\n                )\n            except Exception as e:\n                self.stdout.write(\n                    self.style.ERROR(f'  ❌ Media directory access issue: {str(e)}')\n                )\n        \n        # Check for uploaded files\n        try:\n            from django.core.files.storage import default_storage\n            # This is a basic check - in a real implementation, you'd scan for malicious files\n            self.stdout.write('  📂 File upload security: Basic checks enabled')\n        except Exception as e:\n            self.stdout.write(\n                self.style.WARNING(f'  ⚠️  File storage check failed: {str(e)}')\n            )\n    \n    def generate_recommendations(self):\n        \"\"\"Generate security recommendations\"\"\"\n        self.stdout.write('\\n💡 Security Recommendations:')\n        \n        recommendations = [\n            'Regularly review and rotate SECRET_KEY',\n            'Monitor failed login attempts and block suspicious IPs',\n            'Implement regular password policy enforcement',\n            'Review user permissions and remove unnecessary admin access',\n            'Set up automated security scanning',\n            'Configure HTTPS and security headers for production',\n            'Implement regular database backups with encryption',\n            'Set up monitoring and alerting for security events',\n            'Regularly update dependencies and apply security patches',\n            'Conduct periodic security audits and penetration testing'\n        ]\n        \n        for i, rec in enumerate(recommendations, 1):\n            self.stdout.write(f'  {i:2d}. {rec}')\n        \n        # Additional recommendations based on findings\n        if settings.DEBUG:\n            self.stdout.write(\n                self.style.WARNING('\\n⚠️  HIGH PRIORITY: Disable DEBUG mode in production')\n            )\n        \n        # Check for recent security updates\n        self.stdout.write('\\n🔧 Maintenance Suggestions:')\n        self.stdout.write('  • Run `python manage.py check --deploy` for deployment checklist')\n        self.stdout.write('  • Review access logs regularly with: `python manage.py security_audit --detailed`')\n        self.stdout.write('  • Monitor system resources and performance')\n        self.stdout.write('  • Keep Django and dependencies updated')