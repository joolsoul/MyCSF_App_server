from rest_framework import filters


class BuildingSearchFilter(filters.SearchFilter):
    search_param = 'building'
