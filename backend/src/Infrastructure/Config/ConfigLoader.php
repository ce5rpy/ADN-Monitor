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

namespace AdnSystemsMonitor\Backend\Infrastructure\Config;

use Symfony\Component\Yaml\Yaml;

/**
 * Loads adn-mon config from YAML (adn-mon.yaml).
 * Section and key names are preserved; lowercase key aliases are added for compatibility
 * with code that expects lowercased option names.
 */
final class ConfigLoader
{
    public function __construct(
        private string $configPath,
    ) {
    }

    /** @return array<string, array<string, mixed>> */
    public function load(): array
    {
        if (!is_readable($this->configPath)) {
            throw new \RuntimeException('Config file not found: ' . $this->configPath);
        }
        $raw = file_get_contents($this->configPath);
        if ($raw === false) {
            return [];
        }

        $ext = strtolower(pathinfo($this->configPath, PATHINFO_EXTENSION));
        if ($ext !== 'yaml' && $ext !== 'yml') {
            throw new \RuntimeException('Config must be YAML (.yaml or .yml): ' . $this->configPath);
        }

        return $this->parseYaml($raw);
    }

    /** @return array<string, array<string, mixed>> */
    private function parseYaml(string $raw): array
    {
        $data = Yaml::parse($raw);
        if (!is_array($data)) {
            return [];
        }
        $config = [];
        foreach ($data as $section => $values) {
            if (!is_array($values)) {
                continue;
            }
            $config[$section] = [];
            foreach ($values as $key => $val) {
                $config[$section][$key] = $val;
                $config[$section][strtolower((string) $key)] = is_scalar($val) || $val === null ? ($val === null ? '' : $val) : $val;
            }
        }
        return $config;
    }

    public static function fromEnv(): self
    {
        $path = $_ENV['ADN_CONFIG_PATH'] ?? dirname(__DIR__, 3) . '/../adn-mon.yaml';
        return new self($path);
    }
}
