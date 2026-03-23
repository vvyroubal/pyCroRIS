"""Testovi za crosbi.endpoints.projekti."""

import pytest

from crosbi.endpoints.projekti import (
    get_projekt,
    get_projekti_po_ustanovi,
    list_projekti,
)
from crosbi.models.projekt import Projekt


@pytest.fixture
def mock_client(mocker):
    return mocker.MagicMock()


class TestGetProjekt:
    def test_calls_correct_path(self, mock_client, projekt_raw):
        mock_client.get.return_value = projekt_raw
        result = get_projekt(1, client=mock_client)
        mock_client.get.assert_called_once_with("/projekt/1")

    def test_returns_projekt_instance(self, mock_client, projekt_raw):
        mock_client.get.return_value = projekt_raw
        result = get_projekt(1, client=mock_client)
        assert isinstance(result, Projekt)

    def test_id_mapped_correctly(self, mock_client, projekt_raw):
        mock_client.get.return_value = projekt_raw
        result = get_projekt(1, client=mock_client)
        assert result.id == 1


class TestListProjekti:
    def test_calls_paginate_with_correct_args(self, mock_client, projekt_raw):
        mock_client.paginate.return_value = iter([projekt_raw])
        results = list(list_projekti(client=mock_client))
        mock_client.paginate.assert_called_once_with("/projekt", "projekti")

    def test_returns_projekt_instances(self, mock_client, projekt_raw):
        mock_client.paginate.return_value = iter([projekt_raw])
        results = list(list_projekti(client=mock_client))
        assert len(results) == 1
        assert isinstance(results[0], Projekt)

    def test_empty_response_returns_empty_list(self, mock_client):
        mock_client.paginate.return_value = iter([])
        assert list(list_projekti(client=mock_client)) == []

    def test_multiple_results(self, mock_client, projekt_raw):
        raw2 = {**projekt_raw, "id": 2}
        mock_client.paginate.return_value = iter([projekt_raw, raw2])
        results = list(list_projekti(client=mock_client))
        assert len(results) == 2
        assert results[1].id == 2


class TestGetProjektiPoUstanovi:
    def test_calls_correct_path(self, mock_client, projekt_raw):
        mock_client.get_embedded.return_value = [projekt_raw]
        get_projekti_po_ustanovi("0010001", client=mock_client)
        mock_client.get_embedded.assert_called_once_with(
            "/projekt/ustanova/0010001", "projekti"
        )

    def test_returns_list_of_projekti(self, mock_client, projekt_raw):
        mock_client.get_embedded.return_value = [projekt_raw]
        result = get_projekti_po_ustanovi("0010001", client=mock_client)
        assert isinstance(result, list)
        assert isinstance(result[0], Projekt)

    def test_empty_response_returns_empty_list(self, mock_client):
        mock_client.get_embedded.return_value = []
        result = get_projekti_po_ustanovi("0010001", client=mock_client)
        assert result == []
