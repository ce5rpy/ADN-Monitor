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

namespace AdnSystemsMonitor\Backend\Domain\ValueObject;

/**
 * Result type for functional error handling.
 */
final readonly class Result
{
    private function __construct(
        private bool $isOk,
        private mixed $value = null,
        private ?\Throwable $error = null,
    ) {
    }

    public static function success(mixed $value): self
    {
        return new self(true, $value, null);
    }

    public static function failure(\Throwable $error): self
    {
        return new self(false, null, $error);
    }

    public function isOk(): bool
    {
        return $this->isOk;
    }

    public function isFail(): bool
    {
        return !$this->isOk;
    }

    public function getValue(): mixed
    {
        return $this->value;
    }

    public function getError(): ?\Throwable
    {
        return $this->error;
    }

    public function unwrapOr(mixed $default): mixed
    {
        return $this->isOk ? $this->value : $default;
    }
}
