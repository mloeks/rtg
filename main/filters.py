import dateutil.parser
from django.core.exceptions import FieldDoesNotExist
from django.db.models import Q
from django.db.models.fields.related import ForeignObjectRel
from rest_framework import filters
from rest_framework.exceptions import ParseError
from rest_framework.filters import OrderingFilter

from main.utils import get_reference_date


class IsOwnerOrDeadlinePassed(filters.BaseFilterBackend):
    """
        Filter that only allows users to see their own bets
        or bets from other users if the corresponding deadline has passed already (bets are unchangeable and public then).
    """
    def filter_queryset(self, request, queryset, view):
        return queryset.filter(Q(user=request.user) | Q(bettable__deadline__lt=get_reference_date()))


class BettablesWithBetsOpenIfParamSet(filters.BaseFilterBackend):
    """
        Return only bettables where bets can still be placed (deadline has not yet passed), if bets_open=true is set in the request
        OR only those where bets can NOT be placed anymore (deadline has passed), if bets_open=false is set
    """
    def filter_queryset(self, request, queryset, view):
        bets_open = request.query_params.get('bets_open', None)
        if bets_open is not None:
            return queryset.filter(deadline__gt=get_reference_date()) if bets_open == 'true' \
                else queryset.filter(deadline__lte=get_reference_date())
        return queryset


class GamesFromDate(filters.BaseFilterBackend):
    """
        Return only games starting on or later than a given date
    """
    def filter_queryset(self, request, queryset, view):
        from_date = self.parse_date(request.query_params.get('from', None))
        if from_date is not None:
            return queryset.filter(kickoff__gte=from_date)
        return queryset

    def parse_date(self, date_string):
        if date_string:
            try:
                return dateutil.parser.parse(date_string)
            except ValueError:
                raise ParseError('Invalid date provided in from query parameter')
        return None

class GamesKickedOff(filters.BaseFilterBackend):
    """
        Return only games which have been kicked off (this includes finished games!)
    """
    def filter_queryset(self, request, queryset, view):
        kicked_off = request.query_params.get('kicked_off', None)
        if kicked_off:
            return queryset.filter(kickoff__lte=get_reference_date())
        return queryset


class TopLevelComments(filters.BaseFilterBackend):
    """
        Return only comments which directly reply to the post (reply_to = null)
    """
    def filter_queryset(self, request, queryset, view):
        toplevel = request.query_params.get('toplevel', None)
        if toplevel is not None and toplevel == 'true':
            return queryset.filter(reply_to=None)
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