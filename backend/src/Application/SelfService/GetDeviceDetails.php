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

namespace AdnSystemsMonitor\Backend\Application\SelfService;

use AdnSystemsMonitor\Backend\Domain\Entity\Client;
use AdnSystemsMonitor\Backend\Domain\ValueObject\Result;

final class GetDeviceDetails
{
    public function __construct(
        private DeviceRepository $deviceRepository,
    ) {
    }

    public function __invoke(int $intId): Result
    {
        $client = $this->deviceRepository->getById($intId);
        if ($client === null) {
            return Result::failure(new \RuntimeException('Device not found'));
        }
        return Result::success($client);
    }
}
