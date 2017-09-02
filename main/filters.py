from django.db.models import Q
from django.conf import settings
from django.utils import timezone
from rest_framework import filters

from django.core.exceptions import FieldDoesNotExist
from django.db.models.fields.related import ForeignObjectRel
from rest_framework.filters import OrderingFilter


class IsOwnerOrGameDeadlinePassed(filters.BaseFilterBackend):
    """
        Filter that only allows users to see their own bets
        or bets from other users if the corresponding game bet deadline has passed already (bets are unchangeable and public then).
    """
    def filter_queryset(self, request, queryset, view):
        reference_date = settings.FAKE_DATE if hasattr(settings, 'FAKE_DATE') else timezone.now()
        return queryset.filter(Q(user=request.user) | Q(game__deadline__lt=reference_date))


class IsOwnerOrExtraDeadlinePassed(filters.BaseFilterBackend):
    """
        Same as IsOwnerOrGameDeadlinePassed, only for ExtraBets
    """
    def filter_queryset(self, request, queryset, view):
        reference_date = settings.FAKE_DATE if hasattr(settings, 'FAKE_DATE') else timezone.now()
        return queryset.filter(Q(user=request.user) | Q(extra__deadline__lt=reference_date))


class GamesWithBetsOpenIfParamSet(filters.BaseFilterBackend):
    """
        Return only games where bets can still be placed (deadline has not yet passed), if bets_open=true is set in the request
    """
    def filter_queryset(self, request, queryset, view):
        bets_open = request.query_params.get('bets_open', None)
        if bets_open is not None:
            if bets_open == 'true':
                reference_date = settings.FAKE_DATE if hasattr(settings, 'FAKE_DATE') else timezone.now()
                return queryset.filter(deadline__gt=reference_date)
        return queryset


class RelatedOrderingFilter(OrderingFilter):
    """
        Extends OrderingFilter to support ordering by fields in related models
        using the Django ORM __ notation
        cf. https://github.com/tomchristie/django-rest-framework/issues/1005
    """
    def is_valid_field(self, model, field):
        """
            Return true if the field exists within the model (or in the related
            model specified using the Django ORM __ notation)
        """
        components = field.split('__', 1)
        try:
            field, parent_model, direct, m2m = \
                model._meta.get_field_by_name(components[0])

            # reverse relation
            if isinstance(field, ForeignObjectRel):
                return self.is_valid_field(field.model, components[1])

            # foreign key
            if field.rel and len(components) == 2:
                return self.is_valid_field(field.rel.to, components[1])
            return True
        except FieldDoesNotExist:
            return False

    def remove_invalid_fields(self, queryset, ordering, view):
        return [term for term in ordering
                if self.is_valid_field(queryset.model, term.lstrip('-'))]