from django.conf import settings

from documents import Device


_default_device = Device.objects(name=settings.SITE['name']).first()

if not _default_device:
    _default_device = Device(name=settings.SITE['name'],
        url=''.join(('http://', settings.SITE['domain'], '/')))
    _default_device.save()

default_device = _default_device
