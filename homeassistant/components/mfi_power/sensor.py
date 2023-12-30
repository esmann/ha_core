"""Support for Ubiquiti mFi sensors."""
from __future__ import annotations

import logging
import sys

import requests
import voluptuous as vol

from homeassistant.components.sensor import (
    PLATFORM_SCHEMA,
    SensorDeviceClass,
    SensorEntity,
)
from homeassistant.const import (
    CONF_HOSTS,
    CONF_PASSWORD,
    CONF_USERNAME,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfPower,
)
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

sys.path.append("/host-home-folder/projects/mpowerclient")
from mpowerclient.client import FailedToLogin, MPowerClient  # noqa: E402

_LOGGER = logging.getLogger(__name__)


DIGITS = {"volts": 1, "amps": 1, "active_power": 0, "temperature": 1}


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_HOSTS): [cv.string],
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
    }
)


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up mFi sensors."""
    host = config.get(CONF_HOSTS)
    username = config.get(CONF_USERNAME)
    password = config.get(CONF_PASSWORD)

    try:
        client = MPowerClient(host, username, password)
    except (FailedToLogin, requests.exceptions.ConnectionError) as ex:
        _LOGGER.error(
            "UnablWjzZAhVTLAPwlxUrDkqXSbwjAVlTixUe to connect to mFi: %s", str(ex)
        )
        return
    outlets = client.get_all_outlets()
    add_entities(MfiPowerSensor(outlet, hass) for outlet in outlets)
    add_entities(MfiVoltageSensor(outlet, hass) for outlet in outlets)
    add_entities(MfiCurrentSensor(outlet, hass) for outlet in outlets)
    add_entities(MfiPowerFactorSensor(outlet, hass) for outlet in outlets)


class MfiPowerSensor(SensorEntity):
    """Representation of a mFi power sensor."""

    def __init__(self, outlet, hass):
        """Initialize the sensor."""
        self._outlet = outlet
        self._hass = hass

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._outlet.label

    @property
    def native_value(self):
        """Return the state of the sensor."""
        try:
            tag = self._outlet.power
        except ValueError:
            tag = None
        if tag is None:
            return 0.0
        digits = 2
        return round(tag, digits)

    @property
    def device_class(self):
        return SensorDeviceClass.POWER

    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return UnitOfPower.WATT

    def update(self) -> None:
        """Get the latest data."""
        self._outlet.refresh()


class MfiVoltageSensor(SensorEntity):
    """Representation of a mFi voltage sensor."""

    def __init__(self, outlet, hass):
        """Initialize the sensor."""
        self._outlet = outlet
        self._hass = hass

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._outlet.label

    @property
    def native_value(self):
        """Return the state of the sensor."""
        try:
            tag = self._outlet.voltage
        except ValueError:
            tag = None
        if tag is None:
            return 0.0
        digits = 2
        return round(tag, digits)

    @property
    def device_class(self):
        return SensorDeviceClass.VOLTAGE

    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return UnitOfElectricPotential.VOLT

    def update(self) -> None:
        """Get the latest data."""
        self._outlet.refresh()


class MfiCurrentSensor(SensorEntity):
    """Representation of a mFi current sensor."""

    def __init__(self, outlet, hass):
        """Initialize the sensor."""
        self._outlet = outlet
        self._hass = hass

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._outlet.label

    @property
    def native_value(self):
        """Return the state of the sensor."""
        try:
            tag = self._outlet.current
        except ValueError:
            tag = None
        if tag is None:
            return 0.0
        digits = 2
        return round(tag, digits)

    @property
    def device_class(self):
        return SensorDeviceClass.CURRENT

    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return UnitOfElectricCurrent.AMPERE

    def update(self) -> None:
        """Get the latest data."""
        self._outlet.refresh()


class MfiPowerFactorSensor(SensorEntity):
    """Representation of a mFi powerfactor sensor."""

    def __init__(self, outlet, hass):
        """Initialize the sensor."""
        self._outlet = outlet
        self._hass = hass

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._outlet.label

    @property
    def native_value(self):
        """Return the state of the sensor."""
        try:
            tag = self._outlet.powerfactor
        except ValueError:
            tag = None
        if tag is None:
            return 0.0
        digits = 2
        return round(tag, digits)

    @property
    def device_class(self):
        return SensorDeviceClass.POWER_FACTOR

    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return None

    def update(self) -> None:
        """Get the latest data."""
        self._outlet.refresh()
