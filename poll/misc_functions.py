import os
import uuid


def party_symbol_name(instance, filename):
    upload_to = 'party-symbols'
    party_name = ""
    if instance.name:
        party_name = instance.name
    else:
        party_name = str(uuid.uuid4())
    print(filename)
    filename = os.path.basename(filename)
    (name, ext) = os.path.splitext(filename)
    filename = '{}-{}.{}'.format(party_name, name, ext)
    return os.path.join(upload_to, filename)
