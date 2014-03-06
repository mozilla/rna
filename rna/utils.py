from .models import Release


def migrate_versions():
    for r in Release.objects.filter(version__endswith='.0.0').only(
            'channel', 'version'):
        if r.channel == 'Release':
            Release.objects.filter(id=r.id).update(version=r.version[:-2])
        elif r.channel == 'Aurora':
            Release.objects.filter(id=r.id).update(version=r.version[:-2] + 'a2')
        elif r.channel == 'Beta':
            Release.objects.filter(id=r.id).update(version=r.version[:-2] + 'beta')


def get_duplicate_product_versions():
    version_ids = {}
    duplicates = {}
    for product in Release.PRODUCTS:
        version_ids[product] = {}
        for r in Release.objects.filter(product=product):
            version_ids[product].setdefault(r.version, [])
            version_ids[product][r.version].append(r.id)
            if len(version_ids[product][r.version]) > 1:
                duplicates[(product, r.version)] = version_ids[product][
                    r.version]
    return duplicates
