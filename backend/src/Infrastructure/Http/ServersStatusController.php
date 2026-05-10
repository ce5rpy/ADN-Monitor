<?php

declare(strict_types=1);

/*
 * ADN Monitor - Dashboard and backend for ADN Systems.
 * Copyright (C) 2026  Rodrigo Pérez, CE5RPY <ce5rpy@qmd.cl>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 */

namespace AdnSystemsMonitor\Backend\Infrastructure\Http;

use AdnSystemsMonitor\Backend\Infrastructure\Config\ConfigLoader;
use JsonException;
use Psr\Http\Message\ResponseInterface;
use Psr\Http\Message\ServerRequestInterface;

/** Proxies configured world server status JSON (same-origin for the SPA; URL from adn-monitor.yaml). */
final class ServersStatusController
{
    private const DEFAULT_URL = 'https://adn.systems/servers/status.json';

    public function __construct(
        private ConfigLoader $configLoader,
    ) {
    }

    public function get(ServerRequestInterface $request, ResponseInterface $response): ResponseInterface
    {
        $config = $this->configLoader->load();
        $dashboard = $config['DASHBOARD'] ?? $config['dashboard'] ?? [];
        $url = trim((string) (
            $dashboard['SERVER_STATUS_URL']
            ?? $dashboard['server_status_url']
            ?? self::DEFAULT_URL
        ));
        if ($url === '') {
            $url = self::DEFAULT_URL;
        }
        if (!$this->isAllowedUrl($url)) {
            $response->getBody()->write(json_encode(['error' => 'Invalid SERVER_STATUS_URL in DASHBOARD config'], JSON_THROW_ON_ERROR));

            return $response->withStatus(500)->withHeader('Content-Type', 'application/json');
        }

        $ctx = stream_context_create([
            'http' => [
                'timeout' => 25,
                'header' => "User-Agent: ADN-Monitor-ServersStatus/1.0\r\nAccept: application/json\r\n",
            ],
            'ssl' => [
                'verify_peer' => true,
                'verify_peer_name' => true,
            ],
        ]);
        $raw = @file_get_contents($url, false, $ctx);
        if ($raw === false) {
            $response->getBody()->write(json_encode(['error' => 'Upstream server status request failed'], JSON_THROW_ON_ERROR));

            return $response->withStatus(502)->withHeader('Content-Type', 'application/json');
        }
        try {
            json_decode($raw, true, 512, JSON_THROW_ON_ERROR);
        } catch (JsonException) {
            $response->getBody()->write(json_encode(['error' => 'Upstream response is not valid JSON'], JSON_THROW_ON_ERROR));

            return $response->withStatus(502)->withHeader('Content-Type', 'application/json');
        }
        $response->getBody()->write($raw);

        return $response->withHeader('Content-Type', 'application/json; charset=utf-8');
    }

    private function isAllowedUrl(string $url): bool
    {
        $parts = parse_url($url);
        if (!is_array($parts) || empty($parts['scheme']) || empty($parts['host'])) {
            return false;
        }
        $scheme = strtolower((string) $parts['scheme']);

        return $scheme === 'http' || $scheme === 'https';
    }
}
