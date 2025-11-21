# Medical Imaging HIPAA Compliance

This document outlines the HIPAA compliance measures implemented for medical imaging storage and processing in MemoryGuard.

## Overview

The medical imaging system handles Protected Health Information (PHI) in the form of DICOM files containing brain MRI scans. All imaging data is handled in accordance with HIPAA Security Rule requirements.

## Security Measures

### 1. Encryption at Rest

**Implementation**: `app/services/imaging_service.py`

- All DICOM files are encrypted using Fernet (symmetric encryption) before storage
- Encryption key is stored securely in environment variables
- Each file is encrypted individually with AES-128 in CBC mode
- Encrypted files cannot be read without the encryption key

```python
# Encryption process
encrypted_content = self.cipher.encrypt(file_content)
file_path.write_bytes(encrypted_content)
```

### 2. Encryption in Transit

**Implementation**: API endpoints use HTTPS/TLS

- All API communications use TLS 1.3
- File uploads are transmitted over encrypted connections
- No PHI is transmitted in plain text

### 3. Access Controls

**Implementation**: `app/api/v1/imaging.py`

- Authentication required for all imaging endpoints
- Users can only access their own imaging studies
- Caregivers can access patient data only with explicit permission
- Role-based access control (RBAC) enforced at API level

```python
# Authorization check
if str(current_user.id) != str(user_id):
    if str(current_user.id) not in target_user.caregivers:
        raise HTTPException(status_code=403, detail="Not authorized")
```

### 4. Audit Logging

**Implementation**: Database tracking and application logs

- All imaging uploads are logged with timestamps
- Access to imaging data is tracked in database
- Processing status changes are logged
- Failed access attempts are logged

### 5. Data Integrity

**Implementation**: File hashing and validation

- MD5 hashes generated for uploaded files
- File integrity verified during processing
- Corrupted files are detected and rejected
- Processing errors are logged and reported

### 6. Secure File Storage

**Implementation**: Organized directory structure

- Files stored in user-specific directories
- Unique filenames prevent collisions
- File paths are not predictable
- Storage location configurable via environment variables

```
data/imaging/
├── {user_id_1}/
│   ├── 20251117_120000_abc123_scan.dcm
│   └── 20251117_130000_def456_scan.dcm
└── {user_id_2}/
    └── 20251117_140000_ghi789_scan.dcm
```

### 7. Data Minimization

**Implementation**: Metadata extraction and anonymization

- Only necessary data is extracted from DICOM files
- Patient identifiers are not stored in analysis results
- Volumetric measurements stored separately from raw files
- Original files can be deleted after processing if needed

### 8. Secure Deletion

**Implementation**: File system operations

- Files can be securely deleted when no longer needed
- Encrypted files overwritten before deletion
- Database records maintain audit trail even after file deletion

## Configuration

### Environment Variables

Required environment variables for HIPAA-compliant operation:

```bash
# Imaging storage path (should be on encrypted volume)
IMAGING_STORAGE_PATH=/secure/encrypted/volume/imaging

# Encryption key (32-byte base64-encoded key)
IMAGING_ENCRYPTION_KEY=your-secure-encryption-key-here

# Maximum file size (bytes)
IMAGING_MAX_FILE_SIZE=104857600  # 100MB
```

### Generating Encryption Key

```python
from cryptography.fernet import Fernet

# Generate a new encryption key
key = Fernet.generate_key()
print(key.decode())  # Use this as IMAGING_ENCRYPTION_KEY
```

## Database Schema

### medical_imaging Table

```sql
CREATE TABLE medical_imaging (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id),
    file_path VARCHAR NOT NULL,  -- Path to encrypted file
    file_size FLOAT NOT NULL,
    status VARCHAR NOT NULL,
    -- Volumetric measurements (de-identified)
    hippocampal_volume_total FLOAT,
    cortical_thickness_mean FLOAT,
    -- ... other measurements
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

-- Indexes for performance
CREATE INDEX idx_medical_imaging_user_id ON medical_imaging(user_id);
CREATE INDEX idx_medical_imaging_status ON medical_imaging(status);
```

## API Endpoints

### POST /api/v1/imaging/upload

- **Authentication**: Required
- **Authorization**: User can only upload their own scans
- **Encryption**: File encrypted before storage
- **Validation**: File type and size validated
- **Audit**: Upload logged with timestamp

### GET /api/v1/imaging/{imaging_id}/analysis

- **Authentication**: Required
- **Authorization**: User can only access their own data
- **Data**: Returns de-identified analysis results
- **Audit**: Access logged

### GET /api/v1/imaging/user/{user_id}

- **Authentication**: Required
- **Authorization**: User or authorized caregiver only
- **Data**: Returns list of imaging studies
- **Audit**: Access logged

## Compliance Checklist

- [x] Encryption at rest (AES-128)
- [x] Encryption in transit (TLS 1.3)
- [x] Access controls (authentication + authorization)
- [x] Audit logging (database + application logs)
- [x] Data integrity (file hashing)
- [x] Secure storage (encrypted files)
- [x] Data minimization (extract only necessary data)
- [x] Secure deletion capability
- [x] Role-based access control
- [x] Session management
- [x] Error handling (no PHI in error messages)
- [x] Backup procedures (encrypted backups)

## Best Practices

### For Deployment

1. **Use encrypted volumes** for imaging storage
2. **Rotate encryption keys** periodically
3. **Monitor access logs** for suspicious activity
4. **Implement backup procedures** with encryption
5. **Use secure key management** (e.g., AWS KMS, HashiCorp Vault)
6. **Enable database encryption** at rest
7. **Configure firewall rules** to restrict access
8. **Implement rate limiting** to prevent abuse

### For Development

1. **Never commit encryption keys** to version control
2. **Use separate keys** for dev/staging/production
3. **Test with synthetic data** when possible
4. **Follow secure coding practices**
5. **Conduct regular security audits**
6. **Keep dependencies updated**

## Incident Response

In case of a security incident:

1. **Immediately revoke** compromised credentials
2. **Rotate encryption keys** if compromised
3. **Review audit logs** for unauthorized access
4. **Notify affected users** as required by HIPAA
5. **Document the incident** for compliance
6. **Implement corrective measures**

## References

- [HIPAA Security Rule](https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [DICOM Security](https://www.dicomstandard.org/current)

## Contact

For security concerns or questions about HIPAA compliance, contact the security team.
