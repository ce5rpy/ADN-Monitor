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

use AdnSystemsMonitor\Backend\Application\Auth\AuthenticateByIp;
use AdnSystemsMonitor\Backend\Application\Auth\AuthenticateUser;
use Psr\Http\Message\ResponseInterface;
use Psr\Http\Message\ServerRequestInterface;
use Slim\Routing\RouteContext;

final class AuthController
{
    public function __construct(
        private AuthenticateUser $authenticateUser,
        private AuthenticateByIp $authenticateByIp,
    ) {
    }

    public function login(ServerRequestInterface $request, ResponseInterface $response): ResponseInterface
    {
        $body = $request->getParsedBody() ?? [];
        $callsign = trim((string) ($body['callsign'] ?? ''));
        $password = (string) ($body['password'] ?? '');
        if ($callsign === '' || $password === '') {
            return $this->json($response, ['error' => 'Missing callsign or password'], 400);
        }
        $result = ($this->authenticateUser)($callsign, $password);
        if ($result->isFail()) {
            return $this->json($response, ['error' => 'Invalid callsign or password'], 401);
        }
        $data = $result->getValue();
        $this->startSession($data);
        return $this->json($response, ['redirect' => '/self-service']);
    }

    public function loginByIp(ServerRequestInterface $request, ResponseInterface $response): ResponseInterface
    {
        $ip = $request->getServerParams()['REMOTE_ADDR'] ?? '';
        if ($ip === '') {
            return $this->json($response, ['error' => 'Unknown client'], 400);
        }
        $result = ($this->authenticateByIp)($ip);
        if ($result->isFail()) {
            return $this->json($response, ['error' => 'No single user for this IP'], 401);
        }
        $data = $result->getValue();
        $this->startSession($data);
        return $this->json($response, ['redirect' => '/self-service']);
    }

    public function logout(ServerRequestInterface $request, ResponseInterface $response): ResponseInterface
    {
        $this->destroySession();
        return $this->json($response, ['redirect' => '/login']);
    }

    public function me(ServerRequestInterface $request, ResponseInterface $response): ResponseInterface
    {
        if (session_status() === PHP_SESSION_NONE) {
            session_start();
        }
        if (empty($_SESSION['user_id'])) {
            return $this->json($response, ['error' => 'Unauthorized'], 401);
        }
        return $this->json($response, [
            'callsign' => $_SESSION['user_id'],
            'int_ids' => $_SESSION['int_ids'] ?? [],
            'selected_int_id' => $_SESSION['selected_int_id'] ?? null,
        ]);
    }

    /** @param array{callsign: string, int_ids: list<int>} $data */
    private function startSession(array $data): void
    {
        if (session_status() === PHP_SESSION_NONE) {
            session_start();
        }
        $_SESSION['user_id'] = $data['callsign'];
        $_SESSION['int_ids'] = $data['int_ids'];
        $_SESSION['selected_int_id'] = $data['int_ids'][0] ?? null;
        $_SESSION['last_activity'] = time();
    }

    private function destroySession(): void
    {
        if (session_status() === PHP_SESSION_NONE) {
            session_start();
        }
        $_SESSION = [];
        session_destroy();
    }

    private function json(ResponseInterface $response, array $data, int $status = 200): ResponseInterface
    {
        $response->getBody()->write(json_encode($data, JSON_THROW_ON_ERROR));
        return $response->withHeader('Content-Type', 'application/json')->withStatus($status);
    }
}
