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

use AdnSystemsMonitor\Backend\Application\SelfService\DeviceRepository;
use AdnSystemsMonitor\Backend\Application\SelfService\GetDeviceDetails;
use AdnSystemsMonitor\Backend\Application\SelfService\UpdateDeviceOptions;
use Psr\Http\Message\ResponseInterface;
use Psr\Http\Message\ServerRequestInterface;

final class SelfServiceController
{
    private const SESSION_TIMEOUT = 3600 * 24 * 30; // 30 days

    public function __construct(
        private GetDeviceDetails $getDeviceDetails,
        private UpdateDeviceOptions $updateDeviceOptions,
        private DeviceRepository $deviceRepository,
    ) {
    }

    private const OPTIONS_MAX_LENGTH = 4096;

    public function getDevice(ServerRequestInterface $request, ResponseInterface $response): ResponseInterface
    {
        $this->ensureSession();
        $authResponse = $this->requireAuth($response);
        if ($authResponse !== null) {
            return $authResponse;
        }
        $intId = (int) ($request->getQueryParams()['int_id'] ?? $_SESSION['selected_int_id'] ?? 0);
        if ($intId === 0) {
            return $this->json($response, ['error' => 'Device not selected'], 400);
        }
        if (!$this->intIdAllowed($intId)) {
            return $this->json($response, ['error' => 'Device not allowed'], 403);
        }
        $result = ($this->getDeviceDetails)($intId);
        if ($result->isFail()) {
            return $this->json($response, ['error' => 'Device not found'], 404);
        }
        $client = $result->getValue();
        $options = $this->parseOptions($client->options);
        return $this->json($response, [
            'int_id' => $client->intId,
            'callsign' => $client->callsign,
            'mode' => $client->mode,
            'options' => $options,
        ]);
    }

    public function updateOptions(ServerRequestInterface $request, ResponseInterface $response): ResponseInterface
    {
        $this->ensureSession();
        $authResponse = $this->requireAuth($response);
        if ($authResponse !== null) {
            return $authResponse;
        }
        $body = $request->getParsedBody() ?? [];
        $intId = (int) ($body['int_id'] ?? $_SESSION['selected_int_id'] ?? 0);
        $options = trim((string) ($body['options'] ?? ''));
        if ($intId === 0) {
            return $this->json($response, ['error' => 'Invalid request'], 400);
        }
        if (!$this->intIdAllowed($intId)) {
            return $this->json($response, ['error' => 'Device not allowed'], 403);
        }
        if ($options === '') {
            return $this->json($response, ['error' => 'Options cannot be empty'], 400);
        }
        if (strlen($options) > self::OPTIONS_MAX_LENGTH) {
            return $this->json($response, ['error' => 'Options too long'], 400);
        }
        $result = ($this->updateDeviceOptions)($intId, $options);
        if ($result->isFail()) {
            return $this->json($response, ['error' => 'Update failed'], 400);
        }
        return $this->json($response, ['ok' => true]);
    }

    public function getModified(ServerRequestInterface $request, ResponseInterface $response): ResponseInterface
    {
        $this->ensureSession();
        $authResponse = $this->requireAuth($response);
        if ($authResponse !== null) {
            return $authResponse;
        }
        $intId = (int) ($request->getQueryParams()['int_id'] ?? $_SESSION['selected_int_id'] ?? 0);
        if ($intId === 0 || !$this->intIdAllowed($intId)) {
            return $this->json($response, ['modified' => 0]);
        }
        $modified = $this->deviceRepository->getModified($intId) ? 1 : 0;
        return $this->json($response, ['modified' => $modified]);
    }

    public function selectDevice(ServerRequestInterface $request, ResponseInterface $response): ResponseInterface
    {
        $this->ensureSession();
        $authResponse = $this->requireAuth($response);
        if ($authResponse !== null) {
            return $authResponse;
        }
        $body = $request->getParsedBody() ?? [];
        $intId = (int) ($body['int_id'] ?? 0);
        if (!$this->intIdAllowed($intId)) {
            return $this->json($response, ['error' => 'Invalid device'], 400);
        }
        $_SESSION['selected_int_id'] = $intId;
        return $this->json($response, ['ok' => true]);
    }

    private function ensureSession(): void
    {
        if (session_status() === PHP_SESSION_NONE) {
            session_start();
        }
        if (isset($_SESSION['last_activity']) && (time() - $_SESSION['last_activity'] > self::SESSION_TIMEOUT)) {
            session_unset();
            session_destroy();
            session_start();
        }
        $_SESSION['last_activity'] = time();
    }

    /** @return ResponseInterface|null Null if authorized; 401 response to return if not */
    private function requireAuth(ResponseInterface $response): ?ResponseInterface
    {
        if (empty($_SESSION['user_id'])) {
            $response->getBody()->write(json_encode(['error' => 'Unauthorized']));
            return $response->withHeader('Content-Type', 'application/json')->withStatus(401);
        }
        return null;
    }

    private function intIdAllowed(int $intId): bool
    {
        $intIds = $_SESSION['int_ids'] ?? [];
        return in_array($intId, $intIds, true);
    }

    /** @return array{TS1: list<string>, TS2: list<string>, DIAL: string, VOICE: string, LANG: string, SINGLE: string, TIMER: string} */
    private function parseOptions(string $options): array
    {
        $out = ['TS1' => [], 'TS2' => [], 'DIAL' => '0', 'VOICE' => '-1', 'LANG' => '0', 'SINGLE' => '-1', 'TIMER' => '0'];
        foreach (explode(';', $options) as $part) {
            $part = trim($part);
            if ($part === '') {
                continue;
            }
            if (str_contains($part, '=')) {
                [$key, $value] = explode('=', $part, 2);
                $key = trim($key);
                $value = trim($value);
                if ($key === 'TS1') {
                    $out['TS1'] = $value === '' ? [] : array_map('trim', explode(',', $value));
                } elseif ($key === 'TS2') {
                    $out['TS2'] = $value === '' ? [] : array_map('trim', explode(',', $value));
                } elseif (isset($out[$key])) {
                    $out[$key] = $value;
                }
            }
        }
        return $out;
    }

    private function json(ResponseInterface $response, array $data, int $status = 200): ResponseInterface
    {
        $response->getBody()->write(json_encode($data, JSON_THROW_ON_ERROR));
        return $response->withHeader('Content-Type', 'application/json')->withStatus($status);
    }
}
