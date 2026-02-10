import asyncio
import socket
import ipaddress
import logging
from urllib.parse import urlparse
from typing import List

logger = logging.getLogger(__name__)

async def is_safe_url(url: str) -> bool:
    """
    Check if a URL is safe to fetch (not pointing to local or private networks).

    This function performs the following checks:
    1. Validates the scheme (only http and https allowed).
    2. Resolves the hostname to IP addresses.
    3. Checks if any resolved IP is in a private, loopback, or link-local range.

    Args:
        url: The URL to check.

    Returns:
        True if the URL is safe, False otherwise.
    """
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            logger.warning(f"URL scheme not allowed: {parsed.scheme}")
            return False

        hostname = parsed.hostname
        if not hostname:
            logger.warning(f"Could not extract hostname from URL: {url}")
            return False

        # Handle IPv6 brackets in hostname if present (urlparse should handle this,
        # but ipaddress needs it without brackets)
        host_to_resolve = hostname
        if hostname.startswith('[') and hostname.endswith(']'):
            host_to_resolve = hostname[1:-1]

        # Check if the hostname itself is an IP address
        try:
            ip = ipaddress.ip_address(host_to_resolve)
            if _is_private_ip(ip):
                logger.warning(f"URL points to a private IP: {ip}")
                return False
            return True
        except ValueError:
            # Not an IP address, proceed to DNS resolution
            pass

        # Resolve hostname to IP addresses (async)
        loop = asyncio.get_event_loop()
        try:
            # We use getaddrinfo to get both IPv4 and IPv6 addresses
            addr_info = await loop.getaddrinfo(hostname, None)
        except socket.gaierror as e:
            logger.error(f"DNS resolution failed for {hostname}: {e}")
            return False

        for item in addr_info:
            ip_str = item[4][0]
            try:
                ip = ipaddress.ip_address(ip_str)
                if _is_private_ip(ip):
                    logger.warning(f"Hostname {hostname} resolves to a private IP: {ip}")
                    return False
            except ValueError:
                continue

        return True
    except Exception as e:
        logger.error(f"Error validating URL {url}: {e}")
        return False

def _is_private_ip(ip: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    """Check if an IP address is in a private or reserved range."""
    return (
        ip.is_loopback or
        ip.is_private or
        ip.is_link_local or
        ip.is_unspecified or
        ip.is_multicast or
        # Additional checks for IPv4 mapped IPv6 addresses
        (isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped and _is_private_ip(ip.ipv4_mapped))
    )
