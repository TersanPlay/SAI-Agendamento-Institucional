"""
Data encryption utilities for protecting sensitive information
"""
import base64
import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
import logging

logger = logging.getLogger(__name__)


class DataEncryption:
    """
    Utility class for encrypting and decrypting sensitive data
    """
    
    def __init__(self):
        self.key = self._get_or_create_key()
        self.cipher = Fernet(self.key)
    
    def _get_or_create_key(self):
        """Get or create encryption key"""
        # In production, this should be stored securely (e.g., environment variable)
        secret_key = getattr(settings, 'SECRET_KEY', 'default-secret-key')
        
        # Derive a key from SECRET_KEY
        password = secret_key.encode()
        salt = b'eventosys_salt'  # In production, use a random salt stored securely
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key
    
    def encrypt(self, data):
        """
        Encrypt sensitive data
        
        Args:
            data (str): Data to encrypt
            
        Returns:
            str: Encrypted data (base64 encoded)
        """
        if not data:
            return data
        
        try:
            encrypted_data = self.cipher.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted_data).decode()
        except Exception as e:
            logger.error(f"Encryption error: {str(e)}")
            raise
    
    def decrypt(self, encrypted_data):
        """
        Decrypt sensitive data
        
        Args:
            encrypted_data (str): Base64 encoded encrypted data
            
        Returns:
            str: Decrypted data
        """
        if not encrypted_data:
            return encrypted_data
        
        try:
            decoded_data = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = self.cipher.decrypt(decoded_data)
            return decrypted_data.decode()
        except Exception as e:
            logger.error(f"Decryption error: {str(e)}")
            raise
    
    def hash_sensitive_data(self, data, salt=None):
        """
        Create a hash of sensitive data for verification purposes
        
        Args:
            data (str): Data to hash
            salt (str, optional): Salt for hashing
            
        Returns:
            str: Hashed data
        """
        if not data:
            return data
        
        if salt is None:
            salt = settings.SECRET_KEY[:16]  # Use part of SECRET_KEY as salt
        
        # Create hash
        hasher = hashlib.pbkdf2_hmac('sha256', 
                                   data.encode('utf-8'), 
                                   salt.encode('utf-8'), 
                                   100000)
        
        return base64.urlsafe_b64encode(hasher).decode()


class SecureFileHandler:
    """
    Handler for secure file operations
    """
    
    def __init__(self):
        self.encryption = DataEncryption()
    
    def secure_file_upload(self, file_obj, allowed_extensions=None, max_size=None):
        """
        Securely handle file uploads with validation
        
        Args:
            file_obj: Uploaded file object
            allowed_extensions (list): List of allowed file extensions
            max_size (int): Maximum file size in bytes
            
        Returns:
            dict: File validation results
        """
        if allowed_extensions is None:
            allowed_extensions = ['.pdf', '.doc', '.docx', '.txt', '.jpg', '.png', '.jpeg']
        
        if max_size is None:
            max_size = 10 * 1024 * 1024  # 10MB default
        
        results = {
            'valid': True,
            'errors': [],
            'file_info': {}
        }
        
        # Check file size
        if file_obj.size > max_size:
            results['valid'] = False
            results['errors'].append(f'File size exceeds maximum of {max_size // (1024*1024)}MB')
        
        # Check file extension
        file_extension = self._get_file_extension(file_obj.name)
        if file_extension.lower() not in allowed_extensions:
            results['valid'] = False
            results['errors'].append(f'File type {file_extension} not allowed')
        
        # Scan for malicious content (basic checks)
        try:
            content_sample = file_obj.read(1024)  # Read first 1KB
            file_obj.seek(0)  # Reset file pointer
            
            # Check for suspicious patterns
            suspicious_patterns = [b'<script', b'javascript:', b'<?php', b'exec(']
            for pattern in suspicious_patterns:
                if pattern in content_sample.lower():
                    results['valid'] = False
                    results['errors'].append('File contains suspicious content')
                    break
        
        except Exception as e:
            logger.warning(f"Could not scan file content: {str(e)}")
        
        # Generate secure filename
        if results['valid']:
            secure_filename = self._generate_secure_filename(file_obj.name)
            results['file_info'] = {
                'original_name': file_obj.name,
                'secure_name': secure_filename,
                'size': file_obj.size,
                'extension': file_extension
            }
        
        return results
    
    def _get_file_extension(self, filename):
        """Extract file extension"""
        return '.' + filename.split('.')[-1] if '.' in filename else ''
    
    def _generate_secure_filename(self, original_filename):
        """Generate a secure filename"""
        import uuid
        import os
        
        # Get file extension
        _, ext = os.path.splitext(original_filename)
        
        # Generate unique filename
        secure_name = f"{uuid.uuid4().hex}{ext}"
        
        return secure_name


class AuditLogger:
    """
    Enhanced audit logging for security events
    """
    
    @staticmethod
    def log_security_event(user, event_type, details, ip_address=None, user_agent=None):
        """
        Log security-related events
        
        Args:
            user: User object or username
            event_type (str): Type of security event
            details (dict): Event details
            ip_address (str): Client IP address
            user_agent (str): Client user agent
        """
        try:
            from accounts.models import AccessLog
            
            # Convert user to username if it's a User object
            username = user.username if hasattr(user, 'username') else str(user)
            
            # Create detailed log message
            log_message = f"Security Event: {event_type}"
            if details:
                log_message += f" - Details: {details}"
            
            # Log to database
            if hasattr(user, 'username'):  # It's a User object
                AccessLog.objects.create(
                    user=user,
                    action=f"security_{event_type}",
                    resource="security",
                    ip_address=ip_address or "0.0.0.0",
                    user_agent=user_agent or "Unknown",
                    success=True
                )
            
            # Log to file
            logger.warning(f"SECURITY: {username} - {log_message} from IP {ip_address}")
            
        except Exception as e:
            logger.error(f"Failed to log security event: {str(e)}")
    
    @staticmethod
    def log_data_access(user, data_type, action, record_id=None):
        """
        Log access to sensitive data
        
        Args:
            user: User object
            data_type (str): Type of data accessed
            action (str): Action performed
            record_id: ID of the record accessed
        """
        try:
            details = {
                'data_type': data_type,
                'action': action,
                'record_id': record_id,
                'timestamp': timezone.now().isoformat()
            }
            
            AuditLogger.log_security_event(
                user=user,
                event_type='data_access',
                details=details
            )
            
        except Exception as e:
            logger.error(f"Failed to log data access: {str(e)}")


# Initialize global instances
encryption = DataEncryption()
file_handler = SecureFileHandler()


def encrypt_field(value):
    """Convenience function to encrypt a field value"""
    return encryption.encrypt(value) if value else value


def decrypt_field(value):
    """Convenience function to decrypt a field value"""
    return encryption.decrypt(value) if value else value


def hash_field(value):
    """Convenience function to hash a field value"""
    return encryption.hash_sensitive_data(value) if value else value