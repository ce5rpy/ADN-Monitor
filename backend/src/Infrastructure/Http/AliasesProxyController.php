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
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

namespace AdnSystemsMonitor\Backend\Infrastructure\Http;

use AdnSystemsMonitor\Backend\Infrastructure\Config\ConfigLoader;
use Psr\Http\Message\ResponseInterface;
use Psr\Http\Message\ServerRequestInterface;

/**
 * Proxies TG list and Bridge list from configured URLs to avoid CORS in the frontend.
 */
final class AliasesProxyController
{
    private const BASE_URL_FALLBACK = 'https://adn.systems/files';

    public function __construct(
        private ConfigLoader $configLoader,
    ) {
    }

    private function getAliases(): array
    {
        $config = $this->configLoader->load();
        $aliases = $config['ALIASES'] ?? $config['FILES'] ?? [];
        $baseUrl = getenv('ALIASES_BASE_URL') ?: self::BASE_URL_FALLBACK;
        return [
            'tgListUrl' => $aliases['TG_LIST_URL'] ?? $aliases['tg_list_url'] ?? $baseUrl . '/talkgroup_ids.json',
            'bridgeListUrl' => $aliases['BRIDGE_LIST_URL'] ?? $aliases['bridge_list_url'] ?? $baseUrl . '/server_ids.tsv',
        ];
    }

    private function fetchUrl(string $url): string|false
    {
        $ctx = stream_context_create([
            'http' => [
                'timeout' => 15,
                'user_agent' => 'ADN-Monitor-Backend/1.0',
                'follow_location' => true,
            ],
        ]);
        $body = @file_get_contents($url, false, $ctx);
        return $body !== false ? $body : false;
    }

    public function tgList(ServerRequestInterface $request, ResponseInterface $response): ResponseInterface
    {
        $url = trim($this->getAliases()['tgListUrl']);
        $body = $this->fetchUrl($url);
        if ($body === false) {
            $response->getBody()->write(json_encode([
                'error' => 'Failed to load TG list. Check backend can reach: ' . $url,
            ], JSON_THROW_ON_ERROR));
            return $response->withStatus(502)->withHeader('Content-Type', 'application/json');
        }
        $response->getBody()->write($body);
        return $response->withHeader('Content-Type', 'application/json');
    }

    public function bridgeList(ServerRequestInterface $request, ResponseInterface $response): ResponseInterface
    {
        $url = trim($this->getAliases()['bridgeListUrl']);
        $body = $this->fetchUrl($url);
        if ($body === false) {
            $response->getBody()->write(json_encode([
                'error' => 'Failed to load bridge list. Check backend can reach: ' . $url,
            ], JSON_THROW_ON_ERROR));
            return $response->withStatus(502)->withHeader('Content-Type', 'application/json');
        }
        $response->getBody()->write($body);
        return $response->withHeader('Content-Type', 'text/tab-separated-values; charset=utf-8');
    }
}
