from src.models import CardDAVContactResponse
from typing import List
import re
from datetime import datetime

def parse_vcf(vcf_content: str) -> CardDAVContactResponse:
    """
    Parse a vCard/CardDAV format contact and extract genealogical relevant fields.
    
    vCard 3.0 / 4.0 format example:
    BEGIN:VCARD
    VERSION:3.0
    FN:John Doe
    N:Doe;John;;;
    BDAY:1980-01-15
    EMAIL:john@example.com
    ...
    END:VCARD
    """
    
    lines = vcf_content.strip().split('\n')
    
    contact_data = {
        'name': '',
        'given_names': None,
        'surname': None,
        'email': None,
        'phone': None,
        'birth_date': None,
        'note': None
    }
    
    for line in lines:
        line = line.strip()
        if not line or line in ['BEGIN:VCARD', 'END:VCARD', 'VERSION:3.0', 'VERSION:4.0']:
            continue
        
        # Extract key:value pairs
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.split(';')[0].upper()  # Handle metadata like TYPE=HOME
            
            if key == 'FN':
                contact_data['name'] = value
            elif key == 'N':
                # Format: LastName;FirstName;MiddleName;Prefix;Suffix
                parts = value.split(';')
                if len(parts) >= 2:
                    contact_data['surname'] = parts[0] if parts[0] else None
                    contact_data['given_names'] = parts[1] if parts[1] else None
            elif key == 'BDAY':
                contact_data['birth_date'] = value
            elif key == 'EMAIL':
                contact_data['email'] = value
            elif key == 'TEL':
                contact_data['phone'] = value
            elif key == 'NOTE':
                contact_data['note'] = value
    
    return CardDAVContactResponse(**contact_data)

def parse_vcf_file(file_path: str) -> List[CardDAVContactResponse]:
    """Parse a vCard file and return list of contacts"""
    contacts = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by BEGIN:VCARD and END:VCARD
    vcards = re.split(r'END:VCARD', content)
    
    for vcard in vcards:
        if 'BEGIN:VCARD' in vcard:
            vcard_content = vcard.split('BEGIN:VCARD', 1)[1]
            contact = parse_vcf(vcard_content)
            if contact.name:  # Only add if we extracted a name
                contacts.append(contact)
    
    return contacts
