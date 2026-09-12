"""
IP Whitelisting Service supporting CIDR subnet matching.
"""
import ipaddress
import logging
from typing import List
from core.ports.interfaces import IIPWhitelist

logger = logging.getLogger(__name__)


class IPWhitelistService(IIPWhitelist):
    """
    IP Whitelisting adapter using Python standard ipaddress module.
    Supports individual IPv4/IPv6 addresses and CIDR notation subnets (e.g. 192.168.1.0/24).
    """

    def is_allowed(self, client_ip: str, allowed_cidrs: List[str]) -> bool:
        """
        Returns True if client_ip matches any entry in allowed_cidrs.
        If allowed_cidrs is empty, access is allowed by default.
        """
        if not allowed_cidrs:
            return True

        try:
            ip_obj = ipaddress.ip_address(client_ip.strip())
        except ValueError:
            logger.warning(f"Invalid client IP address provided: {client_ip}")
            return False

        for cidr in allowed_cidrs:
            try:
                network = ipaddress.ip_network(cidr.strip(), strict=False)
                if ip_obj in network:
                    return True
            except ValueError:
                # Might be exact IP string or invalid pattern
                try:
                    if ip_obj == ipaddress.ip_address(cidr.strip()):
                        return True
                except ValueError:
                    logger.warning(f"Invalid CIDR/IP string in whitelist: {cidr}")
                    continue

        return False
