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
 *
 * Derived from: FDMR Monitor (OA4DOA, https://github.com/yuvelq/FDMR-Monitor);
 * HBMonv2 (SP2ONG, https://github.com/sp2ong/HBMonv2);
 * hbmonitor3 (KC1AWV, https://github.com/kc1awv/hbmonitor3);
 * HBmonitor (Cortney T. Buffington, N0MJS, Copyright (C) 2013-2018).
 * Original works and this derivative are under GPLv3.
 */

namespace AdnSystemsMonitor\Backend\Infrastructure\Persistence;

use AdnSystemsMonitor\Backend\Application\SelfService\DeviceRepository;
use AdnSystemsMonitor\Backend\Domain\Entity\Client;
use PDO;

final class MySqlDeviceRepository implements DeviceRepository
{
    public function __construct(
        private PDO $pdo,
    ) {
    }

    public function getById(int $intId): ?Client
    {
        $stmt = $this->pdo->prepare('SELECT * FROM Clients WHERE int_id = :id');
        $stmt->execute(['id' => $intId]);
        $row = $stmt->fetch(PDO::FETCH_ASSOC);
        if ($row === false) {
            return null;
        }
        return new Client(
            intId: (int) $row['int_id'],
            callsign: $row['callsign'],
            options: $row['options'] ?? '',
            modified: (bool) (int) ($row['modified'] ?? 0),
            mode: (int) ($row['mode'] ?? 4),
            host: $row['host'] ?? null,
        );
    }

    public function updateOptions(int $intId, string $options): int
    {
        // Set modified=1 so the hotspot proxy send_opts (every 10s) will push RPTO to the peer server
        // and the new options (e.g. TG list) apply to the hotspot without restart. Proxy then sets modified=0.
        $stmt = $this->pdo->prepare(
            'UPDATE Clients SET options = :options, modified = 1 WHERE int_id = :id'
        );
        $stmt->execute(['options' => $options, 'id' => $intId]);
        return $stmt->rowCount();
    }

    public function getModified(int $intId): bool
    {
        $stmt = $this->pdo->prepare('SELECT modified FROM Clients WHERE int_id = :id');
        $stmt->execute(['id' => $intId]);
        $row = $stmt->fetch(PDO::FETCH_ASSOC);
        return $row !== false && (bool) (int) $row['modified'];
    }
}
