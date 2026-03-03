<?php

declare(strict_types=1);


/*
 * ADN Monitor - Dashboard and backend for ADN Systems.
 * Copyright (C) 2025  Rodrigo Pérez, CE5RPY <ce5rpy@qmd.cl>
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

final class ConfigController
{
    public function __construct(
        private ConfigLoader $configLoader,
        private string $configPath,
    ) {
    }

    public function dashboard(ServerRequestInterface $request, ResponseInterface $response): ResponseInterface
    {
        $config = $this->configLoader->load();
        $dashboard = $config['DASHBOARD'] ?? $config['dashboard'] ?? [];

        $title = $dashboard['DASHTITLE'] ?? $dashboard['dashtitle'] ?? 'ADN Systems Dashboard';

        $navLinks = $this->normalizeNavLinks($dashboard);
        $footer = $this->normalizeFooter($dashboard);

        $out = [
            'title' => $title,
            'language' => $dashboard['LANGUAGE'] ?? $dashboard['language'] ?? 'en',
            'background' => (bool) ($dashboard['BACKGROUND'] ?? $dashboard['background'] ?? false),
            'selfService' => (bool) ($dashboard['SELF_SERVICE'] ?? $dashboard['self_service'] ?? false),
            'footer' => $footer,
            'navLinks' => $navLinks,
        ];
        $response->getBody()->write(json_encode($out, JSON_THROW_ON_ERROR | JSON_INVALID_UTF8_SUBSTITUTE));
        return $response->withHeader('Content-Type', 'application/json');
    }

    /** @return array{name: string, items: array<array{name: string, url: string}>} */
    private function normalizeNavLinks(array $dashboard): array
    {
        $nav = $dashboard['nav_links'] ?? $dashboard['NAV_LINKS'] ?? null;
        if (is_array($nav)) {
            $name = $nav['name'] ?? $nav['Name'] ?? '';
            $items = $nav['items'] ?? $nav['Items'] ?? [];
            if (is_array($items)) {
                $list = [];
                foreach ($items as $entry) {
                    if (is_array($entry) && isset($entry['name'], $entry['url'])) {
                        $list[] = ['name' => (string) $entry['name'], 'url' => (string) $entry['url']];
                    } elseif (is_array($entry) && isset($entry['name']) && isset($entry['url'])) {
                        $list[] = ['name' => (string) $entry['name'], 'url' => (string) $entry['url']];
                    } elseif (is_string($entry)) {
                        $parts = explode(',', $entry, 2);
                        $list[] = ['name' => trim($parts[0] ?? ''), 'url' => trim($parts[1] ?? '')];
                    }
                }
                return ['name' => (string) $name, 'items' => $list];
            }
        }
        $navName = $dashboard['NAV_LNK_NAME'] ?? $dashboard['nav_lnk_name'] ?? '';
        $items = [];
        for ($i = 1; true; $i++) {
            $val = $dashboard['LINK' . $i] ?? $dashboard['link' . $i] ?? null;
            if ($val === null || $val === '') {
                break;
            }
            $parts = explode(',', (string) $val, 2);
            $items[] = ['name' => trim($parts[0] ?? ''), 'url' => trim($parts[1] ?? '')];
        }
        return ['name' => (string) $navName, 'items' => $items];
    }

    /** @return list<array{name: string, url: string}> Same structure as nav_links items (name + url). */
    private function normalizeFooter(array $dashboard): array
    {
        $footer = $dashboard['footer'] ?? $dashboard['FOOTER'] ?? null;
        if (is_array($footer)) {
            $items = $footer['items'] ?? $footer['Items'] ?? $footer;
            if (is_array($items)) {
                $list = [];
                foreach ($items as $entry) {
                    if (is_array($entry) && isset($entry['name'], $entry['url'])) {
                        $list[] = ['name' => (string) $entry['name'], 'url' => (string) $entry['url']];
                    } elseif (is_array($entry) && isset($entry['name']) && isset($entry['url'])) {
                        $list[] = ['name' => (string) $entry['name'], 'url' => (string) $entry['url']];
                    } elseif (is_string($entry)) {
                        $parts = explode(',', $entry, 2);
                        $list[] = ['name' => trim($parts[0] ?? ''), 'url' => trim($parts[1] ?? '')];
                    }
                }
                return $list;
            }
        }
        $list = [];
        for ($i = 1; true; $i++) {
            $val = $dashboard['FOOTER' . $i] ?? $dashboard['footer' . $i] ?? null;
            if ($val === null || $val === '') {
                break;
            }
            $parts = explode(',', (string) $val, 2);
            $list[] = ['name' => trim($parts[0] ?? ''), 'url' => trim($parts[1] ?? '')];
        }
        return $list;
    }
}
