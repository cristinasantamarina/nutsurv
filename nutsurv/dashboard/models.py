from django.db import models

from jsonfield import JSONField
from jsonschema import validate, ValidationError


class JSONDocument(models.Model):
    # Set help_text to something else than empty but still invisible so that
    # the JSONField does not set it to its custom default (we want nothing
    # displayed).
    json = JSONField(null=True, blank=True, help_text=' ')

    def guess_type(self, list_of_json_document_types):
        """Matches the stored JSON document with the document types provided
        using list_of_json_document_types.  The order of the JSONDocumentType
        objects determines their priority as the method stops as soon as the
        first match is found.

        :param list_of_json_document_types:
        :return: the matched JSONDocumentType or None if no match found
        """
        for json_document_type in list_of_json_document_types:
            if json_document_type.matches(self):
                return json_document_type
        return None


class JSONDocumentType(models.Model):
    name = models.CharField(max_length=255)
    schema = JSONField(null=True, blank=True, help_text=' ')
    priority = models.IntegerField(unique=True, blank=True, null=True)

    def matches(self, json_document):
        try:
            validate(json_document.json, self.schema)
        except ValidationError:
            matches = False
        else:
            matches = True
        return matches

    @staticmethod
    def get_all_by_priority():
        return JSONDocumentType.objects.all().order_by('priority')

    def __unicode__(self):
        return self.name
