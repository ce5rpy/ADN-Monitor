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

namespace AdnSystemsMonitor\Backend\Application\Auth;

use AdnSystemsMonitor\Backend\Domain\ValueObject\Result;

final class AuthenticateUser
{
    public function __construct(
        private AuthRepository $authRepository,
        private string $pbkdf2Salt = 'ADN',
        private int $pbkdf2Iterations = 2000,
    ) {
    }

    public function __invoke(string $callsign, string $password): Result
    {
        $user = $this->authRepository->findByCallsignAndLoggedIn($callsign);
        if ($user === null) {
            return Result::failure(new \RuntimeException('Invalid callsign or password'));
        }
        foreach ($user as $row) {
            if ($this->verifyPassword($password, $row['psswd'])) {
                return Result::success([
                    'callsign' => $row['callsign'],
                    'int_ids' => $this->authRepository->getIntIdsForCallsign($row['callsign']),
                ]);
            }
        }
        return Result::failure(new \RuntimeException('Invalid callsign or password'));
    }

    /**
     * Must match hotspot_proxy_self_service.py (same salt/iterations from config).
     */
    private function verifyPassword(string $password, string $storedHash): bool
    {
        $hash = hash_pbkdf2('sha256', $password, $this->pbkdf2Salt, $this->pbkdf2Iterations);
        return hash_equals($storedHash, $hash);
    }
}
