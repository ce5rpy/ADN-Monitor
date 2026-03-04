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

namespace AdnSystemsMonitor\Backend\Infrastructure\Persistence;

use AdnSystemsMonitor\Backend\Application\Auth\AuthRepository;
use PDO;

final class MySqlAuthRepository implements AuthRepository
{
    public function __construct(
        private PDO $pdo,
    ) {
    }

    /** @return array<int, array{callsign: string, psswd: string}>|null */
    public function findByCallsignAndLoggedIn(string $callsign): ?array
    {
        $stmt = $this->pdo->prepare(
            'SELECT int_id, callsign, psswd FROM Clients WHERE callsign = :callsign AND logged_in = 1'
        );
        $stmt->execute(['callsign' => $callsign]);
        $rows = $stmt->fetchAll(PDO::FETCH_ASSOC);
        if ($rows === []) {
            return null;
        }
        $out = [];
        foreach ($rows as $row) {
            $out[(int) $row['int_id']] = ['callsign' => $row['callsign'], 'psswd' => $row['psswd']];
        }
        return $out;
    }

    /** @return list<int> */
    public function getIntIdsForCallsign(string $callsign): array
    {
        $stmt = $this->pdo->prepare(
            'SELECT int_id FROM Clients WHERE callsign = :callsign AND logged_in = 1'
        );
        $stmt->execute(['callsign' => $callsign]);
        $rows = $stmt->fetchAll(PDO::FETCH_COLUMN);
        $ids = array_map('intval', $rows);
        return array_values(array_unique($ids, SORT_NUMERIC));
    }

    /** @return array{callsign: string, int_ids: list<int>}|null */
    public function findByHost(string $ip): ?array
    {
        $stmt = $this->pdo->prepare(
            "SELECT DISTINCT callsign FROM Clients WHERE host = :host AND logged_in = 1"
        );
        $stmt->execute(['host' => $ip]);
        $rows = $stmt->fetchAll(PDO::FETCH_COLUMN);
        if (count($rows) !== 1) {
            return null;
        }
        $callsign = $rows[0];
        $intIds = $this->getIntIdsForCallsign($callsign);
        if ($intIds === []) {
            return null;
        }
        return ['callsign' => $callsign, 'int_ids' => $intIds];
    }
}
