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

/**
 * ADN Systems Monitor API entry point.
 */

use AdnSystemsMonitor\Backend\Infrastructure\Config\ConfigLoader;
use AdnSystemsMonitor\Backend\Infrastructure\Http\AliasesProxyController;
use AdnSystemsMonitor\Backend\Infrastructure\Http\AuthController;
use AdnSystemsMonitor\Backend\Infrastructure\Http\ConfigController;
use AdnSystemsMonitor\Backend\Infrastructure\Http\SelfServiceController;
use AdnSystemsMonitor\Backend\Infrastructure\Persistence\MySqlAuthRepository;
use AdnSystemsMonitor\Backend\Infrastructure\Persistence\MySqlDeviceRepository;
use AdnSystemsMonitor\Backend\Application\Auth\AuthenticateByIp;
use AdnSystemsMonitor\Backend\Application\Auth\AuthenticateUser;
use AdnSystemsMonitor\Backend\Application\SelfService\GetDeviceDetails;
use AdnSystemsMonitor\Backend\Application\SelfService\UpdateDeviceOptions;
use Slim\Factory\AppFactory;
use Slim\Routing\RouteCollectorProxy;

require dirname(__DIR__) . '/vendor/autoload.php';

$projectRoot = dirname(__DIR__, 2);
$backendRoot = dirname(__DIR__);

// Load .env: first project root (monorepo), then backend dir (so backend can have its own .env)
if (is_file($projectRoot . '/.env')) {
    $dotenv = Dotenv\Dotenv::createImmutable($projectRoot);
    $dotenv->safeLoad();
} elseif (is_file($backendRoot . '/.env')) {
    $dotenv = Dotenv\Dotenv::createImmutable($backendRoot);
    $dotenv->safeLoad();
}

// Path to adn-mon.yaml: nginx fastcgi_param → $_SERVER; else getenv / .env; else default
$configPath = ($_SERVER['ADN_CONFIG_PATH'] ?? null) ?: getenv('ADN_CONFIG_PATH') ?: ($_ENV['ADN_CONFIG_PATH'] ?? $projectRoot . '/monitor/adn-mon.yaml');
$configPath = is_string($configPath) ? $configPath : $projectRoot . '/monitor/adn-mon.yaml';
$defaultYaml = $projectRoot . '/monitor/adn-mon.yaml';
if (!is_readable($configPath)) {
    $configPath = $defaultYaml;
}

try {
    $configLoader = new ConfigLoader($configPath);
    $config = $configLoader->load();
} catch (Throwable $e) {
    http_response_code(500);
    header('Content-Type: application/json');
    echo json_encode([
        'error' => 'Config load failed',
        'message' => $e->getMessage(),
        'path' => $configPath,
    ], JSON_THROW_ON_ERROR);
    exit(1);
}

$db = $config['SELF_SERVICE'] ?? null;
$pdo = null;
$authController = null;
$selfServiceController = null;

if ($db) {
    try {
        $dsn = sprintf(
            'mysql:host=%s;port=%s;dbname=%s;charset=utf8mb4',
            $db['DB_SERVER'] ?? 'localhost',
            $db['DB_PORT'] ?? 3306,
            $db['DB_NAME'] ?? 'adn'
        );
        $pdo = new PDO($dsn, $db['DB_USERNAME'] ?? 'root', $db['DB_PASSWORD'] ?? '', [
            PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
        ]);
        $authRepo = new MySqlAuthRepository($pdo);
        $deviceRepo = new MySqlDeviceRepository($pdo);
        $authenticateUser = new AuthenticateUser(
            $authRepo,
            (string) ($db['PBKDF2_SALT'] ?? $db['pbkdf2_salt'] ?? 'ADN'),
            (int) ($db['PBKDF2_ITERATIONS'] ?? $db['pbkdf2_iterations'] ?? 2000),
        );
        $authenticateByIp = new AuthenticateByIp($authRepo);
        $getDeviceDetails = new GetDeviceDetails($deviceRepo);
        $updateDeviceOptions = new UpdateDeviceOptions($deviceRepo);
        $authController = new AuthController($authenticateUser, $authenticateByIp);
        $selfServiceController = new SelfServiceController($getDeviceDetails, $updateDeviceOptions, $deviceRepo);
    } catch (Throwable $e) {
        $pdo = null;
        $authController = null;
        $selfServiceController = null;
    }
}

$configController = new ConfigController($configLoader, $configPath);
$aliasesProxyController = new AliasesProxyController($configLoader);

$app = AppFactory::create();
$app->addBodyParsingMiddleware();
$app->addRoutingMiddleware();
$app->setBasePath($_ENV['API_BASE_PATH'] ?? '');

$app->get('/api/config/dashboard', [$configController, 'dashboard']);
$app->get('/api/aliases/tg-list', [$aliasesProxyController, 'tgList']);
$app->get('/api/aliases/bridge-list', [$aliasesProxyController, 'bridgeList']);

if ($authController) {
    $app->group('/api/auth', function (RouteCollectorProxy $group) use ($authController) {
        $group->post('/login', [$authController, 'login']);
        $group->get('/login-by-ip', [$authController, 'loginByIp']);
        $group->post('/logout', [$authController, 'logout']);
        $group->get('/me', [$authController, 'me']);
    });
}

if ($selfServiceController) {
    $app->group('/api/self-service', function (RouteCollectorProxy $group) use ($selfServiceController) {
        $group->get('/device', [$selfServiceController, 'getDevice']);
        $group->post('/device/options', [$selfServiceController, 'updateOptions']);
        $group->get('/device/modified', [$selfServiceController, 'getModified']);
        $group->post('/device/select', [$selfServiceController, 'selectDevice']);
    });
}

$app->run();
